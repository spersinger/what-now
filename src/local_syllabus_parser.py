import logging
import numpy as np
import cv2

def deskew_image(img):
    """
    Correct image skew using Hough line detection
    """
    try:
        # Detect edges
        edges = cv2.Canny(img, 50, 150, apertureSize=3)

        # Detect lines
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)

        if lines is None:
            return img

        # Calculate angles
        angles = []
        for rho, theta in lines[:, 0]:
            angle = theta * 180 / np.pi
            if angle > 45:
                angle = angle - 90
            elif angle < -45:
                angle = angle + 90
            angles.append(angle)

        if not angles:
            return img

        # Use median angle for rotation
        median_angle = np.median(angles)

        # Rotate image
        height, width = img.shape
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(img, rotation_matrix, (width, height),
                                flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return rotated
    except Exception as e:
        logging.warning(f"Deskewing failed: {e}")
        return img

def enhance_preprocessing(img):
    """
    Enhanced preprocessing pipeline for OCR
    """
    try:
        # 1. Noise reduction with median blur
        img = cv2.medianBlur(img, 3)

        # 2. CLAHE for contrast enhancement (existing)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img = clahe.apply(img)

        # 3. Adaptive thresholding for better text separation
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)

        # 4. Morphological operations to clean up text
        kernel = np.ones((2, 2), np.uint8)
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

        return img
    except Exception as e:
        logging.error(f"Preprocessing failed: {e}")
        raise e

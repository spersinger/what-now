from llama_cpp import Llama
import logging
import json
import numpy as np
import time
import cv2
from PIL import Image

from pathlib import Path
# Get the path to the project root (one level up from src)
project_root = Path(__file__).resolve().parent.parent
model = project_root / "models" / "qwen2.5-coder-1.5b-instruct-q4_0.gguf"

from concurrent.futures import ThreadPoolExecutor, as_completed

class LocalSyllabusParser:
    def __init__(self):
        """
        Initialize with GGUF model file
        model_path: path to .gguf file
        """
        self.llm = Llama(
            model_path = str(model),
            n_ctx=4096,  # Context window
            n_threads=4,  # CPU threads
            n_gpu_layers=0,  # Set to 35 for GPU acceleration
            verbose=False
        )

    def parse(self, ocr_text: str) -> dict:
        prompt = f"""You are a JSON extraction assistant. Parse the following syllabus text and extract course information.

SYLLABUS TEXT:
{ocr_text}

INSTRUCTIONS:
1. Extract the course name/title
2. Find all recurring class meetings (lectures and office hours that repeat weekly)
3. Find single events (exams, assignments)
4. For each event, extract: day, start_time, end_time, room
5. If information is missing, use "null" as the value
6. Output ONLY valid JSON, no explanations
7. Do not skip any class days, office hours, exams, or assignments

OUTPUT FORMAT:
{{
  "course": "course name here",
  "recurring_events": [
    {{
      "name: "Name of event here"
      "day": "Day here",
      "start_time": "Start time here",
      "end_time": "End time here",
      "room": "Room and room number here"
    }}
    ...
  ],
  "exams": [
    {{
      "name": "Name of event here"
      "day": "Day here",
      "start_time": "Start time here",
      "end_time": "End time here",
      "room": "Room and room number here"
    }}
    ...
  ],
  "assignments": [
    {{
      "name": "Name of assignment here"
      "due_day": "Due day here",
      "due_time": "Due day here",
    }}
    ...
  ]
}}

JSON:"""

        response = self.llm.create_chat_completion(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.1,
            max_tokens=2000,
            response_format={"type": "json_object"}  # Forces JSON
        )

        content = response['choices'][0]['message']['content']
        try:
            parsed_data = json.loads(content)
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return {"error": "Failed to parse JSON"}

# TODO: Move these into a class

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

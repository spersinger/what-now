# from local_syllabus_parser import *

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera

import time
import cv2

from kivy.clock import Clock


# Main class, extending from whatnow.kv CameraClick class
class DocumentScanner(BoxLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Text scanned from OCR
        self.scanned_text: str


    def on_kv_post(self, base_widget):
        # wait until UI is fully built
        Clock.schedule_once(self.create_camera, 0.5)

    def create_camera(self, dt):
        self.camera = Camera(resolution=(640, 480), play=False)
        self.ids.camera_container.add_widget(self.camera)

    def capture(self):
            ################################
            ## TODO : This will go to CommandInterpreter
            #################################


            # Disable buttons while processing takes place to disallow misinputs
            self.ids.scan_button.disabled = True
            self.ids.upload_button.disabled = True

            # Do OCR, possibly move this to another function at some point
            timestr = time.strftime("%Y%m%d_%H%M%S")

            camera = self.camera

            camera.export_to_png("IMG_{}.png".format(timestr))

            # Change this to actual scan at some point, it will work the same
            original_img = cv2.imread("IMG_{}.png".format(timestr), cv2.IMREAD_GRAYSCALE)
            # deskewed_img = deskew_image(original_img)
            # processed_img = enhance_preprocessing(deskewed_img)
            # Save for dev purposes
            cv2.imwrite("pngs/ocr.png", original_img)

            # Scan text using pytesseract
            # try:
            #     self.scanned_text = pytesseract.image_to_string(
            #         original_img,
            #         config="--oem 1 --psm 12"
            #     )
            # except:
            #     print('failed: probably on android')
            #     self.scanned_text = "ERROR: pytesseract failed"
            # PROBLEM: even in try/except, can't have it on android
            self.scanned_text = "PLACEHOLDER (pytesseract currently unavailable)"

            # Disable camera while processing
            self.camera.play = False
            self.camera.opacity = 0

            # Build content for the verification popup, move this to a seperate function
            # self.build_verify_popup_ui()
            # self.verify_text_popup.open()
            
            self.camera.play = True
            self.camera.opacity = 100
            self.ids.scan_button.disabled = False
            self.ids.upload_button.disabled = False
            
            
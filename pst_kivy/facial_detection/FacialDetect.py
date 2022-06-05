import cv2
import numpy as np


class FacialDetect:
    """This class is available to do facial recognition on the image"""

    def __init__(self):
        self.width = 600
        self.height = 300
        self.error_marge = 150
        self.facial_classifier = "./facial_detection/Ressources/Classifiers/haarcascade_frontalface_alt2.xml"
        self.profile_classifier = "./facial_detection/Ressources/Classifiers/haarcascade_profileface.xml"
        self.face_cascade = None
        self.profile_cascade = None
        self.fb_range = [6000, 6200]
        self.pid = [0.4, 0.4, 0]
        self.pError = 0

    @staticmethod
    def capture_video(num):
        """Allow u to choise which camera, u want to use"""
        return cv2.VideoCapture(num)

    def resize_image(self, image):
        dimension = (self.width, self.height)
        return cv2.resize(image, dimension, interpolation=cv2.INTER_AREA)

    @staticmethod
    def adjust_image(image, capture):
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        dimension = (width, height)
        return cv2.resize(image, dimension, interpolation=cv2.INTER_AREA)

    def init_cascade_file(self):
        try:
            with open(self.facial_classifier):
                pass
            with open(self.profile_classifier):
                pass
        except IOError:
            print("fichier %s inexistant")
            exit(-1)
        self.face_cascade = cv2.CascadeClassifier(self.facial_classifier)
        self.profile_cascade = cv2.CascadeClassifier(self.profile_classifier)

    # claire
    def track(self, info):
        area = info[1]
        x, y = info[0]
        fb = 0
        error = x - (self.width // 2)
        speed = (self.pid[0] * error) + (self.pid[1] * (error - self.pError))
        speed = int(np.clip(speed, - 100, 100))

        if (area > self.fb_range[0]) and (area < self.fb_range[1]):
            fb = 0
        elif area > self.fb_range[1]:
            fb = -20
        elif area < self.fb_range[0] and area != 0:
            fb = 20
        if x == 0:
            speed = 0
            error = 0

        return error, (0, fb, 0, 0)

    # claire
    def process(self, image):
        # debut de la gestion de la reconnaissance
        tab_face = []
        my_face_list_c = []
        my_face_list_area = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        result = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=8, minSize=(5, 5))
        for x, y, w, h in result:
            tab_face.append([x, y, w, h])
        result = self.profile_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=8)
        for x, y, w, h in result:
            tab_face.append([x, y, w, h])
        result = self.profile_cascade.detectMultiScale(cv2.flip(gray, 1), scaleFactor=1.2, minNeighbors=8)
        for x, y, w, h in result:
            tab_face.append([self.width - x, y, self.width - w, h])
        index = 0
        for x, y, w, h in tab_face:
            if not index \
                    or (x - tab_face[index - 1][0] > self.error_marge or y - tab_face[index - 1][1] > self.error_marge):
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cx = x + (w // 2)
                cy = y + (h // 2)
                area = w * h
                cv2.circle(image, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
                my_face_list_c.append([cx, cy])
                my_face_list_area.append(area)
            index += 1

        if len(my_face_list_area) != 0:
            i = my_face_list_area.index(max(my_face_list_area))
            return image, [my_face_list_c[i], my_face_list_area[i]]

        else:
            return image, [[0, 0], 0]

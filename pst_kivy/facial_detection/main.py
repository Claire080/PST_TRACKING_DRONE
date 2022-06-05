from facial_detection.FacialDetect import FacialDetect
import cv2


def main():
    # initialise notre objet facial detect
    fd: FacialDetect = FacialDetect()

    # on connecte notre camera
    cap = FacialDetect.capture_video(0)

    # init cascade which u use
    fd.init_cascade_file()

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image = FacialDetect.adjust_image(image, capture=cap)
        image_processed = fd.process(image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        cv2.imshow('Opencv with poo', image_processed)

    # libère l'espace utilisé
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

import cv2

CAT_CASCADE = "haarcascade_frontalcatface.xml"
CAT_CASCADE_EXTENDED = "haarcascade_frontalcatface_extended.xml"
HUMAN_CASCADE = "haarcascade_frontalface_default.xml"


def main():
    cat_detector = cv2.CascadeClassifier(CAT_CASCADE_EXTENDED)
    human_detector = cv2.CascadeClassifier(HUMAN_CASCADE)
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        human_parameters = {"scaleFactor": 1.3, "minNeighbors": 10, "minSize": (75, 75)}
        cat_parameters = {"scaleFactor": 1.15, "minNeighbors": 1, "minSize": (75, 75)}
        human_rects = human_detector.detectMultiScale(frame, **human_parameters)
        cat_rects = cat_detector.detectMultiScale(frame, **cat_parameters)
        print(
            f"\rFound {len(human_rects)} human(s) and {len(cat_rects)} cat(s)", end=""
        )


if __name__ == "__main__":
    main()

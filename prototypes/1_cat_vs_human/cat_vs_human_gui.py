import cv2

CAT_CASCADE = "haarcascade_frontalcatface.xml"
CAT_CASCADE_EXTENDED = "haarcascade_frontalcatface_extended.xml"
HUMAN_CASCADE = "haarcascade_frontalface_default.xml"

RED = (0, 0, 255)
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)


def draw_labeled_rectangles(frame, rects, label, color):
    for (i, (x, y, w, h)) in enumerate(rects):
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(
            frame,
            f"{label} #{i + 1}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
        )


def main():
    cat_detector = cv2.CascadeClassifier(CAT_CASCADE_EXTENDED)
    human_detector = cv2.CascadeClassifier(HUMAN_CASCADE)
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        human_parameters = {"scaleFactor": 1.3, "minNeighbors": 10, "minSize": (75, 75)}
        cat_parameters = {"scaleFactor": 1.15, "minNeighbors": 1, "minSize": (75, 75)}
        human_rects = human_detector.detectMultiScale(frame, **human_parameters)
        cat_rects = cat_detector.detectMultiScale(frame, **cat_parameters)

        draw_labeled_rectangles(frame, human_rects, "Human", RED)
        draw_labeled_rectangles(frame, cat_rects, "Cat", GREEN)
        cv2.imshow("Human vs. Cat", frame)

        # press q or Esc to quit
        if (cv2.waitKey(1) & 0xFF == ord("q")) or (cv2.waitKey(1) == 27):
            cap.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

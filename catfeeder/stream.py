import time
import datetime
from pathlib import Path

import cv2
import numpy as np
from loguru import logger


def start_stream():  # TODO check return value
    return cv2.VideoCapture(0)


def repair_stream(video_stream):
    logger.warning("Failed to capture image. Restarting video feed...")
    video_stream.release()
    video_stream = cv2.VideoCapture(0)
    time.sleep(1)
    return video_stream


def capture_frame(video_stream, retry=True) -> np.ndarray:
    ret, frame = video_stream.read()
    # validate capture / stream
    if not ret:
        if retry:
            video_stream = repair_stream(video_stream)
            ret, frame = capture_frame(video_stream, retry=False)
        else:
            raise Exception("Unable to capture video stream frame")
    return frame


def save_frame(frame: np.ndarray):
    file_name = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
    file_path = Path(f"/home/pi/Pictures/{file_name}")
    cv2.imwrite(str(file_path), frame)
    return file_path

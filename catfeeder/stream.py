import time

import cv2
from loguru import logger


def start_stream():
    return cv2.VideoCapture(0)


def repair_stream(video_stream):
    logger.warning("Failed to capture image. Restarting video feed...")
    video_stream.release()
    video_stream = cv2.VideoCapture(0)
    time.sleep(1)
    return video_stream


def capture_frame(video_stream):
    ret, frame = video_stream.read()
    # validate capture / stream
    if not ret:
        video_stream = repair_stream(video_stream)
        ret, frame = capture_frame(video_stream)
    return frame

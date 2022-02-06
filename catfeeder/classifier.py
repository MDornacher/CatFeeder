from pathlib import Path

import cv2
import numpy as np
import tflite_runtime.interpreter as tflite


MODEL_PATH = Path(__file__).parent.resolve() / "resources" / "model.tflite"
LABELS_PATH = Path(__file__).parent.resolve() / "resources" / "labels.txt"

TEST_IMAGE = Path(__file__).parent.resolve() / "resources" / "nadir.jpg"


def load_labels():
    with open(LABELS_PATH, "r") as file_ref:
        return file_ref.read().splitlines()


def initiate_model():
    interpreter = tflite.Interpreter(
        model_path=str(MODEL_PATH),
    )
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    return interpreter, input_details, output_details


def evaluate_image(image, interpreter, input_details, output_details):
    height = input_details[0]["shape"][1]
    width = input_details[0]["shape"][2]

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height))

    input_data = np.expand_dims(image_resized, axis=0)
    interpreter.set_tensor(input_details[0]["index"], input_data)
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]["index"])
    results = np.squeeze(output_data)

    top_match, *_ = results.argsort()[::-1]
    labels = load_labels()
    return labels[top_match], float(results[top_match] / 255.0)

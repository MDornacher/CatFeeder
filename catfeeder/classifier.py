from pathlib import Path

import cv2
import numpy as np
import tflite_runtime.interpreter as tflite


MODEL_PATH = Path(__file__).parent.resolve() / "resources" / "model.tflite"
LABELS_PATH = Path(__file__).parent.resolve() / "resources" / "labels.txt"


class Classifier:
    def __init__(self):
        self.labels = None
        self.load_labels()

        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.initiate_model()

        self.image_height = self.input_details[0]["shape"][1]
        self.image_width = self.input_details[0]["shape"][2]

    def load_labels(self):
        with open(LABELS_PATH, "r") as file_ref:
            self.labels = file_ref.read().splitlines()

    def initiate_model(self):
        self.interpreter = tflite.Interpreter(
            model_path=str(MODEL_PATH),
        )
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def evaluate(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image_rgb, (self.image_height, self.image_width))

        input_data = np.expand_dims(image_resized, axis=0)
        self.interpreter.set_tensor(self.input_details[0]["index"], input_data)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]["index"])
        results = np.squeeze(output_data)

        top_match, *_ = results.argsort()[::-1]
        return self.labels[top_match], float(results[top_match] / 255.0)

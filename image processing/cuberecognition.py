from tflite_runtime.interpreter import Interpreter
from PIL import Image
import numpy as np
import cv2


def load_labels(path):  # Read the labels from the text file as a Python list.
    with open(path, 'r') as f:
        return [line.strip() for i, line in enumerate(f.readlines())]


def set_input_tensor(interpreter, img):
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = img


def classify_image(interpreter, img, top_k=1):
    set_input_tensor(interpreter, img)

    interpreter.invoke()
    output_details = interpreter.get_output_details()[0]
    output = np.squeeze(interpreter.get_tensor(output_details['index']))

    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

    ordered = np.argpartition(-output, 1)
    return [(i, output[i]) for i in ordered[:top_k]][0]




model_path = "model.tflite"
label_path = "labels.txt"

interpreter = Interpreter(model_path)
print("Model Loaded Successfully.")

interpreter.allocate_tensors()
_, height, width, _ = interpreter.get_input_details()[0]['shape']
print("Image Shape (", width, ",", height, ")")
cap = cv2.VideoCapture(0)
while True:
    _, cv2_im = cap.read()
    cv2_im = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
    image =cv2.resize(cv2_im,(width, height))
    cv2.imshow("image", image)
    cv2.waitKey(1)
    label_id, prob = classify_image(interpreter, image)
    labels = load_labels(label_path)
    classification_label = labels[label_id]
    print("Image Label is :", classification_label, ", with Accuracy :", np.round(prob * 100, 2), "%.")
cap.release()
cv2.destroyAllWindows()

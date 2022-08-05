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
arr = np.zeros((6,6))
interpreter.allocate_tensors()
_, height, width, _ = interpreter.get_input_details()[0]['shape']
cap = cv2.VideoCapture(0)
ret ,img =cap.read()
for i in range(0, 6):
    for j in range(0, 6):
        cropped_image = img[68 + (65 * i):136 + (65 * i), 155 + (j * 65):219 + (j * 65)]
        #cv2.imshow("cropped_image", cropped_image)
        raw = cv2.resize(cropped_image, (height, width))
        image = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)
        label_id, prob = classify_image(interpreter, image)
        labels = load_labels(label_path)
        classification_label = labels[label_id]
        # blue medicine cube
        if(label_id ==0):
            arr[i][j] =1
        # hazardous medicine cube
        elif(label_id ==1):
            arr[i][j] = 3
        # white medicine cube
        elif(label_id ==2):
            arr[i][j] = 2
        # gurney
        elif(label_id ==3):
            arr[i][j] = 4
        # blank space
        elif(label_id ==4):
            arr[i][j] = 0
            
        
        print("Image Label is :", classification_label, ", with Accuracy :", np.round(prob * 100, 2), "%.")
cv2.imshow('frame', img)
print(arr) 
cv2.waitKey(0)
cap.release()
cv2.destroyAllWindows()

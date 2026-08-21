# -*- coding: utf-8 -*-
import cv2
import numpy as np
from tensorflow.keras.models import load_model

model = load_model('pothole_model.h5')
img_path = "My Dataset/train/Pothole/p 320.jpg" # replace with your test image
img = cv2.imread(img_path, 0)  # Read as grayscale
img = cv2.resize(img, (224, 224))  # VGG19 input size
# Convert grayscale to RGB
img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
img = img.reshape(1, 224, 224, 3).astype('float32') / 255.

prediction = model.predict(img)
label = np.argmax(prediction)

print("Prediction:", "Pothole" if label == 1 else "Plain Road")


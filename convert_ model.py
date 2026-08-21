# %%
# %%
# -*- coding: utf-8 -*-


import tensorflow as tf

# ✅ Step 1: Load your trained Keras model
model = tf.keras.models.load_model('pothole_model.h5')

# ✅ Step 2: Convert the model to TensorFlow Lite
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# (Optional) Optimization for size & speed — good for mobile
# converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_model = converter.convert()

# ✅ Step 3: Save the converted model to a file
with open("pothole_model.tflite", "wb") as f:
    f.write(tflite_model)

print("✅ Conversion complete! Model saved as pothole_model.tflite")


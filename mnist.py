import base64
from io import BytesIO
from random import randint
from PIL import Image
from tensorflow.examples.tutorials.mnist import input_data
import tensorflow as tf
import numpy as np

def vec_to_png(data, rows, cols):
    image_array = 255 - np.reshape(data,(28,28))*255
    pil_img = Image.fromarray(image_array).convert('L')
    buffer = BytesIO()
    pil_img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def random_image():
    mnist = input_data.read_data_sets(data_dir, one_hot=True)
    i = randint(0, len(mnist.train.images))
    output = {
      'label': list(mnist.test.labels[i]).index(1),
      'image': vec_to_png(mnist.train.images[i], 28, 28)
    }
    return output
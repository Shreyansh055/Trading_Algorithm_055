"""
In this code, we implement a check of the neural network's image class predictions.
"""

import os
import functions
import numpy as np
from PIL import Image

from keras.models import load_model
from keras.utils.image_utils import img_to_array

from my_config.trade_config import Config  # Configuration file for the trading bot


if __name__ == "__main__":

    timeframe_0 = Config.timeframe_0  # the timeframe we trade on == the timeframe the neural network was trained on

    # load the trained neural network
    model = load_model(os.path.join("NN_winner", "cnn_Open.hdf5"))
    # Check its architecture
    model.summary()

    # load an image to test its class prediction
    _path0 = functions.join_paths(["NN", f"training_dataset_{timeframe_0}", "0"])
    images_class_0 = [f for f in os.listdir(_path0) if os.path.isfile(os.path.join(_path0, f))]  # images of class 0
    _path1 = functions.join_paths(["NN", f"training_dataset_{timeframe_0}", "1"])
    images_class_1 = [f for f in os.listdir(_path1) if os.path.isfile(os.path.join(_path1, f))]  # images of class 1

    images_class_0 = images_class_0[:10]  # keep the first 10
    images_class_1 = images_class_1[:10]  # keep the first 10

    # print(images_class_0)

    for _img in images_class_0:
        img = Image.open(os.path.join(_path0, _img))
        # send the image to the neural network
        img_array = img_to_array(img)  # https://www.tensorflow.org/api_docs/python/tf/keras/utils/img_to_array
        # print(img_array.shape)
        img_array = np.expand_dims(img_array, axis=0)
        # print(img_array.shape)
        _predict = model.predict(img_array, verbose=0)
        _class = 0
        if _predict[0][1] >= 0: _class = 1
        print(f"For image: {_path0}\{_img} Predicted: {_predict} => class={_class}")

    for _img in images_class_1:
        img = Image.open(os.path.join(_path1, _img))
        # send the image to the neural network
        img_array = img_to_array(img)  # https://www.tensorflow.org/api_docs/python/tf/keras/utils/img_to_array
        # print(img_array.shape)
        img_array = np.expand_dims(img_array, axis=0)
        # print(img_array.shape)
        _predict = model.predict(img_array, verbose=0)
        _class = 0
        if _predict[0][1] >= 0: _class = 1
        print(f"For image: {_path1}\{_img} Predicted: {_predict} => class={_class}")

"""
In this code, we train a neural network (NN), using `timeframe_0` as input and `timeframe_1` as output. NN models are saved in the folder `NN/_models`.
After training, the best NN model is manually saved in the folder `NN_winner`.

Logs are saved in the following files:
- 3_Training and Validation Accuracy and Loss.jpg - a graph of Training and Validation Accuracy and Loss
- 3_results_of_training_neural_network.txt - training process logs from the screen
During the training process, the model performed best at epoch 27:
Epoch 26/40
449/449 [==============================] - 25s 55ms/step - loss: 0.0402 - accuracy: 0.9871 - val_loss: 0.2765 - val_accuracy: 0.9312
Epoch 27/40
449/449 [==============================] - 25s 55ms/step - loss: 0.0386 - accuracy: 0.9875 - val_loss: 0.1685 - val_accuracy: 0.9563
Epoch 28/40
449/449 [==============================] - 25s 55ms/step - loss: 0.0370 - accuracy: 0.9875 - val_loss: 0.2051 - val_accuracy: 0.9491
We select the 27th epoch and place it in the `NN_winner` folder under the name `cnn_Open.hdf5`.
"""

exit(777)  # prevent code from running, otherwise, it will overwrite the results

import functions
import matplotlib.pyplot as plt
import os
import tensorflow as tf

from tensorflow import keras
from tensorflow import config
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Rescaling
from keras.layers import Activation, Dropout, Flatten, Dense, BatchNormalization
from keras.callbacks import ModelCheckpoint

from my_config.trade_config import Config  # Configuration file for the trading bot

print("Num GPUs Available: ", len(config.list_physical_devices('GPU')))

if __name__ == '__main__':  # Entry point when running this script

    # whether to redirect output from console to a file
    functions.start_redirect_output_from_screen_to_file(False, filename="3_results_of_training_neural_network.txt")

    # ------------------------------------------------------------------------------------------------------------------

    timeframe_0 = Config.timeframe_0  # timeframe for training the neural network - input - for images
    draw_size = Config.draw_size  # size of the side of the square image

    # =================================================================================================================

    cur_run_folder = os.path.abspath(os.getcwd())  # current directory
    data_dir = os.path.join(os.path.join(cur_run_folder, "NN"), f"training_dataset_{timeframe_0}")  # directory with data
    num_classes = 2  # total classes
    epochs = 40  # number of epochs
    batch_size = 10  # batch size
    img_height, img_width = draw_size, draw_size  # image dimensions
    input_shape = (img_height, img_width, 3)  # image shape

    # # First type of model
    # model = Sequential()
    # model.add(Rescaling(1. / 255))
    # model.add(Conv2D(64, (3, 3), input_shape=input_shape))
    # model.add(Activation('relu'))
    # model.add(MaxPooling2D(pool_size=(2, 2)))
    # model.add(BatchNormalization())
    # model.add(Conv2D(32, (3, 3)))
    # model.add(Activation('relu'))
    # model.add(MaxPooling2D(pool_size=(2, 2)))
    # model.add(BatchNormalization())
    # model.add(Flatten())
    # model.add(Dense(128))
    # model.add(Activation('relu'))
    # model.add(Dropout(0.5))
    # model.add(Dense(num_classes))
    # model.add(Activation('sigmoid'))
    # # version with Gradient descent (with momentum) optimizer
    # model.compile(
    #     optimizer=keras.optimizers.SGD(),
    #     loss=keras.losses.SparseCategoricalCrossentropy(),
    #     metrics=['accuracy']
    # )

    # Second type of model
    model = keras.Sequential([
        keras.layers.Rescaling(1. / 255),
        keras.layers.Conv2D(32, 3, activation='relu'),
        keras.layers.MaxPooling2D(),
        keras.layers.BatchNormalization(),
        keras.layers.Conv2D(32, 3, activation='relu'),
        keras.layers.MaxPooling2D(),
        keras.layers.BatchNormalization(),
        keras.layers.Conv2D(32, 3, activation='relu'),
        keras.layers.MaxPooling2D(),
        keras.layers.BatchNormalization(),
        keras.layers.Flatten(),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(num_classes)
    ])
    # version with Adam optimization (a stochastic gradient descent method)
    model.compile(
        optimizer='adam',
        loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy'])

    # model.summary()

    # training dataset
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        # seed=123,
        shuffle=False,
        image_size=(img_height, img_width),
        batch_size=batch_size)

    # validation dataset
    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        # seed=123,
        shuffle=False,
        image_size=(img_height, img_width),
        batch_size=batch_size)

    # # normalization is built directly into the model
    # normalization_layer = tf.keras.layers.Rescaling(1. / 255)
    # train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
    # val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y))

    # for model saving
    callbacks = [ModelCheckpoint(functions.join_paths([cur_run_folder, "NN", "_models", 'cnn_Open{epoch:1d}.hdf5'])),
                 # keras.callbacks.EarlyStopping(monitor='loss', patience=10),
                 ]

    # start training process
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks
    )

    # plots of training and validation accuracy and loss
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs_range = range(epochs)

    plt.figure(figsize=(8, 8))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    plt.savefig("3_Training and Validation Accuracy and Loss.png", dpi=150)
    plt.show()

    # =================================================================================================================

    # stop redirecting output from the console to the file
    functions.stop_redirect_output_from_screen_to_file()

from keras import (layers, models, regularizers)
import keras.backend as kb
from keras.applications import ResNet50
import keras

def _prob_bird(y_true, y_pred):
    return kb.mean(y_true)

def conv_model(input_shape):
    """A basic convolutional model created by the 2018 Summer research project undergrads."""
    model = models.Sequential(name="conv")
    model.add(layers.Input(input_shape))
    model.add(layers.Conv2D(32, (2, 2), activation='relu'))#
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(16, (2, 2), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Flatten())
    model.add(layers.Dropout(0.3))
    model.add(layers.Dense(16, activation='relu'))
    model.add(layers.Dense(16, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))
    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy',
                  metrics=['binary_accuracy', _prob_bird])
    return model

def gru_model(input_shape):
    """A basic GRU-based model created by 2018 Summer undergrad students."""
    model = models.Sequential(name="gru")
    model.add(layers.GRU(64, input_shape=input_shape, return_sequences=True))
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.01)))
    model.add(layers.Dense(1, activation='sigmoid'))
    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy',
                  metrics=['binary_accuracy', _prob_bird])
    return model
    
                
def bulbul(input_shape):
    """The Grill & Schluter model 'bulbul'.
    
    See Grill, Thomas and Schluter, Jan. 'Two Convolutional Neural Networks for Bird 
    Detection in Audio Signals.' (Self published?)

    Winner of 2018 Bird Audio Detection Challence:
    http://machine-listening.eecs.qmul.ac.uk/bird-audio-detection-challenge/
    https://arxiv.org/abs/1807.05812
    """
    model = models.Sequential(name="bulbul")
    model.add(layers.Input(input_shape))
    model.add(layers.Conv2D(32, (2, 2), activation='relu'))
    model.add(layers.LeakyReLU(alpha = 0.01))
    model.add(layers.MaxPooling2D((3, 3)))
    model.add(layers.Conv2D(16, (3,3)))
    model.add(layers.LeakyReLU(alpha = 0.01))
    model.add(layers.MaxPooling2D((3,3)))
    model.add(layers.Conv2D(16, (3,3)))
    model.add(layers.LeakyReLU(alpha = 0.01))
    model.add(layers.MaxPooling2D((3,3)))
    model.add(layers.Conv2D(16, (3,3)))
    model.add(layers.LeakyReLU(alpha = 0.01))
    model.add(layers.Dropout(0.5))
    model.add(layers.Flatten())
    model.add(layers.Dense(256))
    model.add(layers.LeakyReLU(alpha = 0.01))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(32))
    model.add(layers.LeakyReLU(alpha = 0.01))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(1, activation = 'sigmoid'))
    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy',
                  metrics=['binary_accuracy', _prob_bird])
    return model

def transfer(input_shape):
    base_model = ResNet50(include_top=False,
                     weights="imagenet",
                     input_shape=input_shape)
    inputs = keras.Input(shape=input_shape)
    #x = base_model(inputs, training=False)
    x = base_model(inputs)
    x = layers.GlobalAveragePooling2D()(x)
    outputs = layers.Dense(1)(x)
    model = keras.Model(inputs, outputs, name="transfer")
    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy',
                  metrics=['binary_accuracy', _prob_bird])
    return model

# MODELS = dict(
#     conv = dict(model = conv_model, filepath = 'data/conv.h5', feature = pepeiao.feature.Spectrogram),
#     bulbul = dict(model = bulbul, filepath = 'data/bulbul.h5', feature = pepeiao.feature.Spectrogram),
#     gru = dict(model = gru_model, filepath = 'data/gru.h5', feature = pepeiao.feature.Spectrogram),
#     transfer = dict(model = transfer, filepath = 'data/transfer.h5', feature = pepeiao.feature.Spectrogram),
#     )
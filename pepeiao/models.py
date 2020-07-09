from keras import (layers, models, regularizers)
import keras.backend as kb
from keras.applications import ResNet50, VGG16
from keras.layers import Dense
from keras import callbacks
import numpy as np

def _prob_bird(y_true, y_pred):
    return kb.mean(y_true)

def feature_extraction(output, dataset, model):
    # takes in data set, returns list of features
    for i in range(len(dataset)):
        x = np.expand_dims(dataset[i], axis=0)
        output.append(model.predict(x))

def generate_features(training_set, validation_set, input_shape):
    (trainImages, trainLabels) = next(training_set)
    (validationImages, validationLabels) = next(validation_set)
    trainFeatures = []
    validationFeatures=[]

    # functional type  API, not sequential
    model = VGG16(weights='imagenet', include_top=False, input_shape=input_shape)
    # feature extraction
    feature_extraction(trainFeatures, trainImages, model)
    feature_extraction(validationFeatures, validationImages, model)
    return trainFeatures, validationFeatures

def conv_model(input_shape):
    """A basic convolutional model created by the 2018 Summer research project undergrads."""
    model = models.Sequential()
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
    model = models.Sequential()
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
    model = models.Sequential()
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
    model.compile(optimizer = 'rmsprop',
                  loss = 'binary_crossentropy',
                  metrics = ['binary_accuracy', _prob_bird])
    return model

def transfer(input_shape):
    # use features as input for a shallow neural network
    top = models.Sequential()
    top.add(layers.GlobalAveragePooling2D(input_shape=(13,1,512)))
    top.add(Dense(100, activation='relu'))
    top.add(Dense(1, activation='softmax'))
    top.summary()
    top.compile(optimizer = 'rmsprop',
                loss = 'binary_crossentropy',
                metrics = ['binary_accuracy', _prob_bird])
    return top

# MODELS = dict(
#     conv = dict(model = conv_model, filepath = 'data/conv.h5', feature = pepeiao.feature.Spectrogram),
#     bulbul = dict(model = bulbul, filepath = 'data/bulbul.h5', feature = pepeiao.feature.Spectrogram),
#     gru = dict(model = gru_model, filepath = 'data/gru.h5', feature = pepeiao.feature.Spectrogram),
#     transfer = dict(model = transfer, filepath = 'data/transfer.h5', feature = pepeiao.feature.Spectrogram),
#     )

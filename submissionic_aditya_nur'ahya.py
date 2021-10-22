# -*- coding: utf-8 -*-
"""SubmissionIC_Aditya Nur'ahya.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZA5PCOWAvaZQ8mCgijmskj-ySlHxIW_W

## Image Classification for Stanford Online Product

### Created by : Aditya Nur'ahya (aditya.nurahya17@gmail.com)
"""

import tensorflow as tf
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing.image import ImageDataGenerator

"""#### Get Dataset from 'ftp://cs.stanford.edu/cs/cvgl/Stanford_Online_Products.zip'

#### For more : http://cvgl.stanford.edu/projects/lifted_struct/
"""

!wget --no-check-certificate \
  ftp://cs.stanford.edu/cs/cvgl/Stanford_Online_Products.zip \
  -O /tmp/Stanford_Online_Products.zip

import os
import zipfile

local_tar = '/tmp/Stanford_Online_Products.zip'
tar_ref = zipfile.ZipFile(local_tar, 'r')
tar_ref.extractall('/tmp/')
tar_ref.close()

os.listdir('/tmp')

os.listdir('/tmp/Stanford_Online_Products')

base_dir = os.path.join('/tmp/Stanford_Online_Products')

os.listdir(base_dir)

train_datagen = ImageDataGenerator(rescale=1./255,
    zoom_range=0.2,
    shear_range=0.2,
    rotation_range=20,
    fill_mode='nearest',
    horizontal_flip=True,
    validation_split=0.2) # set validation 20%

"""#### Generate image for classes ['bicycle_final', 'cabinet_final', 'coffee_maker_final']"""

train_generator = train_datagen.flow_from_directory(
      base_dir,
      target_size=(224, 224),
      batch_size=64,
      classes=['bicycle_final', 'cabinet_final', 'coffee_maker_final'],
      class_mode='categorical',
      subset='training') # set as training data
validation_generator = train_datagen.flow_from_directory(
      base_dir, # same directory as training data
      target_size=(224, 224),
      batch_size=64,
      classes=['bicycle_final', 'cabinet_final', 'coffee_maker_final'],
      class_mode='categorical',
      subset='validation')

"""#### Using Application VGG16 for Image Classification"""

from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.layers import Input
model_train = VGG16(include_top=False, input_tensor=Input(shape=(224, 224, 3)))
model_train.trainable = False
model_train.summary()

model = tf.keras.models.Sequential([
    model_train,  
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(3, activation='softmax')   
])

# #modeling CNN
# model = tf.keras.models.Sequential([
#     tf.keras.layers.InputLayer(input_shape=(224, 224, 3)),
#     # 1st conv block
#     tf.keras.layers.Conv2D(25, (5, 5), activation='relu', strides=(1, 1), padding='same'),
#     tf.keras.layers.MaxPool2D(pool_size=(2, 2), padding='same'),
#     # 2nd conv block
#     tf.keras.layers.Conv2D(50, (5, 5), activation='relu', strides=(2, 2), padding='same'),
#     tf.keras.layers.MaxPool2D(pool_size=(2, 2), padding='same'),
#     tf.keras.layers.BatchNormalization(),
#     # 3rd conv block
#     tf.keras.layers.Conv2D(70, (3, 3), activation='relu', strides=(2, 2), padding='same'),
#     tf.keras.layers.MaxPool2D(pool_size=(2, 2), padding='valid'),
#     tf.keras.layers.BatchNormalization(),
#     # ANN block
#     tf.keras.layers.Flatten(),
#     tf.keras.layers.Dense(units=100, activation='relu'),
#     tf.keras.layers.Dense(units=100, activation='relu',name='feature_generator'),
#     tf.keras.layers.Dropout(0.25),
#     # output layer
#     tf.keras.layers.Dense(units=2, activation='sigmoid')
# ])

model.summary()

model.compile(
    loss = 'categorical_crossentropy',
    optimizer = tf.optimizers.Adam(),
    metrics = ['accuracy']
)

class myCallback(tf.keras.callbacks.Callback):
   def on_epoch_end(self, epoch, logs={}):
      if(logs.get('accuracy') >= 0.92 and logs.get('val_accuracy') >= 0.92):
          print("\nAkurasi telah mencapai > 92%!")
          self.model.stop_training = True
callbacks = myCallback()

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', patience=15, min_lr=0.00001, verbose=2)

"""#### Pre-Trained Model"""

history = model.fit(
    train_generator,
    epochs = 50,
    steps_per_epoch = 25,
    validation_data = validation_generator,
    validation_steps = 5,
    verbose = 1,
    callbacks = [callbacks])

"""#### Plotting Accuracy"""

import matplotlib.pyplot as plt
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(acc))

plt.plot(epochs, acc, 'r', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend(loc=0)
plt.figure()


plt.show()

plt.plot(epochs, loss, 'r', label='Training Loss')
plt.plot(epochs, val_loss, 'b', label='Validation Loss')
plt.title('Training and validation loss')
plt.legend(loc=0)
plt.figure()


plt.show()

"""#### Deployment TFLite"""

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with tf.io.gfile.GFile('image-model.tflite', 'wb') as f:
  f.write(tflite_model)
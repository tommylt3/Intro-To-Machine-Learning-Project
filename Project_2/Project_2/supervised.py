import os
import mss
import subprocess
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing import image

class Button:
    name : str
    pressed : bool

    def __init__(self, name):
        self.name = name
        self.pressed = False

    def press(self):
        self.pressed = True
        return f'PRESS {self.name}'

    def release(self):
        self.pressed = False
        return f'RELEASE {self.name}'

    def toggle(self):
        if self.pressed:
            return self.release()
        else:
            return self.press()

class Controller:
    def __init__(self):
        self.buttons = {
            'A': Button('A'),
            'B': Button('B'),
            'D_UP': Button('D_UP'),
            'D_LEFT': Button('D_LEFT'),
            'D_RIGHT': Button('D_RIGHT'),
            'D_DOWN': Button('D_DOWN')
        }


    def toggle(self, button_name: str):
        button = self.buttons.get(button_name)
        try:
            if isinstance(button, Button):
                return button.toggle()
            else:
                raise Exception('Bad Button')
        except:
            raise Exception('Not In Dictionary')

class WiiController(Controller):
    def __init__(self):
        super().__init__()

        self.buttons.update({
            'HOME': Button('HOME'),
            'MINUS': Button('MINUS'),
            'PLUS': Button('PLUS'),
            'SWIPE': Button('X')
        })

class Pipe:

    def __init__(self):
        self.fifo_path = "/home/tommy/.dolphin-emu/Pipes/"
        self.fifo_stream = None
        if not os.path.exists(self.fifo_path):
            os.mkdir(self.fifo_path)
        self.fifo_pipe = self.fifo_path + 'pipe0'
        try:
            self.fifo_stream = open(self.fifo_pipe, 'w')
        except:
            print("Stream not working")

    def write_to_buffer(self, content):
        self.fifo_stream.write(content + "\n")
        self.fifo_stream.flush()

class Game:

    def __init__(self, classifier):
        self.pipe = Pipe()
        self.controller = WiiController()
        self.classifier = classifier
        #subprocess.Popen(['dolphin-emu', '/home/tommy/DYOP/Python/Intro-To-Machine-Learning-Project/Project_2/Project_2/DolphinFiles/Wii Sports (USA).rvz'])

    def game_loop(self):
        while True:
            with mss.mss() as sct:
                screenshot = sct.grab(sct.monitors[2])
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                guess = self.classifier.predict(img)
                print(f"Label: {guess}")
                if guess != "None":
                    self.pipe.write_to_buffer(self.controller.toggle(guess))
class Classifier:

    def __init__(self, base_path, img_size, batch_size):
        self.base_path = base_path
        self.img_size = img_size
        self.batch_size = batch_size
        self.class_names = []
        self.model = None

    def prepare_data(self, validation_split=0.35):
        datagen = image.ImageDataGenerator(validation_split=validation_split, rescale=1./255)

        self.train_gen = datagen.flow_from_directory(
            self.base_path,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='sparse',
            subset='training',
            shuffle=True
        )

        self.val_gen = datagen.flow_from_directory(
            self.base_path,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='sparse',
            subset='validation',
            shuffle=True
        )

        self.class_names = list(self.train_gen.class_indices.keys())
        self.num_classes = len(self.class_names)

    def build_model(self):
        self.model = models.Sequential()
        self.model.add(layers.Conv2D(16, (3,3), 1, activation='relu', input_shape=(256,256,3)))
        self.model.add(layers.MaxPooling2D())
        self.model.add(layers.Dropout(0.25))
        self.model.add(layers.Conv2D(32, (3,3), 1, activation='relu'))
        self.model.add(layers.MaxPooling2D())
        self.model.add(layers.Dropout(0.5))
        self.model.add(layers.Conv2D(16, (3,3), 1, activation='relu'))
        self.model.add(layers.MaxPooling2D())
        self.model.add(layers.Dense(48, activation='relu'))
        self.model.add(layers.MaxPooling2D())
        self.model.add(layers.Flatten())
        self.model.add(layers.Dense(256, activation='relu'))
        self.model.add(layers.Dense(self.num_classes, activation='softmax'))
        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    def train(self, epochs=5):
        history = self.model.fit(self.train_gen, validation_data=self.val_gen, epochs=epochs)
        return history

    def save_model(self, path='backup.keras'):
        self.model.save(path)

    def load_model(self, path='backup.keras'):
        self.model = tf.keras.models.load_model(path)

    def predict_image(self, img):
        img = img.resize(self.img_size)
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        prediction = self.model.predict(img_array)
        predicted_index = np.argmax(prediction)
        predicted_label = self.class_names[predicted_index]
        return predicted_label

    def predict(self, img):
        return self.predict_image(img)


class TennisClassifier(Classifier):
    def __init__(self):
        super().__init__('Images/Tennis/', (256,256), 32)

class MenuClassifier(Classifier):
    def __init__(self):
        super().__init__('Images/Menu/', (256,256), 32)

class GenericClassifier(Classifier):
    def __init__(self, menu_classifier : MenuClassifier,  tennis_classifier : TennisClassifier):
        super().__init__('Images/Generic/', (256, 256), 32)
        self.menu_classifier = menu_classifier
        self.tennis_classifier = tennis_classifier

    def predict(self, img):
        label = self.predict_image(img)
        if label == 'Tennis':
            print('Tennis')
            return self.tennis_classifier.predict(img)
        if label == 'Menu':
            print('Menu')
            return self.menu_classifier.predict(img)


# Little Bit of Setup
if __name__ == "__main__":

    # Build Classifiers
    tennis_class = TennisClassifier()
    tennis_class.prepare_data()
    menu_class = MenuClassifier()
    menu_class.prepare_data()
    generic_class = GenericClassifier(menu_class, tennis_class)
    generic_class.prepare_data()

    # Using Model
    #tennis_class.load_model('tennis_v2.keras')
    #menu_class.load_model('menu_v2.keras')
    #generic_class.load_model('generic_v1.keras')
    #game_of_tennis = Game(generic_class)
    #game_of_tennis.game_loop()

    # Training
    #print("Starting Tennis")
    #tennis_class.build_model()
    #tennis_class.train()
    #tennis_class.save_model('tennis_v3.keras')
    #print("Starting Menu")
    #menu_class.build_model()
    #menu_class.train()
    #menu_class.save_model('menu_v2.keras')
    #print("Starting Generic")
    generic_class.build_model()
    generic_class.train()
    generic_class.save_model('generic_v1.keras')

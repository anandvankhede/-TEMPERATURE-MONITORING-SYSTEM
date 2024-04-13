# -*- coding: UTF-8 -*-
import time
import serial
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import lcd

KV = '''
Screen:
    BoxLayout:
        orientation: 'vertical'

        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 1
            padding: dp(5)

            MDLabel:
                id: error_label
                text: ""
                font_style: 'Body1'
                theme_text_color: "Error"
                size_hint_y: None
                height: dp(20)
                halign: 'center'
                valign: 'middle'

            MDLabel:
                text: "Temperature"
                font_style: 'Subtitle2'
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                size_hint_y: None
                height: dp(140)
                halign: 'center'
                valign: 'middle'

            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(30)
                spacing: dp(10)
                padding: dp(5)

                BoxLayout:
                    id: left_layout
                    orientation: 'vertical'
                    size_hint_x: None
                    size_hint_y: None
                    height: dp(30)
                    width: dp(60)  # Adjusted width
                    padding: dp(10)
                    pos_hint: {'center_x': 0.5,'center_y': 0.5}  

                    MDLabel:
                        id: value_label_left
                        text: ""
                        font_style: 'Subtitle1'
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint: None, None
                        size: dp(50), dp(35)  # Adjusted size
                        font_size: '12sp'
                        halign: 'center'
                        valign: 'middle'
                        pos_hint: {'center_x': 0.5, 'center_y': 1}

                BoxLayout:  
                    orientation: 'vertical'
                    size_hint_x: None  # Adjusted width
                    size_hint_y: 1

                    width: dp(20)
                    padding: dp(3)
                    spacing: dp(3)
                    MDLabel:
                        text: "200°C"
                        font_style: 'Body1'
                        size_hint_y: None
                        height: dp(35)
                        size_hint: None, None
                        size: dp(20), dp(5)
                        font_size: '7sp'

                    MDProgressBar:
                        id: progress_bar
                        size_hint_y: None
                        height: dp(55)
                        orientation: 'vertical'
                        color: 0, 1, 0, 1
                        pos_hint: {'center_x': 0.5}

                    MDLabel:
                        text: " 0°C"
                        font_style: 'Body1'
                        size_hint_y: None
                        height: dp(35)
                        size_hint: None, None
                        size: dp(25), dp(4)
                        font_size: '7sp'
'''

class ST7789App(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animation = Animation(value=0, duration=1)
        self.ser = None
        self.mylcd = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.screen = Builder.load_string(KV)
        Window.size = (240, 240)

        # Initialize the LCD
        self.mylcd = lcd.ST7789V(3, 2, 18)  # Set the GPIO pins accordingly
        self.mylcd.lcdinit()

        # Start the serial listener after the GUI is built
        Clock.schedule_once(lambda dt: self.start_serial_listener("/dev/ttyACM0", 9600))
        return self.screen

    def start_serial_listener(self, port, baudrate):
        try:
            self.ser = serial.Serial(port, baudrate)
            print(f"Connected to serial port '{port}'")

            # Start the data reading loop
            Clock.schedule_interval(self.read_serial_data, 2)  # Adjust the interval as needed

        except serial.SerialException as e:
            self.show_error_message(f"Serial error: {e}")

    def read_serial_data(self, dt):
        try:
            data = self.ser.readline().decode().strip()
            if data:
                # Split the received data into an array using the comma delimiter
                data_array = data.split(',')
                if len(data_array) >= 7:
                    self.update_label(data_array[6])
                    self.update_progress_bar(float(data_array[6]))

        except Exception as e:
            self.show_error_message(f"Error: {e}")

    def update_label(self, value):
        self.screen.ids.value_label_left.text = f"{value}°C"

    def update_progress_bar(self, value):
        thresholds = [40, 80, 100]
        colors = [(0, 0, 1, 1), (0, 1, 0, 1), (1, 0, 0, 1)]
        progress_value = (value / 200) * 100
        color_index = next((i for i, threshold in enumerate(thresholds) if progress_value <= threshold), len(thresholds) - 1)

        self.animation.stop(self.screen.ids.progress_bar)
        self.animation = Animation(value=progress_value, duration=1)
        self.animation.start(self.screen.ids.progress_bar)

        self.screen.ids.progress_bar.color = colors[color_index]

    def show_error_message(self, message):
        self.screen.ids.error_label.text = message

    def on_stop(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    ST7789App().run()

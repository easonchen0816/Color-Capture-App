import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView

from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.uix.screenmanager import Screen, ScreenManager

# from kivy.clock import Clock
from kivy.graphics.texture import Texture

from kivy.uix.camera import Camera
from kivy.properties import BooleanProperty, NumericProperty, StringProperty

import os
import cv2
import numpy as np
import logging
from PIL import Image
from colorimeter import *
# from android.permissions import request_permissions, Permission

# Index page 
class IndexPage(FloatLayout):
 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


    @staticmethod
    def page_go(*args):
        App.get_running_app().screen_manager.current="Image_page"
        App.get_running_app().screen_manager.transition.direction = 'left'


# Image page
class LoadDialog(FloatLayout):
 
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    cwdir = ObjectProperty(None)
    

Factory.register("LoadDialog",cls=LoadDialog)


class ImagePage(BoxLayout):
    rgb = StringProperty()
    xyz = StringProperty()
    yxy = StringProperty()
    

    def __init__(self,**kwargs):
        super().__init__(**kwargs)


    @staticmethod
    def back_index(*args):
        App.get_running_app().screen_manager.current="Index_page"
        App.get_running_app().screen_manager.transition.direction = 'right'


    def back_video(self,*args):
        App.get_running_app().screen_manager.current="Video_page"
        App.get_running_app().screen_manager.transition.direction = 'left'


    def dismiss_popup(self):
       
        self._popup.dismiss()



    def show_load(self):
      
        content = LoadDialog(load=self._load,cancel=self.dismiss_popup,cwdir=os.getcwd())
       
        self._popup = Popup(title="Load Image",content=content,size_hint=(.9,.9))
    
        self._popup.open()

    def _load(self,path,filename):
        logging.info("path:{},filename:{}".format(path,filename))
        self.dismiss_popup()
        img = Image.open(filename)
        img, rgb1, rgb2, rgb3 = cauculate_rgb(img)
        self.rgb = 'RGB: (%d, %d, %d)'%(rgb1[0], rgb1[1], rgb1[2])
        self.xyz = 'CIExyz: (%.2f, %.2f, %.2f)'%(rgb2[0], rgb2[1], rgb2[2])
        self.yxy = 'CIEYxy: (%.2f, %.2f, %.2f)'%(rgb3[0], rgb3[1], rgb3[2])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        img = cv2.flip(img, 0) 
        img_buff = img.tostring()
        img_texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='rgba')
        img_texture.blit_buffer(img_buff, colorfmt='rgba', bufferfmt='ubyte')
        self.ids.img_det.texture = img_texture


# video page
class CameraWidget(Camera):
    vrgb = StringProperty()
    vxyz = StringProperty()
    vyxy = StringProperty()
    detectFaces = BooleanProperty(False)
    angle = NumericProperty(0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def on_tex(self, *l):
        if self.texture is not None:
            image = np.frombuffer(self.texture.pixels, dtype='uint8')
            image = image.reshape(self.texture.height, self.texture.width, -1)
            Img = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

            Img = Image.fromarray(Img)
            _, rgb1, rgb2, rgb3 = cauculate_rgb(Img)
            self.vrgb = 'RGB: (%d, %d, %d)'%(rgb1[0], rgb1[1], rgb1[2])
            self.vxyz = 'CIExyz: (%.2f, %.2f, %.2f)'%(rgb2[0], rgb2[1], rgb2[2])
            self.vyxy = 'CIEYxy: (%.2f, %.2f, %.2f)'%(rgb3[0], rgb3[1], rgb3[2])
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            image = cv2.resize(image,(640,480))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
            numpy_data = image.tostring()
            self.texture.blit_buffer(numpy_data, bufferfmt="ubyte", colorfmt='rgba')    
        super().on_tex(self.texture)



 

class VideoPage(BoxLayout):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


    @staticmethod
    def back_image(*args):
        App.get_running_app().screen_manager.current="Image_page"
        App.get_running_app().screen_manager.transition.direction = 'right'

    @staticmethod
    def back_index_1(*args):
        App.get_running_app().screen_manager.current="Index_page"
        App.get_running_app().screen_manager.transition.direction = 'left'



class LaneDetectApp(App):
    def build(self):
        self.icon = "./static/icon.ico"
        self.title = "capture color"
        # request_permissions([
        #                         Permission.CAMERA,
        #                         Permission.WRITE_EXTERNAL_STORAGE,
        #                         Permission.READ_EXTERNAL_STORAGE
        #                     ])
        self.load_kv("./index.kv")
        self.load_kv("./image.kv")
        self.load_kv("./video.kv")



        self.screen_manager = ScreenManager()
        pages = {"Index_page":IndexPage(),"Image_page":ImagePage(),"Video_page":VideoPage()} #
        


        for item,page in pages.items():
            self.default_page = page
           
            screen = Screen(name=item)
            screen.add_widget(self.default_page)
           
            self.screen_manager.add_widget(screen)
        return self.screen_manager



if __name__ == "__main__":
    LaneDetectApp().run()
import time
from time import sleep

from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang.builder import Builder
from kivymd.uix.menu import MDDropdownMenu
from facial_detection.FacialDetect import FacialDetect
from djitellopy import tello
import cv2

event_tracking = None
event_manual = None


class Tracking(Screen):
    """Screen use for tracking"""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.image = None
        self.out = None
        self.video = 0
        self.fd: FacialDetect = FacialDetect()  # initialise notre objet facial detect
        global event_tracking
        event_tracking = Clock.schedule_interval(self.tracking, 0.04)
        Clock.unschedule(event_manual)

        self.fd.init_cascade_file()  # init cascade which u use
        print(tello_object.get_battery())

    def tracking(self, *args):
        self.image = tello_object.get_frame_read().frame
        if self.image is None:
            return
        self.image, info = self.fd.process(self.image)
        error, (lr, fb, ud, yv) = self.fd.track(info)
        buffer = bytes(cv2.flip(self.image, 0))
        texture = Texture.create(size=(self.image.shape[1], self.image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.ids.tracking_image.texture = texture
        if self.out is not None:
            self.out.write(self.image)
        tello_object.send_rc_control(lr, fb, ud, yv)

    @staticmethod
    def take_off():
        tello_object.takeoff()
        tello_object.send_rc_control(0, 0, 50, 0)
        sleep(1)

    @staticmethod
    def land():
        tello_object.land()
        time.sleep(1)

    def take_photo(self):
        cv2.imwrite(f'./Images/{time.time()}.jpg', self.image)
        time.sleep(0.3)

    def back(self):
        self.manager.switch_to(SelectMode(), direction='right', duration=1)

    def take_video(self):
        if self.video:
            self.video = 0
            self.out.release()
            self.out = None
            return
        else:
            self.video = 1
        self.out = cv2.VideoWriter(f'./Images/{time.time()}.avi',
                                   cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (960, 720))


class Manual(Screen):
    """Screen use for manage drone manualy and display the facial tracking image"""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.video = 0
        self.lr = 0
        self.fb = 0
        self.ud = 0
        self.yv = 0
        self.speed = 50
        self.menu = None
        self.image = None
        self.out = None
        global event_manual
        event_manual = Clock.schedule_interval(self.do_tracking, 0.04)
        Clock.unschedule(event_tracking)
        self.menu_items = [
            {
                "text": f"File",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"File": self.menu_callback(x),
            },
            {
                "text": f"Preferences",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"Preferences": self.menu_callback(x),
            },
        ]
        self.menu = MDDropdownMenu(
            items=self.menu_items,
            width_mult=2,
            position="bottom",
        )

    def dropdown(self, instance):
        self.menu.caller = instance
        self.menu.elevation = 10
        self.menu.open()

    @staticmethod
    def menu_callback(text_item):
        print(text_item)

    def open_menu(self):
        pass

    def do_tracking(self, *args):
        self.image = tello_object.get_frame_read().frame
        if self.image is None:
            return
        buffer = bytes(cv2.flip(self.image, 0))
        texture = Texture.create(size=(self.image.shape[1], self.image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.ids.track_manual_image.texture = texture

        if self.ids.btn_left.state == "down":
            self.lr = -self.speed
        if self.ids.btn_right.state == "down":
            self.lr = self.speed
        if self.ids.btn_up.state == "down":
            self.ud = self.speed
        if self.ids.btn_down.state == "down":
            self.ud = -self.speed
        if self.ids.btn_forward.state == "down":
            self.fb = self.speed
        if self.ids.btn_backward.state == "down":
            self.fb = -self.speed

        if self.out is not None:
            self.out.write(self.image)

        # stabiliser les drones
        tello_object.send_rc_control(self.lr, self.fb, self.ud, self.yv)
        self.lr, self.fb, self.ud, self.yv = 0, 0, 0, 0

    @staticmethod
    def take_off():
        tello_object.takeoff()

    @staticmethod
    def land():
        tello_object.land()
        time.sleep(1)

    def take_photo(self):
        cv2.imwrite(f'./Images/{time.time()}.jpg', self.image)
        time.sleep(0.3)

    def back(self):
        self.manager.switch_to(SelectMode(), direction='right', duration=1)

    def switch(self):
        self.manager.switch_to(Tracking(), direction='right', duration=1)

    def take_video(self):
        if self.video:
            self.video = 0
            self.out.release()
            self.out = None
            return
        else:
            self.video = 1
        self.out = cv2.VideoWriter(f'./Images/{time.time()}.avi',
                                   cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (960, 720))


class SelectMode(Screen):
    def switch_to_manual(self):
        try:
            # affichage d'image apres une certaine period
            self.manager.switch_to(Manual(), direction='right', duration=1)

        except Exception as e:
            print(e)

    def switch_to_tracking(self):
        try:
            self.manager.switch_to(Tracking(), direction='right', duration=1)
        except Exception as e:
            print(e)


class FrontFace(Screen):
    def on_enter(self):
        """Change la fenêtre principal après 7 secondes d'attente"""
        Clock.schedule_once(self.change_screen, 7)

    def change_screen(self, time):
        """Une fois l'évènement on_enter survenu, cette fonction permettra de
        switcher de la fenetre Frontface vers la fenètre WifiPage"""
        try:
            self.manager.switch_to(WifiPage(), direction='right', duration=1)
        except Exception as e:
            print(e)


class WifiPage(Screen):
    pass


class FrontApp(ScreenManager):
    pass


class MyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global tello_object
        tello_object = tello.Tello()
        tello_object.connect()
        # self.tello_object.streamoff()
        tello_object.streamon()
        self.path_to_kv_file = "manual.kv"

    def build(self):
        return Builder.load_file("frontapp.kv")


if __name__ == "__main__":
    app = MyApp().run()

import os
from kaki.app import App
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.factory import Factory


class MDLive(App, MDApp):
    """Utiliser pour effectuer un auto-reload"""

    CLASSES = {
        "Manual": "app",
    }

    AUTORELOADER_PATHS = [
        (".", {"recursive": True})
    ]

    KV_FILES = [
        "manual.kv",
    ]

    IDLE_DETECTION = True

    IDLE_TIMEOUT = 2

    def build_app(self, *args):
        print("Inside built to Autoreload")
        Window.size = [640, 320]
        self.path_to_kv_file = "manual.kv"
        return Factory.Manual()


MDLive().run()

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, FadeTransition, Screen
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, NumericProperty
from threading import Thread
from os.path import join
from utils.classes.database import init_db
import time

Window.size = (320, 700)  # For desktop preview

class FrontScreen(Screen):
    pass

class lawofattraction(Screen):
    pass

class MainApp(MDApp):
    sm = None
    bot_name = ObjectProperty(None)
    text_input = ObjectProperty(None)
    dialog = None
    angle = NumericProperty(0)

    def build(self):
        self.title = "Motivation App"
        self.theme_cls.theme_style = "Dark"

        self.sm = ScreenManager(transition=FadeTransition(duration=0.3))

        # Load front screen synchronously to show instantly
        Builder.load_file("utils/pages/front.kv")
        front_screen = FrontScreen(name="front")
        self.sm.add_widget(front_screen)
        self.sm.current = "front"

        # Add screen manager to layout
        root_layout = FloatLayout()
        root_layout.add_widget(self.sm)

        # Start background loading
        Clock.schedule_once(lambda dt: self.start_background_tasks(front_screen), 0)

        return root_layout

    def start_background_tasks(self, front_screen):
        # Start spinner
        front_screen.ids.spinner.active = True

        # Start threading for background task
        Thread(target=self.background_loader, args=(front_screen,), daemon=True).start()

    def background_loader(self, front_screen):
        # Simulate or call DB init
        init_db()

        # Simulate delay (you can remove this in production)
        time.sleep(1)

        # Prepare UI from main thread
        Clock.schedule_once(lambda dt: self.prepare_home_screen(front_screen), 0)

    @mainthread
    def prepare_home_screen(self, front_screen):
        self.load_screen("home", "home.kv")

        # Stop spinner and navigate
        front_screen.ids.spinner.active = False
        self.sm.current = "home"

    def change_screen(self, screen_name, kv_filename=None, folder="utils/pages"):
        if not self.sm.has_screen(screen_name):
            self.load_screen(screen_name, kv_filename or f"{screen_name}.kv", folder)
        self.sm.current = screen_name

    def load_screen(self, screen_name, kv_filename, folder="utils/pages"):
        screen_class = self.get_screen_class(screen_name)
        if not screen_class:
            print(f"[ERROR] No screen class found for: {screen_name}")
            return

        Builder.load_file(join(folder, kv_filename))
        screen = screen_class(name=screen_name)
        self.sm.add_widget(screen)

    def get_screen_class(self, screen_name):
        from utils.classes.home import HomeScreen
        from utils.classes.CBT import cbt
        from utils.classes.pdf_chat import chat
        from utils.classes.Loaform import loaform
        from utils.classes.journal import journal_affirmation
        from utils.classes.visualization_tech import visualization_tech
        from utils.classes.visualization_instruction import visualization_instruction
        from utils.classes.voice_affirmation import voice_affirmation
        from utils.classes.thought_refarming_gemini import though_chat
        from utils.classes.thought import though
        from utils.classes.insta_reels import reels
        from utils.classes.imagery import imagery
        from utils.classes.imagery_chat import imgery_chat
        from utils.classes.riddles import reddles
        from utils.classes.quotes import quotes
        from utils.classes.das_test import TestScreen
        from utils.classes.Afterlove import Afterlove
        from utils.classes.anxiety import anxiety

        screen_map = {
            "home": HomeScreen,
            "chat": chat,
            "cbt": cbt,
            "reels": reels,
            "lawofattraction": lawofattraction,
            "loaform": loaform,
            "journal_affirmation": journal_affirmation,
            "visualization_tech": visualization_tech,
            "visualization_instruction": visualization_instruction,
            "voice_affirmation": voice_affirmation,
            "though": though,
            "imagery": imagery,
            "imagery_chat": imgery_chat,
            "thought_chat": though_chat,
            "riddles": reddles,
            "quotes": quotes,
            "das_test": TestScreen,
            "Afterlove": Afterlove,
            "anxiety": anxiety,
        }

        return screen_map.get(screen_name, None)

if __name__ == "__main__":
    MainApp().run()

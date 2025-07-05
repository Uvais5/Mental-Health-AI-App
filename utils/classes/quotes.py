import os
  # Force Kivy to use SDL2 audio backend to avoid ffpyplayer issues
from datetime import datetime
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ListProperty
from kivy.clock import Clock, mainthread
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.core.audio import SoundLoader
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
from plyer.utils import platform
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList, OneLineIconListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from utils.classes.database import get_database_path
from kivy.metrics import dp
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.uix.screenmanager import ScreenManager,Screen
import requests
import threading
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.spinner import MDSpinner
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.label import MDLabel
from kivy.uix.relativelayout import RelativeLayout
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.uix.image import AsyncImage



class Waveform(Widget):
    waveform = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(waveform=self.update_waveform)
        

    def update_waveform(self, instance, value):
        self.canvas.clear()
        with self.canvas:
            Color(0, 0, 0, 0.5)
            if len(value) > 1:
                width = self.width
                height = self.height
                step = max(1, len(value) // int(width))
                points = []
                for i in range(0, len(value), step):
                    x = i / len(value) * width
                    y = (value[i] + 1) / 2 * height
                    points.extend([x, y])
                Line(points=points, width=1.5)
class ClickableCard(MDCard, ButtonBehavior):
    pass



class quotes(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_more = False
        self.loading_fullscreen_more = False
        self.fs = 44100  # Sample rate
        self.recording = []
        self.snackbar = None
        self.stream = None
        self.mode="normal"
        self.threads = []
        self.stop_flags = []
        self.record_save = get_database_path()[2]
        print(self.record_save)
    is_recording = BooleanProperty(False)
    current_playing_audio = None
    sound = None
    sound_path = None


########################################quotes screen function #####################################################

    def quotes_start(self,mode):
        self.on_leave()
        if mode == "loves":
            self.mode = "love"
        elif mode=="relationship":
            self.mode = "relationship"
        elif mode=="facts":
            self.mode = "facts"
            self.ids.title.text="Facts"
            self.ids.front_img.source="https://i.pinimg.com/736x/7b/fa/5a/7bfa5a5c3832f1105fef8e2481fc7ca9.jpg"
            self.ids.loading_txt.text="Facts loading... because reality is cooler than fiction."
        elif mode=="normal":
            self.mode="normal"
            self.ids.title.text="Quotes"
            self.ids.front_img.source="https://i.pinimg.com/736x/23/07/00/230700393a2c132d3a7531ae84319fff.jpg"
            self.ids.loading_txt.text="Loading a thought to change your day..."
        elif mode=="love":
            self.mode="love"
            self.ids.title.text="Love Quotes"
            self.ids.front_img.source="https://i.pinimg.com/736x/9a/cf/43/9acf43e7ea915ac4776190f1258f5643.jpg"
            #self.ids.normal_id.md_bg_color = get_color_from_hex("#336699")
            #self.ids.loading_txt.color = get_color_from_hex("#336699")
            self.ids.loading_txt.text="Patience is a virtue, especially when love is loading."
        elif mode=="life":
            self.mode="life"
            self.ids.title.text="Life Quotes "
            self.ids.front_img.source="https://i.pinimg.com/736x/3f/9b/bd/3f9bbd6036f165101e0c12ab77c90632.jpg"
            self.ids.loading_txt.text="Please wait, life is currently under construction (as always)"
        elif mode=="success":
            self.mode="success"
            self.ids.title.text="Quotes about success"
            self.ids.front_img.source="https://i.pinimg.com/736x/87/5a/18/875a18a13f5f759ec929bde5406de70c.jpg"
            self.ids.loading_txt.text="Something great is on its way... Almost there!"
        elif mode=="motivation":
            self.mode="motivation"
            self.ids.title.text="Motivational Quotes "
            self.ids.front_img.source="https://i.pinimg.com/736x/c8/92/61/c892610470b140ed9ec124195a124162.jpg"
            self.ids.loading_txt.text="Turn your 'impossible' into 'I'm possible"
        elif mode=="wisdom":
            self.mode="wisdom"
            self.ids.title.text="Wisdom Quotes "
            self.ids.front_img.source="https://i.pinimg.com/736x/12/f7/3a/12f73a461efb80f3979669fa3f5f9fac.jpg"
            self.ids.loading_txt.text="The only true wisdom is knowing you know nothing"
        elif mode=="inspirational":
            self.mode="inspirational"
            self.ids.title.text="Inspirational Quotes "
            self.ids.front_img.source="https://i.pinimg.com/736x/19/d0/2c/19d02c011affa8f8724fa3ed3332b83e.jpg"
            self.ids.loading_txt.text="The human spirit is stronger than anything that can happen to it"
        elif mode=="friend":
            self.mode="friend"
            self.ids.title.text="Friendship Quotes "
            self.ids.front_img.source="https://i.pinimg.com/736x/af/fe/c2/affec2852a71cb46777d0f719d670a08.jpg"
            self.ids.loading_txt.text="So many memories, so little blackmail material... yet."
        elif mode=="happy":
            self.mode="happy"
            self.ids.title.text="Happiness Quotes "
            self.ids.front_img.source="https://i.pinimg.com/736x/db/43/f2/db43f2197ec3fd83414af2ec798b696c.jpg"
            self.ids.loading_txt.text="Happiness is not a destination, it's a way of life."
        elif mode=="advice":
            self.mode="advice"
            print(self.mode)
            self.ids.title.text="Advice"
            self.ids.front_img.source="https://i.pinimg.com/736x/fd/d9/b6/fdd9b6d85c443a21e24abfd1ccdb5300.jpg"
            self.ids.loading_txt.text="Good advice is worth the (short) wait."
        
        Clock.schedule_once(self.start_initial_loading, 0.1)

        Clock.schedule_once(self.bind_scrolls, 0.2)


    def bind_scrolls(self, dt):
        self.ids.scroll_view.bind(scroll_y=self.on_scroll_main)
        self.ids.full_scroll.bind(scroll_y=self.on_scroll_full)

    def on_scroll_main(self, instance, value):
        if value <= 0.1 and not self.loading_more:
            self.loading_more = True
            self.ids.loading_spinner.active = True
            threading.Thread(target=self.fetch_main_content).start()

    def on_scroll_full(self, instance, value):
        if value <= 0.1 and not self.loading_fullscreen_more:
            self.loading_fullscreen_more = True
            self.ids.loading_spinner1.active = True
            stop_flag = threading.Event()
            thread = threading.Thread(target=self.fetch_fullscreen_content)
            self.threads.append(thread)
            self.stop_flags.append(stop_flag)
            thread.start()

    def start_initial_loading(self, *args):
        self.ids.loading_spinner.active = True
        
        
        stop_flag = threading.Event()
        thread = threading.Thread(target=self.fetch_main_content)
        self.threads.append(thread)
        self.stop_flags.append(stop_flag)
        thread.start()

    def fetch_main_content(self):
        new_cards = self.get_cards(8)
        Clock.schedule_once(lambda dt: self.add_to_main_grid(new_cards), 0)

    def fetch_fullscreen_content(self):
        new_cards = self.get_cards(4)
        #self.ids.loading_spinner.active = True
        Clock.schedule_once(lambda dt: self.add_to_fullscreen_grid(new_cards), 0)

    def get_cards(self, count=6):
        cards = []
        for _ in range(count):
            image_url = self.get_random_image_url()
            quote_text = self.get_random_quote()
            cards.append((image_url, quote_text))
        return cards

    def add_to_main_grid(self, cards):
        grid = self.ids.grid
        for image_url, quote_text in cards:
            card = ClickableCard(
                orientation="vertical",
                size_hint_y=None,
                height="150dp",
                radius=[20],
                elevation=8,
                ripple_behavior=True,
                md_bg_color=(0, 0, 0, 0)
            )

            layout = RelativeLayout()
            img = AsyncImage(source=image_url, size_hint=(1, 1), allow_stretch=True, keep_ratio=False)

            overlay = MDBoxLayout(
                orientation='vertical',
                size_hint=(1, None),
                height="150dp",
                pos_hint={"x": 0, "y": 0},
                md_bg_color=(0, 0, 0, 0.5),
                padding="8dp"
            )

            label = MDLabel(
                text=quote_text,
                halign="center",
                valign="middle",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Overline",
            )

            overlay.add_widget(label)
            layout.add_widget(img)
            layout.add_widget(overlay)
            card.add_widget(layout)
            card.bind(on_release=lambda inst, img=image_url, txt=quote_text: self.open_fullscreen())

            grid.add_widget(card)

        self.ids.loading_spinner.active = False
        self.ids.loading_txt.text=""
        self.loading_more = False

    def add_to_fullscreen_grid(self, cards):
        grid = self.ids.full_grid
        for image_url, quote_text in cards:
                
            card = ClickableCard(
                orientation="vertical",
                size_hint_y=None,
                height="470dp",
                radius=[20, 20, 20, 20],
                elevation=8,
                padding=0,
                ripple_behavior=True,
                md_bg_color=(0, 0, 0, 0)  # transparent card background
            )

            layout = RelativeLayout()

            img = AsyncImage(
                source=image_url,
                size_hint=(1, 1),
                allow_stretch=True,
                keep_ratio=False
            )

            quote_box = MDBoxLayout(
                orientation='vertical',
                size_hint=
                (1, None),
                height="470dp",
                pos_hint={"x": 0, "y": 0},
                md_bg_color=(0, 0, 0, 0.7),
                # radius=[20],
                padding="8dp",
            )

            label = MDLabel(
                text=quote_text,
                halign="center",
                valign="middle",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Subtitle1",
            )

            quote_box.add_widget(label)
            layout.add_widget(img)
            layout.add_widget(quote_box)
            card.add_widget(layout)
            grid.add_widget(card)

        self.loading_fullscreen_more = False
        self.ids.loading_spinner1.active = False


    def open_fullscreen(self):
        self.ids.quotes_screen_manager.current="full"
        full_grid = self.ids.full_grid
        full_grid.clear_widgets()

        main_grid = self.ids.grid
        for card in reversed(main_grid.children):
            layout = card.children[0]
            img_src = layout.children[1].source
            quote = layout.children[0].children[0].text
            self.add_to_fullscreen_grid([(img_src, quote)])
    def facts_random(self):
            
        response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en",verify=False, timeout=5)
        if response.status_code == 200:
            data = response.json()
            quote = data['text']
            return quote

    def advice(self):
        try:
            response = requests.get("https://api.adviceslip.com/advice",verify=False, timeout=5)
            if response.status_code == 200:
                data = response.json()
                quote = data['slip']['advice']
            return quote
        except:
            return"somthing went wrong please try again later"
    def get_activity(self):
        base_url = "https://zenquotes.io/api/random"

    
        response = requests.get(base_url, timeout=5)
        response.raise_for_status()  # Raises an error for non-200 responses
        data = response.json()

        # Make sure the response is as expected
        
        return f"{data[0]['q']} — {data[0]['a']}"
            
       
    def all_type_quotes(self):
        try:
            if self.mode=="love":
                url = "https://api.quotable.io/random?tags=love"
            elif self.mode=="motivation":
                url="https://api.quotable.io/random?tags=motivational"
            elif self.mode=="life":
                url="https://api.quotable.io/random?tags=life"
            elif self.mode=="success":
                url="https://api.quotable.io/random?tags=success"
            elif self.mode=="normal":
                url="https://api.quotable.io/random?"
            elif self.mode=="wisdom":
                url="https://api.quotable.io/random?tags=wisdom"
            elif self.mode=="happy":
                url="https://api.quotable.io/random?tags=happiness"
            elif self.mode=="friend":
                url="https://api.quotable.io/random?tags=friendship"
            elif self.mode=="inspirational":
                url="https://api.quotable.io/random?tags=inspirational"
            else:
                url = "https://api.quotable.io/random?"
            response = requests.get(url, verify=False, timeout=5)
            if response.status_code == 200:
                data = response.json()
                quote = data['content']
                author = data['author']
                return f'"{quote}"\n- {author}'
            

        except Exception:
            response = requests.get("https://api.adviceslip.com/advice",verify=False, timeout=5)
            if response.status_code == 200:
                data = response.json()
                quote = data['slip']['advice']
            return quote
    def get_random_quote(self):
        print(self.mode)
        try:
            if self.mode=="facts":
               return self.facts_random()
            elif self.mode == "advice":
                return self.advice()
            else:
              return  self.all_type_quotes()
           
            

        except Exception:
            response = requests.get("https://api.adviceslip.com/advice",verify=False, timeout=5)
            if response.status_code == 200:
                data = response.json()
                quote = data['slip']['advice']
            return quote

    def get_random_image_url(self):
        try:
            response = requests.get(
                "https://picsum.photos/600/400",
                allow_redirects=False,
                timeout=5
            )
            if response.status_code in [301, 302]:
                return response.headers['Location']
            else:
                return "https://picsum.photos/id/237/600/400"
        except:
            return "https://picsum.photos/id/237/600/400"


    def on_leave(self):
        for flag in self.stop_flags:
            flag.set()
        self.threads.clear()
        self.stop_flags.clear()
        self.mode = None
        if "grid" in self.ids:
            self.ids.grid.clear_widgets()
            print("Grid cleared.")


##########################################################################################################################


    def show_audio_files1(self):
        # Create the MDList
        audio_list = MDList()

        for file in os.listdir(self.record_save):
            if file.endswith(".wav") and "future_recording" in file:
                item = OneLineIconListItem(IconLeftWidget(icon="delete",on_release=lambda x, f=file: self.delete_audio(f)),text=file)

                # Play/stop on item click
                path = f"{self.record_save}\\\\{file}"
                print("path ",path)
                item.bind(on_release=lambda x, f=path: self.play_stop_audio(f))

                # Delete button
               

                # Wrap in horizontal box
                box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60),size_hint_x="1.2")
                box.add_widget(item)


                audio_list.add_widget(box)

        # Put the list in a scrollview
        scroll = MDScrollView()
        scroll.add_widget(audio_list)

        # Fix container height to make content visible
        content = MDBoxLayout(orientation='vertical', size_hint_y=None, height=dp(300))
        content.add_widget(scroll)

        # Show in dialog
        self.dialog = MDDialog(
            title="Audio Recordings",
            type="custom",
            content_cls=content,
            buttons=[],
        )
        self.dialog.open()

    def show_audio_files(self):
        
       
            
        audio_dir = self.record_save

        audio_list = MDList()

        for file in os.listdir(audio_dir):
            if file.endswith(".wav") and "future_recording" in file:
                wav_file = os.path.normpath(os.path.join(audio_dir,file))
                final = wav_file.replace("\\","\\\\")
                item = OneLineIconListItem(
                    IconLeftWidget(
                        icon="delete",
                        on_release=lambda x, f=final: self.delete_audio(f)
                    ),
                    text=file
                )

                # full_path = os.path.join(audio_dir, file)
                
                

                item.bind(on_release=lambda x, f=final: self.play_stop_audio(f))

                box = MDBoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(60),
                    size_hint_x=1.0
                )
                box.add_widget(item)
                audio_list.add_widget(box)

        # ScrollView
        scroll = MDScrollView()
        scroll.add_widget(audio_list)

        content = MDBoxLayout(orientation='vertical', size_hint_y=None, height=dp(300))
        content.add_widget(scroll)

        self.dialog = MDDialog(
            title="Audio Recordings",
            type="custom",
            content_cls=content,
            buttons=[],
        )
        self.dialog.open()


    def delete_audio(self, file_path):
        # Delete the audio file from the directory
        if os.path.exists(file_path):
            os.remove(file_path)
            self.snackbar = Snackbar(text="Audio file deleted")
            self.snackbar.open()
            self.show_audio_files()  # Refresh the list after deletion
        else:
            self.snackbar = Snackbar(text="Failed to delete audio")
            self.snackbar.open()

    def play_stop_audio(self, file_path):
        if self.current_playing_audio == file_path:
            # If the same audio is clicked again, stop it
            self.stop_audio()
        else:
            # If a different audio file is clicked, stop the previous one and play the new one
            if self.current_playing_audio:
                self.stop_audio()
            self.play_selected_audio(file_path)

    def play_selected_audio(self, file_path):
        # Load the selected audio file
        os.environ["KIVY_AUDIO"] = "sdl2"
        print("to play selected audio path :",file_path)
        self.current_playing_audio = file_path
        self.current_sound = SoundLoader.load(file_path)

        if self.current_sound:
            self.current_sound.play()

        else:
            self.snackbar = Snackbar(text="Failed to load audio file")
            self.snackbar.open()

    def stop_audio(self):
        if hasattr(self, 'current_sound') and self.current_sound:
            self.current_sound.stop()
            self.current_playing_audio = None  # Reset the current playing audio
            self.snackbar = Snackbar(text="Audio stopped")
            self.snackbar.open()


###################################################
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
            self.ids.record_button.icon = "pause"
        else:
            self.stop_recording()
            self.ids.record_button.icon = "microphone"

    def start_recording(self):
        if platform == "android":
            try:
                from android.permissions import request_permissions, Permission
                from plyer import audio
                request_permissions([Permission.RECORD_AUDIO, Permission.WRITE_EXTERNAL_STORAGE])
                audio.recorder("recorded_audio")
                self.is_recording = True
                self.ids.status_label.text = "Recording on Android..."
            except Exception as e:
                self.snackbar = Snackbar(text=f"Android record failed {e}")
                self.snackbar.open()
        else:
            self.is_recording = True
            self.snackbar = Snackbar(text="Recording is on")
            self.snackbar.open()
            self.recording = []
            self.stream = sd.InputStream(samplerate=self.fs, channels=1, callback=self.audio_callback)
            self.stream.start()

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()

        if platform == "android":
            self.save_recording_android()
        else:
            self.save_recording_pc()

      # Make sure this is at the top if not already

    def save_recording_pc(self):
        if self.recording:
            audio_data = np.concatenate(self.recording, axis=0)
            max_val = np.max(np.abs(audio_data)) or 1
            audio_data = audio_data / max_val

            # ✅ Format the current time to remove invalid characters
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            wav_file = os.path.normpath(os.path.join(self.record_save, f"{timestamp}_future_recording.wav")).replace("\\","\\\\")
            write(wav_file, self.fs, (audio_data * 32767).astype(np.int16))
            self.snackbar = Snackbar(text="Recording is saved")
            self.snackbar.open()
        else:
            self.snackbar = Snackbar(text="Recording failed")
            self.snackbar.open()


    def save_recording_android(self):
        wav_file = self.record_save()
        self.play_audio(wav_file)
        self.snackbar = Snackbar(text="recording is saved")
        self.snackbar.open()


            
    def audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            self.recording.append(indata.copy())
            audio_data = indata[:, 0]
            rms = np.sqrt(np.mean(audio_data**2))
            threshold = 0.01
            if rms > threshold:
                max_val = np.max(np.abs(audio_data)) or 1
                normalized = (audio_data / max_val).tolist()
            else:
                normalized = [0.01 * np.sin(i / 5.0) for i in range(len(audio_data))]
            self.update_waveform(normalized)



    def switch_screen(self, screen_name):
        """Switches the screen and updates chip colors."""
        self.ids.quotes_screen_manager.current = screen_name

    @mainthread
    def update_waveform(self, data):
        self.ids.waveform.waveform = data






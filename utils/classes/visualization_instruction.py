from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

from kivy.properties import StringProperty,NumericProperty
from kivy.clock import Clock

from kivy.core.audio import SoundLoader
import os
from kivymd.uix.snackbar import Snackbar

from kivy.properties import NumericProperty, StringProperty

class visualization_instruction(Screen):
    visual_play_icon = StringProperty("play")  
    record_play_icon = StringProperty("play") 
    angle = NumericProperty(0) 
    animation_event = None
    visual_sound = None
    record_sound = None

    # Separate pause times
    visual_paused_time = 0
    record_paused_time = 0

    # Separate playing states
    is_visual_playing = False
    is_record_playing = False
    
    def __init__(self, **kw):
        super().__init__(**kw)
        
        
    
    def toggle_visual_audio(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        record_path =  os.path.join(base_dir, "sounds","final_output.mp3")
        print(record_path)
        if os.path.exists(record_path):
            """Toggles playback for visual instructions."""
            if self.is_visual_playing:
                self.stop_audio("visual")
            else:
                self.play_audio("visual", record_path)
        else:
            self.snackbar = Snackbar(text="Please go back and do it again !",snackbar_x="10dp",snackbar_y="10dp",size_hint_x=(Window.width - (dp(10) * 2)) / Window.width)
            self.snackbar.open()         
    def toggle_record_audio(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        record_path =  os.path.join(base_dir, "sounds","voice_recording_affirmation.mp3")
        if os.path.exists(record_path):
        
            if self.is_record_playing:
                self.stop_audio("record")
            else:
                self.play_audio("record", record_path)
        else:
            self.snackbar = Snackbar(text="Please go back and do it again !",snackbar_x="10dp",snackbar_y="10dp",size_hint_x=(Window.width - (dp(10) * 2)) / Window.width)
            self.snackbar.open()

    def play_audio(self, mode, filename):
        """Plays or resumes the selected audio."""
        if mode == "visual":
            if not self.visual_sound:
                self.visual_sound = SoundLoader.load(filename)

            if self.visual_sound:
                self.visual_sound.seek(self.visual_paused_time)
                self.visual_sound.volume = 1.0
                self.visual_sound.play()
                self.visual_sound.bind(on_stop=lambda *args: self.audio_finished("visual"))
                self.is_visual_playing = True
                self.visual_play_icon = "stop"

                Clock.schedule_interval(self.update_progress_bar, 1)
                self.start_rotation()

        elif mode == "record":
            
                if not self.record_sound:
                    self.record_sound = SoundLoader.load(filename)

                if self.record_sound:
                    self.record_sound.seek(self.record_paused_time)
                    self.record_sound.volume = 1.0
                    self.record_sound.play()
                    self.record_sound.bind(on_stop=lambda *args: self.audio_finished("record"))
                    self.is_record_playing = True
                    self.record_play_icon = "stop"

                    Clock.schedule_interval(self.update_progress_bar, 1)
                    self.start_rotation()

    def stop_audio(self, mode):
        """Stops the selected audio and saves the current position."""
        if mode == "visual" and self.visual_sound:
            self.visual_paused_time = self.visual_sound.get_pos()
            self.visual_sound.stop()
            self.is_visual_playing = False
            self.visual_play_icon = "play"

        elif mode == "record" and self.record_sound:
            self.record_paused_time = self.record_sound.get_pos()
            self.record_sound.stop()
            self.is_record_playing = False
            self.record_play_icon = "play"

        self.stop_rotation()

    def audio_finished(self, mode):
        """Handles actions when audio ends."""
        if mode == "visual":
            self.is_visual_playing = False
            self.visual_play_icon = "reload"
            self.stop_rotation()
        elif mode == "record":
            self.is_record_playing = False
            self.record_play_icon = "reload"
            self.stop_rotation()

    def update_progress_bar(self, dt):
        """Updates progress bars and time labels for both audio files."""
        if self.is_visual_playing and self.visual_sound:
            current_pos = self.visual_sound.get_pos()
            duration = self.visual_sound.length

            if duration and current_pos is not None:
                self.ids.visual_progress_bar.value = (current_pos / duration) * 100
                self.ids.visual_current_time.text = self.format_time(current_pos)
                self.ids.visual_total_time.text = self.format_time(duration)

                if current_pos >= duration - 1:
                    self.audio_finished("visual")

        elif self.is_record_playing and self.record_sound:
            current_pos = self.record_sound.get_pos()
            duration = self.record_sound.length

            if duration and current_pos is not None:
                self.ids.record_progress_bar.value = (current_pos / duration) * 100
                self.ids.record_current_time.text = self.format_time(current_pos)
                self.ids.record_total_time.text = self.format_time(duration)

                if current_pos >= duration - 1:
                    self.audio_finished("record")

    def format_time(self, seconds):
        """Formats seconds into MM:SS format."""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"

    def start_rotation(self):
        """Starts rotating the album image when music plays."""
        if not self.animation_event:
            self.animation_event = Clock.schedule_interval(self.rotate_image, 1 / 30)

    def stop_rotation(self):
        """Stops rotating the album image when music stops."""
        if self.animation_event:
            Clock.unschedule(self.animation_event)
            self.animation_event = None

    def rotate_image(self, dt):
        """Rotates the album image smoothly."""
        self.angle += 2

    def switch_screen(self, screen_name):
        """Handles navigation between screens."""
        self.ids.screen_manager1.current = screen_name

# this is main app code all of them is testing file's 
from kivy.metrics import dp
import time
from kivy.uix.screenmanager import Screen
from utils.gemini.gemini_ai import get_visualization_instruction
from kivy.clock import Clock
from kivy.app import App
from kivymd.uix.taptargetview import MDTapTargetView
import os
import sounddevice as sd
import numpy as np
import wave
from pydub import AudioSegment
from kivy.properties import  StringProperty,NumericProperty, BooleanProperty
from kivy.utils import platform
from utils.classes.database import show_loa_form_data,add_or_update_voice_affirmation_data,show_voice_affirmation_data
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Color

class WavingSignal(Widget):
    wave_amplitude = NumericProperty(0)
    is_recording = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.animate_wave, 1 / 30)  # 30 FPS

    def start_wave(self):
        """Starts the wave animation when recording starts."""
        self.is_recording = True

    def stop_wave(self):
        """Stops the wave animation when recording stops."""
        self.is_recording = False

    def animate_wave(self, dt):
        """Creates a smooth wave effect when recording."""
        self.canvas.clear()
        with self.canvas:
            Color(0, 1, 0.5, 1)  # Neon green
            for i in range(5):
                size = 100 + i * 20 + self.wave_amplitude
                Ellipse(pos=(self.center_x - size / 2, self.center_y - size / 2), size=(size, size))
        
        if self.is_recording:
            self.wave_amplitude = (self.wave_amplitude + 2) % 20  # Smooth pulsing effect

class voice_affirmation(Screen):
    record_icon = StringProperty("microphone")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tap_target_view = None
        self.tap_target_view2 = None
    def progress_bar(self):
        spinner = self.ids.spinner
        output_label = self.ids.output_label
        
        # Show spinner
        spinner.active = True
        output_label.text = "Generating text..."
        
        # Simulate text generation with a delay
        Clock.schedule_once(lambda dt: self.generate_affirmation("false"), 2)

    
    def adjust_loa_display(self, affirmation_text):
        """Dynamically adjust and display LoA form data in MDScrollView."""
        
        # Reference to the MDLabel and MDBoxLayout
        loa_label = self.ids.voice_affirmation_text
        box_layout = self.ids.v_dis_loa
        
        # Update the text of the label
        loa_label.text = affirmation_text
        
        # Update the texture to calculate the correct size
        loa_label.texture_update()
        
        # Adjust label height to fit content
        loa_label.height = loa_label.texture_size[1] + dp(10)
        
        # Adjust box layout height based on content
        box_layout.height = loa_label.height + dp(20)  # Add padding for better spacing
        
        # Auto-scroll to bottom after adding content
        scroll_view = self.ids.v_scroll_view
        Clock.schedule_once(lambda dt: scroll_view.scroll_to(loa_label))


    def generate_affirmation(self,reaf):
        name = "Uvaissaifi"
        #generated_affirmation1 = self.ids.voice_user_name
        self.ids.user_name_voice.text = f'Hey {name} lets begin'
        
        #generated_affirmation1 = self.ids.generated_affirmation_voice
        try:
            print("using database data")
            content = show_loa_form_data()
        except Exception as e:
            print(f"{e}")
           
        try:
            if reaf == "false":
                affirmation = show_voice_affirmation_data()
                if affirmation =="No voice affirmation data found.":
                    print("now after no voice affirmation data ")
                    affirmation = get_visualization_instruction(content,"instruction")
                    print("saving data ")
                    add_or_update_voice_affirmation_data(affirmation)
                    print(len(affirmation))
            

            
            elif reaf == "true":
                print("this is working")
                affirmation = get_visualization_instruction(content,"instruction")
                print("after visualization")
                add_or_update_voice_affirmation_data(voice_data=affirmation)
                print(len(affirmation))
         
        except:
            affirmation = "somethings went wrong please try again after sometime"
        try:
            self.adjust_loa_display(affirmation_text=affirmation)
        except:
            print("somthing not right")

        spinner = self.ids.spinner
        output_label = self.ids.output_label
    
        # Hide spinner and update label with generated text
        spinner.active = False
        output_label.text = ""
    def reload_aff(self):
        spinner = self.ids.spinner
        output_label = self.ids.output_label
        print("working")
        
        spinner.active = True
        self.ids.voice_affirmation_text.text = ""
        output_label.text = "Generating text..."
        self.generate_affirmation("true")
    def ensure_writable_directory(self):
        """Ensure writable sounds directory and return its path for PC and Android."""
        
        # Check platform to determine where to create sounds directory
        if platform == "android":
            data_dir = App.get_running_app().user_data_dir  
          

            # Define sounds directory path
            writable_sounds_dir = os.path.join(data_dir, "utils", "sounds")
            print(f"✅ Writable sounds dir: {writable_sounds_dir}")

            # Create sounds directory if not exists
            if not os.path.exists(writable_sounds_dir):
                os.makedirs(writable_sounds_dir)
                print(f"✅ Created sounds directory: {writable_sounds_dir}")
            else:
                print(f"✅ Sounds directory already exists: {writable_sounds_dir}")

            # Return writable sounds directory
        else:
            
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            writable_sounds_dir =  os.path.join(base_dir, "sounds")
           
        return writable_sounds_dir
    def toggle_recording(self):
        """Toggles recording start/stop."""
        wave_widget = self.ids.wave
        if not wave_widget.is_recording:
            self.start_recording()
            wave_widget.start_wave()
            self.record_icon = "stop"
        else:
            self.stop_recording()
            wave_widget.stop_wave()
            self.record_icon = "microphone"

    def start_recording(self):
        """Starts recording audio."""
        self.fs = 44100
        self.recording_list = []
        self.is_recording = True
        self.start_time = time.time()
        
        self.stream = sd.InputStream(samplerate=self.fs, channels=1, dtype=np.float32, callback=self.callback)
        self.stream.start()

    def callback(self, indata, frames, time, status):
        """Captures incoming audio data."""
        if self.is_recording:
            self.recording_list.append(indata.copy())
    
    def stop_recording(self):
        """Stops recording and saves the file."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        
        self.recording = np.concatenate(self.recording_list, axis=0)
        self.recording = self.recording / np.max(np.abs(self.recording))
        self.recording = (self.recording * 32767).astype(np.int16)
        wav_path = self.ensure_writable_directory()

        # Path to save tts_output.mp3 in writable directory
        wav_file = os.path.join(wav_path, "voice_recording_affirmation.wav")
        #wav_file = "sounds/affirmation.wav"
        with wave.open(wav_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.fs)
            wf.writeframes(self.recording.tobytes())
        
        # mp3_file = "sounds/affirmation.mp3"
        mp3_file = os.path.join(wav_path, "voice_recording_affirmation.mp3")
        sound = AudioSegment.from_wav(wav_file)
        sound.export(mp3_file, format="mp3")
        os.remove(wav_file)
        # Play the recorded sound
    def switch_screen(self, screen_name,selected_chip):
        self.ids.screen_manager.current = screen_name

        # Reset all chips to default color
        for chip_id in ["voice_chip1", "voice_chip2"]:
            self.ids[chip_id].md_bg_color = "#005957"
        
        # Highlight the selected chip
        selected_chip.md_bg_color = "#7d9b94"
        
        print(screen_name)
    def toggle_tap_target(self,num):
        """
        Toggles the MDTapTargetView (open/close).
        """
        if num == "1":
            if not self.tap_target_view:
                # Create MDTapTargetView if it doesn't exist
                self.tap_target_view = MDTapTargetView(
                    widget=self.ids.button,
                    title_text=" Vibration",
                    title_text_size="30sp",
                    description_text=(
                        "vibration refers to the energetic state\n of being that you emit into the universe\n through your thoughts, feelings, and beliefs.\nIt's a core concept in the LOA\n, suggesting that everything in the universe\n, including ourselves,\n is made up of energy vibrating at different frequencies"
                    ),
                    description_text_size="10sp",
                    widget_position="top",
                )
                # Bind the on_close event to reset state
                
                self.tap_target_view.outer_circle_color = (125/255, 155/255, 148/255)
                self.tap_target_view.bind(on_close=self.reset_tap_target)

            # Toggle based on current state
            if self.tap_target_view.state == "close":
                self.tap_target_view.start()
            else:
                self.tap_target_view.stop()
        if num == "2":
            if not self.tap_target_view2:
                # Create MDTapTargetView if it doesn't exist
                self.tap_target_view2 = MDTapTargetView(
                    widget=self.ids.button2,
                    title_text="Self-Love",
                    title_text_size="20sp",
                    description_text=(
                        "self-love is not just a feel-good concept\n it's a powerful tool for aligning yourself with\n the positive vibrations necessary to effectively use\n the Law of Attraction. When you love and\n accept yourself, you naturally raise your\n vibration, believe in your worthiness, \nand create a strong foundation for attracting\n positive experiences into your life."
                        
                    ),
                    description_text_size="10sp",
                    widget_position="top",
                )
                # Bind the on_close event to reset state
                self.tap_target_view2.bind(on_close=self.reset_tap_target)
                
                self.tap_target_view2.outer_circle_color = (125/255, 155/255, 148/255)
            # Toggle based on current state
            if self.tap_target_view2.state == "close":
                self.tap_target_view2.start()
            else:
                self.tap_target_view2.stop()

    def reset_tap_target(self, *args):
        """
        Resets the state of MDTapTargetView when closed.
        """
        try:
            self.tap_target_view.state = "close"
            self.tap_target_view2.state = "close"
        except Exception as e:
            print(f"close not working : {e}")
    


from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.core.window import Window
from kivymd.uix.label import MDLabel
from utils.gemini.gemini_ai import get_visualization_instruction
from kivy.clock import Clock
from kivymd.uix.taptargetview import MDTapTargetView
from kivy.core.audio import SoundLoader
from gtts import gTTS
import tempfile
import shutil
from moviepy.editor import AudioFileClip, CompositeAudioClip
import os
from kivymd.uix.snackbar import Snackbar

from kivy.app import App
from kivy.utils import platform
from  utils.classes.database import show_loa_form_data,get_database_path
import threading
class visualization_tech(Screen):

    global so
    def switch_screen(self, screen_name):
        self.ids.screen_manager.current = screen_name
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tap_target_view = None
        self.tap_target_view2 = None
    def check_file(self):
        loaform_data = show_loa_form_data()
        if loaform_data == "no_data":  # Check if file exists
            # ⚠️ File is empty → Redirect to form page
            App.get_running_app().change_screen("loaform")
        

    def toggle_tap_target(self,num):
        """
        Toggles the MDTapTargetView (open/close).
        """
        if num == "1":
            if not self.tap_target_view:
                # Create MDTapTargetView if it doesn't exist
                self.tap_target_view = MDTapTargetView(
                    widget=self.ids.button,
                    title_text="Imagination",
                    title_text_size="30sp",
                    description_text=(
                        "Imagination plays a powerful role in the \n"
                        "effectiveness of affirmations. When you use your \n"
                        "imagination to vividly visualize the desired \n"
                        "outcome while repeating your affirmations,\n"
                        "you reinforce the belief system that supports those goals.\n"
                        "This heightened sense of belief can motivate you to \n"
                        "take action and make choices that align with your affirmations,\n"
                        "ultimately increasing the likelihood of achieving your desired results."
                    ),
                    description_text_size="10sp",
                    widget_position="top",
                )
                # Bind the on_close event to reset state
                self.tap_target_view.bind(on_close=self.reset_tap_target)
                self.tap_target_view.outer_circle_color =(255 / 255, 242 / 255, 230 / 255)
                self.tap_target_view.title_text_color = (0, 0, 0)  # Deep Purple
                self.tap_target_view.description_text_color = (0, 0, 0)
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
                    title_text="Manifestation",
                    title_text_size="20sp",
                    description_text=(
                        "Manifestation is the process of deliberately \ncreating your reality by focusing your thoughts \n"
                        "feelings, and actions on what you desire \n"
                        "It involves aligning yourself with the energy\n of your desired outcome and taking inspired action towards it \n"
                        
                    ),
                    description_text_size="10sp",
                    widget_position="top",
                )
                # Bind the on_close event to reset state
                self.tap_target_view2.bind(on_close=self.reset_tap_target)
                self.tap_target_view2.outer_circle_color = (255 / 255, 242 / 255, 230 / 255)
                self.tap_target_view2.title_text_color = (0, 0, 0)  
                self.tap_target_view2.description_text_color = (0, 0, 0)
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
   
    

    def ensure_writable_directory(self):
        """Ensure writable sounds directory and return its path for PC and Android."""
        
        # Check platform to determine where to create sounds directory
        if platform == "android":
            data_dir = App.get_running_app().user_data_dir  
          

            # Define sounds directory path
            writable_sounds_dir = os.path.join(data_dir, "utils", "sounds")
            print(f" Writable sounds dir: {writable_sounds_dir}")

            # Create sounds directory if not exists
            if not os.path.exists(writable_sounds_dir):
                os.makedirs(writable_sounds_dir)
                print(f" Created sounds directory: {writable_sounds_dir}")
            else:
                print(f" Sounds directory already exists: {writable_sounds_dir}")

            # Return writable sounds directory
        else:
            
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            writable_sounds_dir =  os.path.join(base_dir, "sounds")
        return writable_sounds_dir


    def mix_audio_with_music(self,speech_file, music_file, music_volume=1.0):
        #this function is second function for wakeup
        try:
            print("🔄 Processing audio...")

            # Load speech and music files
            self.speech = AudioFileClip(speech_file)
            self.music = AudioFileClip(music_file).volumex(music_volume)

            # Ensure music duration matches speech
            self.music_duration = self.music.duration
            self.speech_duration = self.speech.duration

            if self.music_duration < self.speech_duration:
                self.num_repeats = int(self.speech_duration // self.music_duration) + 1
                self.music_clips = [self.music] * self.num_repeats  # Duplicate music
                music = CompositeAudioClip(self.music_clips).subclip(0, self.speech_duration)
            else:
                self.music = self.music.subclip(0, self.speech_duration)

            # Combine audio
            self.final_audio = CompositeAudioClip([self.music, self.speech])

            # Use a temporary file to avoid permission issues
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name

            # Export final audio (❌ Removed threads=False)
            self.final_audio.write_audiofile(temp_output, codec="mp3", fps=44100)

            # Close files
            self.speech.close()
            self.music.close()
            self.final_audio.close()

            # Move temp file to final output
            sounds_dir = self.ensure_writable_directory()

            # Path to save tts_output.mp3 in writable directory
            output_file = os.path.join(sounds_dir, "final_output.mp3")
            # output_file = "sounds/final_output.mp3"

            shutil.move(temp_output, output_file)

            print(f"✅ Mixed audio saved to: {output_file}")

        except Exception as e:
            print(f"❌ Error occurred: {e}")

        finally:
            # Ensure all resources are cleaned up
            try:
                self.speech.close()
                self.music.close()
                self.final_audio.close()
            except Exception:
                pass  # Ignore errors if already closed

    def _audio_worker(self, music):
        try:
            # — heavy part —
            content = show_loa_form_data()                  # DB / file hit
            tts_text = get_visualization_instruction(content, "instruction")

            sounds_dir = self.ensure_writable_directory()
            tts_path   = os.path.join(sounds_dir, "tts_output.mp3")

            gTTS(tts_text).save(tts_path)                   # network + disk
            self.mix_audio_with_music(tts_path, music)      # CPU / I/O

            if os.path.exists(tts_path):
                os.remove(tts_path)

        except Exception as e:
            # pass any error back to the UI thread for display / logging
            Clock.schedule_once(lambda dt: self._on_audio_error(str(e)), 0)
            return

        # tell the UI we’re done (must be on main thread)
        Clock.schedule_once(lambda dt: self._on_audio_done(), 0)

    # -------------------------------------------------------------
    # 2) ------------- wrappers callable from UI ------------------
    # -------------------------------------------------------------
    def play_audio(self, music):
        """Entry point called from *main* thread.
        Starts the worker thread and shows spinner right away."""
        # stop any previous Sound instance
        if getattr(self, "sound", None):
            self.sound.stop()

        # show spinner / message (UI thread, so direct access is fine)
        self.ids.spinner_v.active = True
        self.ids.output_label.text = "Generating instruction\nwait 5‑10 sec..."

        # launch background thread **daemon=True** so it won’t block app exit
        threading.Thread(
            target=self._audio_worker,
            args=(music,),
            daemon=True,
        ).start()

    # -------------------------------------------------------------
    # 3) ------------- UI‑thread callbacks ------------------------
    # -------------------------------------------------------------
    def _on_audio_done(self):
        """Runs on main thread after worker finishes successfully."""
        App.get_running_app().change_screen("visualization_instruction")
        self.ids.spinner_v.active = False
        self.ids.output_label.text = ""

    def _on_audio_error(self, msg):
        """Runs on main thread if worker raised an exception."""
        self.ids.spinner_v.active = False
        self.ids.output_label.text = f"Error: {msg}"
        
    def play_background_sound(self,soundname):
        global so
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # Go 2 levels up to app root)
        if soundname == "1":
            if hasattr(self, 'sound') and self.sound:
                self.sound.stop()
            background_music_path =  os.path.join(base_dir, "sounds","inspiring-piano-music.mp3")
            so = background_music_path
            # background_thread = threading.Thread(target=self.play_sound, args=(background_music_path,))
            # background_thread.start()
            self.play_sound(background_music_path,)
            new_label = MDLabel(text="Piano ",halign="center")
            self.ids.Msound.clear_widgets()
            new_label.theme_text_color = "Custom"
            new_label.text_color="black"
            self.ids.Msound.add_widget(new_label)
        elif soundname == "2":
            if hasattr(self, 'sound') and self.sound:
                self.sound.stop()
            background_music_path = os.path.join(base_dir, "sounds","evening-by-the-fireplace.mp3")
            so = background_music_path
            self.play_sound(background_music_path,)
            new_label = MDLabel(text="Fireplace",halign="center")
            new_label.theme_text_color = "Custom"
            new_label.text_color="black"
            self.ids.Msound.clear_widgets()
            
            self.ids.Msound.add_widget(new_label)
            
        elif soundname == "3":
            if hasattr(self, 'sound') and self.sound:
                self.sound.stop()
            background_music_path = os.path.join(base_dir, "sounds","Calming.mp3")
            so = background_music_path
            self.play_sound(background_music_path,)
            new_label = MDLabel(text="Healing",halign="center")
            self.ids.Msound.clear_widgets()
            new_label.theme_text_color = "Custom"
            new_label.text_color="black"
            self.ids.Msound.add_widget(new_label)
        elif soundname == "4":
            if hasattr(self, 'sound') and self.sound:
                self.sound.stop()
            background_music_path = os.path.join(base_dir, "sounds","motivation.mp3")
            so=background_music_path
            print(so)
            self.play_sound(background_music_path,)
            new_label = MDLabel(text="Motivation",halign="center")
            self.ids.Msound.clear_widgets()
            new_label.theme_text_color = "Custom"
            new_label.text_color="black"
            self.ids.Msound.add_widget(new_label)
        elif soundname == "ok":
            try:
                if hasattr(self, 'sound') and self.sound:
                    self.sound.stop()

                spinner = self.ids.spinner_v
                output_label = self.ids.output_label

                # Show spinner and message
                spinner.active = True
                output_label.text = "Generating instruction\nwait 5 to 10 sec..."

                # Run play_audio in a background thread
                def background_task():
                    self.play_audio(so)
                    # Once done, stop spinner and optionally update label (on main thread)
                    # Clock.schedule_once(lambda dt: self.on_audio_done(), 0)

                threading.Thread(target=background_task).start()

                
                
                
            except Exception as e:
                print(f"{e}")
                self.snackbar = Snackbar(text="Please Select the music !",snackbar_x="10dp",snackbar_y="10dp",size_hint_x=(Window.width - (dp(10) * 2)) / Window.width)
                self.snackbar.open()
                spinner = self.ids.spinner_v
                output_label = self.ids.output_label
                spinner.active = False
                output_label.text = ""
        # Play the background music in a separate thread to avoid blocking the main UI
   
    
    def play_sound(self, audio_path):
        """
        Play the sound using Kivy's SoundLoader.
        """
        self.sound = SoundLoader.load(audio_path)
        if self.sound:
            self.sound.volume = 0.01  # Set background music volume to 20%
            self.sound.play()
        else:
            print("Background music not found.")

    def stop_sound(self):
        """
        Stop the sound if it's playing.
        """
        if hasattr(self, 'sound') and self.sound:
            self.sound.stop()
            print("Background sound stopped.")
        else:
            print("No sound is currently playing.")
    
    def generate_affirmation(self,num):
        global affirmation
        if num == "1":
        
            generated_affirmation1 = self.ids.loa_form_text
            try:
                try:
                    print("using the database data")
                    content = show_loa_form_data()
                    print(content)
                except Exception as e:
                    print(f"{e}")
                    
                
                affirmation = get_visualization_instruction(content,"ok")
                print(len(affirmation))
            except:
                affirmation = "somethings went wrong please try again after sometime"
        
            print("using adjust function")
            self.adjust_loa_display(affirmation_text=affirmation)
        
    
        else:
            name = "Uvaissaifi"
            generated_affirmation1 = self.ids.user_name
            new_label = MDLabel(
                text=f'Hey {name} lets begin',
                halign="center",
                font_style="H4",

                pos_hint={"top":1.39}
            )
            new_label.theme_text_color = "Custom"
            new_label.text_color="black"
            new_label.bold=True
            new_label.padding=10
            generated_affirmation1.add_widget(new_label)
    def adjust_loa_display(self, affirmation_text):
        """Dynamically adjust and display LoA form data in MDScrollView."""
        
        # Reference to the MDLabel and MDBoxLayout
        loa_label = self.ids.loa_form_text
        box_layout = self.ids.dis_loa
        
        # Update the text of the label
        loa_label.text = affirmation_text
        
        # Update the texture to calculate the correct size
        loa_label.texture_update()
        
        # Adjust label height to fit content
        loa_label.height = loa_label.texture_size[1] + dp(10)
        
        # Adjust box layout height based on content
        box_layout.height = loa_label.height + dp(20)  # Add padding for better spacing
        
        # Auto-scroll to bottom after adding content
        scroll_view = self.ids.scroll_view
        Clock.schedule_once(lambda dt: scroll_view.scroll_to(loa_label))


    def switch_screen(self, screen_name,selected_chip):
        self.ids.screen_manager.current = screen_name

        # Reset all chips to default color
        for chip_id in ["visual_chip1", "visual_chip2"]:
            self.ids[chip_id].md_bg_color = "#fff2e6"
        
        # Highlight the selected chip
        selected_chip.md_bg_color = "#6600ff"
        print(screen_name)
    

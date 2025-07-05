
from kivy.properties import NumericProperty,StringProperty
from kivy.utils import get_color_from_hex
from kivymd.uix.snackbar import Snackbar
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from  kivymd.uix.spinner.spinner import MDSpinner
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
import os
import json
from kivy.app import App
from plyer import stt,tts
from kivymd.uix.fitimage import FitImage
from utils.classes.database import get_database_path
import platform
import threading
import logging
from kivy.animation import Animation
from threading import Lock
from utils.gemini.gemini_ai import get_cbt_response
from utils.classes.database import show_cbt_form_data
from utils.image_gen.img_gen import image_generator

# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('comtypes').setLevel(logging.ERROR)
is_android = platform.system() == "Android"

if not is_android:
    import speech_recognition as sr
    import pyttsx3
else:
    from jnius import autoclass
    from android import mActivity
    

class Command(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_size = 17

class Response(MDLabel):
    text = StringProperty()
    source = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_size = 17
    pos_hint = { "top": 11}
 

class imgery_chat(Screen):
    def __init__(self, **kwargs):
        
        self.is_listening = False
        self.tts_lock = Lock()
        self.recognition_thread = None

        super().__init__(**kwargs)
        if not is_android:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Adjusting speech rate (optional)

        # self.on_start()
    
    def stop_all(self):
        if self.is_listening:
            self.is_listening = False
            self.animate_glow(False)
        try:
            # Stop the speech recognition thread if it's running
            if self.listening_thread and self.listening_thread.is_alive():
                print("Stopping listening thread.")
                self.listening_thread.join(timeout=2)
                self.listening_thread = None
        except Exception as e:
            print(e)
        # Stop the text-to-speech engine if running
        if hasattr(self, 'tts_engine') and self.tts_engine is not None:
            print("Stopping TTS engine.")
            self.tts_engine.stop()

        # Stop recognition thread if used
        if self.recognition_thread and self.recognition_thread.is_alive():
            print("Stopping recognition thread.")
            self.recognition_thread.join(timeout=2)
            self.recognition_thread = None

        MDApp.get_running_app().change_screen("imagery")
    def handle_thought_session(self):
        print("now handle thought function")
        base_dir = get_database_path()        
        file_path =  os.path.join(base_dir[2],"imagery_conversation_log.json") 


        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            # Show dialog to ask if user wants to continue or start new
            self.dialog = MDDialog(
                title="Resume Conversation?",
                text="Would you like to continue your previous conversation or start a new one?",
                buttons=[
                    MDFlatButton(
                        text="New Conversation",
                        on_release=lambda x: self.new_conversation(file_path)
                    ),
                    MDFlatButton(
                        text="Continue",
                        on_release=lambda x: self.continue_old_session(file_path)
                    ),
                ],
            )
            self.dialog.md_bg_color = (0, 0, 0, 0.5)
            self.dialog.open()
        else:
            # If no previous conversation, just start new session
            self.start_new_session(file_path)

    def new_conversation(self, file_path):
        if hasattr(self, 'dialog'):
            self.dialog.dismiss()

        # Clear the JSON file
        with open(file_path, 'w') as f:
            pass
            print("after go to the instropage")
        # Redirect to thought form screen
                
        MDApp.get_running_app().change_screen("imagery")

        
    def continue_old_session(self, file_path):
        if hasattr(self, 'dialog'):
            self.dialog.dismiss()

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

                delay = 0
                skip_first_user = True  # flag to skip only the first user message

                for entry in data:
                    role = entry.get("role")
                    message = entry.get("parts")

                    if role == "user":
                        if skip_first_user:
                            skip_first_user = False
                            continue  # skip the first user prompt
                        Clock.schedule_once(self.make_lambda("chat_command", message), delay)
                    elif role == "model":
                        Clock.schedule_once(self.make_lambda("chat_response", message), delay)

                    delay += 0.1
        except Exception as e:
            print(f"Error loading chat history: {e}")

   

    def make_lambda(self, role, msg):
        return lambda dt: self.all_chat_response(role, msg)

    def start_new_session(self, file_path):
        # Get form data
        form_data = show_cbt_form_data(mode="imgery")

        if form_data:
            prompt = f"""
            You are a warm, compassionate CBT therapist guiding a user through an imagery-based CBT session using their personal data (filled out in the form).

            The user has described the emotional experience they are dealing with:

            Situation: {form_data["situation"]}

            Mental Image: {form_data["mental_img"]}

            Exploration: {form_data["exploration"]}

            Physical Feelings: {form_data["emotional"]}

            Begin by helping them visualize a safe, calming space. Proceed gently with one question at a time, waiting for their response before continuing to the next step.

            Be sure to respond to their answers with empathy and reflection.

            Your tone should be warm, caring, and supportive, encouraging openness. If they struggle, offer gentle reassurance.
            """
            response = get_cbt_response(prompt,mode="imgery_cbt")
            # response = get_thought_response(prompt)
            Clock.schedule_once(lambda dt: self.all_chat_response("chat_response", response), 0)
        else:
            Snackbar(text="Please fill the form").open()
            app = App.get_running_app()
            app.change_screen("imagery")
            app.sm.get_screen("imagery").ids.imgery_screen_manager.current = "imgery_form"
            # App.get_running_app().change_screen("thought")
            return 
        
    def switch_screen(self, screen_name):
        """Switches the screen and updates chip colors."""
        self.ids.chat_screen_manager.current = screen_name
    def on_start(self):
        print("on_start working")
        self.handle_thought_session()

 
    def show_loading(self):
        """Show a loading bubble styled like a chat message."""
        # Remove if already added
        if hasattr(self, "loading_container") and self.loading_container.parent:
            self.ids.chat_list.remove_widget(self.loading_container)

        self.loading_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            padding=dp(10),
            spacing=dp(10),
            md_bg_color=(0, 0, 0,0.8),  # light background like a message
            radius=[20, 20, 20, 20],
            pos_hint={"right": 1},
        )

        self.loading_spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(20), dp(20)),
            active=True,
            color=(0.13333333333333333, 0.5411764705882353, 0.615686274509804, 1),
            pos_hint={"center_y": 0.5}
        )

        self.loading_label = MDLabel(
            text="Let me generate somthing",
            theme_text_color="Custom",
            text_color=(0.13333333333333333, 0.5411764705882353, 0.615686274509804),
            font_style="Caption",
            size_hint_y=None,
            height=dp(20),
            
        )

        self.loading_container.add_widget(self.loading_label)
        self.loading_container.add_widget(self.loading_spinner)
        

        self.ids.chat_list.add_widget(self.loading_container)

        # Scroll to bottom if needed
        Clock.schedule_once(lambda dt: setattr(self.ids.scroll_view, "scroll_y", 0))
    def show_image(self,text):

        self.image_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(200),
            padding=dp(10),
            spacing=dp(10),
            md_bg_color=(0, 0, 0,0.8),  # light background like a message
            radius=[20, 20, 20, 20],
            pos_hint={"right": 1},
        )


        self.image_label = FitImage(
            source= text
            
        )

        self.image_container.add_widget(self.image_label)
        #self.loading_container.add_widget(self.loading_spinner)
        

        self.ids.chat_list.add_widget(self.image_container)

        # Scroll to bottom if needed
        Clock.schedule_once(lambda dt: setattr(self.ids.scroll_view, "scroll_y", 0))
        Clock.schedule_once(lambda dt: self.run_tts_and_resume("here is your generated image"), 0)

    def hide_loading(self):
        """Removes the loading spinner from the chat layout."""
        if hasattr(self, "loading_container"):
            self.ids.chat_list.remove_widget(self.loading_container)
            del self.loading_container  # Remove reference

   # Start bot response in background

    def all_chat_response(self, name, response=""):
        """Updates UI components safely using Kivy's main thread."""
        def update_ui(*args):


            if name == "chat_command":
                value = response 
                size = min(0.9, max(0.22, len(value) * 0.03))  
                
                self.ids.chat_list.add_widget(Command(text=value, size_hint_x=size, halign="center"))
            elif name == "chat_response":
                value = response
                size = min(0.9, max(0.22, len(value) * 0.03))
                self.ids.chat_list.add_widget(Response(text=value,size_hint_x=size, halign="center"))  
            elif name =="chat_resume":
                size = min(0.9, max(0.22, len(response) * 0.03))  
                self.ids.chat_list.add_widget(Command(text=response, size_hint_x=size, halign="center"))
        Clock.schedule_once(update_ui, 0)  # Ensure UI updates in main thread

   ####################################################################################
    
    def toggle_listening(self):
        if self.is_listening:
            self.is_listening = False
            self.animate_glow(False)
        else:
            self.is_listening = True
            self.animate_glow(True)
            self.start_listening()


    def start_listening(self):
        if hasattr(self, "listening_thread") and self.listening_thread and self.listening_thread.is_alive():
            print("⚠️ Already listening.")
            return

        print("▶️ Starting listening thread")
        if not is_android:
            self.listening_thread = threading.Thread(target=self.listen_loop_pc, daemon=True)
            self.listening_thread.start()
        else:
            self.listening_thread = threading.Thread(target=self.listen_loop_android, daemon=True)
            self.listening_thread.start()
    def listen_loop_android(self):
        """Handle continuous speech recognition in the background."""
        while self.is_listening:
            
            try:
                if stt.exist():
                    print("🎤 Listening...")
                    stt.start()  # Start listening for speech

                    while stt.listening:
                        Clock.sleep(0.1)  # Allow Kivy's UI to remain responsive

                    # Once listening is complete, retrieve the results
                    if stt.results:
                        recognized_text = stt.results[0]  # Get the first recognized phrase
                        print(f"🎤 Recognized: {recognized_text}")

                        # Process in background
                        self.is_listening = False  # Stop loop until processing finishes
                        Clock.schedule_once(lambda dt: self.animate_glow(False))
                        threading.Thread(
                            target=self.process_audio,
                            args=(recognized_text,"None"),
                            daemon=True
                        ).start()

            except Exception as e:
                print(f"❌ Error: {e}")
    
    def listen_loop_pc(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)

        while self.is_listening:
            try:
                with mic as source:
                    print("🎤 Listening...")
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)

                # Process in background
                self.is_listening = False  # Stop loop until TTS finishes
                Clock.schedule_once(lambda dt: self.animate_glow(False))
                threading.Thread(
                    target=self.process_audio,
                    args=(recognizer, audio),
                    daemon=True
                ).start()

            except Exception as e:
                print("❌ Mic Error:", e)
                self.is_listening = True

    def process_audio(self, recognizer, audio:None):
        try:
            if not is_android:
                result = recognizer.recognize_google(audio)
                print("🗣️ Recognized:", result)

                Clock.schedule_once(lambda dt: self.update_chat_ui(result))
            else:
                Clock.schedule_once(lambda dt: self.update_chat_ui(result))
            #self.run_tts_and_resume(result)

        except sr.UnknownValueError:
            print("❗ Could not understand audio.")
            self.resume_listening()
        except sr.RequestError:
            self.run_tts_and_resume("Network error.")
        except Exception as e:
            print("❌ Recognition Error:", e)
            self.resume_listening()

    def run_tts_and_resume(self, text):
        def task():
            with self.tts_lock:
                if not is_android:
                    print("🔊 Speaking:", text)
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                    self.is_listening=False
                    Clock.schedule_once(lambda dt: self.resume_listening(), 0)
                else:
                    tts.speak(text)
                    self.is_listening=False
                    Clock.schedule_once(lambda dt: self.resume_listening(), 0)
        # Restart listening
        # Clock.schedule_once(lambda dt: self.resume_listening())

        threading.Thread(target=task, daemon=True).start()

    def process_response_background(self, message):
        try:
            if "generate" in message:
                image_path = image_generator(message)
                Clock.schedule_once(lambda dt: self.show_image(image_path))
                
            else:
                # Get bot's response (simulate long processing)
                response = get_cbt_response(message,mode="imgery_cbt")
            
                # Update UI with bot response
                self.run_tts_and_resume(response)
                Clock.schedule_once(lambda dt: self.all_chat_response("chat_response", response), 0)
            

        except Exception as e:
            print("❌ Bot processing failed:", e)
            response = "Oops! Something went wrong."
            Clock.schedule_once(lambda dt: self.all_chat_response("chat_response", response), 0)

        finally:
            # Always hide loading and resume listening at the end
            Clock.schedule_once(lambda dt: self.hide_loading(), 0)
            

    def resume_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.animate_glow(True)
            self.start_listening()


    def update_chat_ui(self, message):
        # Show user message
        Clock.schedule_once(lambda dt: self.all_chat_response("chat_command", message), 0)

        # Stop listening and glowing mic animation
        self.is_listening = False
        Clock.schedule_once(lambda dt: self.animate_glow(False), 0)

        # Show loading spinner
        Clock.schedule_once(lambda dt: self.show_loading(), 0)

        # Run bot response in a new thread
        threading.Thread(target=self.process_response_background, args=(message,), daemon=True).start()


    def animate_glow(self, start=True):
        glow = self.ids.get("mic_glow")
        if glow:
            if start:
                self.glow_anim = Animation(size=(160, 160), duration=0.8) + Animation(size=(120, 120), duration=0.8)
                self.glow_anim.repeat = True
                self.glow_anim.start(glow)
            else:
                if self.glow_anim:
                    self.glow_anim.stop(glow)
                glow.size = (120, 120)


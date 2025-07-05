
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.properties import NumericProperty,StringProperty
from kivy.utils import get_color_from_hex
from kivymd.uix.snackbar import Snackbar
from utils.classes.database import get_database_path

from kivy.clock import Clock
import threading
from kivymd.uix.boxlayout import MDBoxLayout
from  kivymd.uix.spinner.spinner import MDSpinner
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
import os
import json
from kivy.app import App
from utils.gemini.gemini_ai import get_cbt_response
from utils.classes.database import show_cbt_form_data
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


class though_chat(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard_height=self.adjust_for_keyboard)
        # self.on_start()
    

    def handle_thought_session(self):
        base_dir = get_database_path()        
        file_path =  os.path.join(base_dir[2],"thought_cbt_conversation_log.json") 


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
            self.dialog.md_bg_color = get_color_from_hex("#513315")
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

        # Redirect to thought form screen
                
        #App.get_running_app().change_screen("though")
        app = App.get_running_app()
        app.change_screen("though")
        app.sm.get_screen("though").ids.thought_screen_manager.current = "thought_form"
        
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
                        Clock.schedule_once(self.make_lambda("chat_resume", message), delay)
                    elif role == "model":
                        Clock.schedule_once(self.make_lambda("chat_response", message), delay)

                    delay += 0.1
        except Exception as e:
            print(f"Error loading chat history: {e}")

    def make_lambda(self, role, msg):
        return lambda dt: self.all_chat_response(role, msg)




    def start_new_session(self, file_path):
        # Get form data
        form_data = show_cbt_form_data("thought")
        if form_data:
            prompt = f"""
    You are a compassionate CBT therapist helping someone process and reframe negative thoughts.

    Here's what the user shared with you:
    - Situation: {form_data["situation"]}
    - Worst Case: {form_data["worst_case"]}
    - Feelings: {form_data["feelings"]}
    - Thought: "{form_data["thoughts"]}"

    Begin the session like a real CBT therapist. First, validate the user's emotional experience and gently reflect what they shared.

    Then, guide the session with a set of Socratic questions to explore their negative thought. Ask 2–3 questions such as:
    - What makes you believe this thought is true?
    - Have you ever faced something similar before? How did you handle it?
    - Are there other possible ways to look at this situation?

    Avoid saying things like "Ask me anything." Instead, lead the conversation with empathy and curiosity. Keep your tone kind, thoughtful, and realistic — not robotic or overly cheerful.
            """

            response = get_cbt_response(prompt,"thought_cbt")
            Clock.schedule_once(lambda dt: self.all_chat_response("chat_response", response), 0)
        else:
            Snackbar(text="Please fill the form").open()
            app = App.get_running_app()
            app.change_screen("though")
            app.sm.get_screen("though").ids.thought_screen_manager.current = "thought_form"
            # App.get_running_app().change_screen("thought")
            return 
        
    def switch_screen(self, screen_name):
        """Switches the screen and updates chip colors."""
        self.ids.chat_screen_manager.current = screen_name
    def on_start(self):
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
            md_bg_color=(239/255, 217/255, 195/255),  # light background like a message
            radius=[20, 20, 20, 20],
            pos_hint={"right": 1},
        )

        self.loading_spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(20), dp(20)),
            active=True,
            color=(0.4, 0.26, 0.13, 1),
            pos_hint={"center_y": 0.5}
        )

        self.loading_label = MDLabel(
            text="Let me generate somthing",
            theme_text_color="Custom",
            text_color=(81/255, 51/255, 21/255),
            font_style="Caption",
            size_hint_y=None,
            height=dp(20),
            
        )

        self.loading_container.add_widget(self.loading_label)
        self.loading_container.add_widget(self.loading_spinner)
        

        self.ids.chat_list.add_widget(self.loading_container)

        # Scroll to bottom if needed
        Clock.schedule_once(lambda dt: setattr(self.ids.scroll_view, "scroll_y", 0))


    def hide_loading(self):
        """Removes the loading spinner from the chat layout."""
        if hasattr(self, "loading_container"):
            self.ids.chat_list.remove_widget(self.loading_container)
            del self.loading_container  # Remove reference

    def move_textfield_up(self):
        """Moves the text field up when the keyboard appears."""
        self.ids.chat_main.pos_hint = {"y": 0.2}  # Adjust as needed

    def move_textfield_down(self):
        """Moves the text field back down when the keyboard disappears."""
        self.ids.chat_main.pos_hint = {"y": 0}
    def adjust_for_keyboard(self, window, height):
        """Moves text field up when keyboard appears."""
        if height > 0:  # Keyboard is shown
            self.ids.chat_main.pos_hint = {"y": 0.3}  # Move up
        else:  # Keyboard is hidden
            self.ids.chat_main.pos_hint = {"y": 0}  # Move back to normal
    def send_chat(self):
        """Handles sending the message and scheduling bot response."""

        
        self.all_chat_response("chat_command")  # Show user message
        
        Clock.schedule_once(lambda dt: self.show_loading(), 0.01)
        thread = threading.Thread(target=self.fake_response, daemon=True)
        thread.start()  # Start bot response in background

    def all_chat_response(self, name, response=""):
        """Updates UI components safely using Kivy's main thread."""
        def update_ui(*args):


            if name == "chat_command":

                value = self.ids.text_input.text
                self.ids.text_input.text = "" 
                size = min(0.9, max(0.22, len(value) * 0.03))  
                
                self.ids.chat_list.add_widget(Command(text=value, size_hint_x=size, halign="center"))
            elif name == "chat_response":
              
                self.ids.chat_list.add_widget(Response(text=response))  
            elif name =="chat_resume":
                size = min(0.9, max(0.22, len(response) * 0.03))  
                self.ids.chat_list.add_widget(Command(text=response, size_hint_x=size, halign="center"))
        Clock.schedule_once(update_ui, 0)  # Ensure UI updates in main thread

    def fake_response(self):
        """Background function that only does processing (no UI changes here)."""

        value = self.ids.text_input.text.strip()
        print("value :", value)
        if not value:
            response = "Invalid input"
        elif value.lower() == "answer is not available in the context":
            self.select_category(self.category)
            response = "we change your book because your answer is not in this book "
       
           
        else:
            response = get_cbt_response(value,"thought_cbt")
        # Schedule UI update safely in main thread
        Clock.schedule_once(lambda dt: self.all_chat_response("chat_response", response), 0)
        Clock.schedule_once(lambda dt: self.hide_loading(), 0)
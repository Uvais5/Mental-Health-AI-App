from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from utils.classes.database import cbt_form_save_to_database
from kivymd.app import App
class imagery(Screen):
    def switch_screen(self, screen_name):
        self.ids.imgery_screen_manager.current = screen_name
    def show_dialog(self, title, message):
        """Display a dialog with a custom message."""
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda _: dialog.dismiss(),
                )
            ],
        )
        dialog.open()
    def process_form(self):
        """Process form data and save it to the database."""
        situation = self.ids.situation_input.text.strip()
        thoughts = self.ids.thoughts_input.text.strip()
        feelings = self.ids.feelings_input.text.strip()
        worst_case = self.ids.worst_case_input.text.strip()

        # Validate that all fields are filled
        if not situation or not thoughts or not feelings or not worst_case:
            self.show_dialog("Error", "Please fill out all fields before submitting.")
            return

        # Save data to the database
        cbt_form_save_to_database(input1=situation, input2=thoughts, input3=feelings, input4=worst_case,mode="imgery")
        self.show_dialog("Success", "Your responses have been successfully saved!")
        self.ids.situation_input.text = ""
        self.ids.thoughts_input.text = ""
        self.ids.feelings_input.text = ""
        self.ids.worst_case_input.text = ""
        try:
            App.get_running_app.change_screen("imagery")
        except Exception as e:
            print(e)
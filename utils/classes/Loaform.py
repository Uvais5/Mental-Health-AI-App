from utils.classes.database import save_loa_form_data
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
class loaform(Screen):
    def submit_data(self):
        """Function to store form data in a .txt file without timestamps"""
        # if not os.path.exists("data"):
        #         os.makedirs("data")
        try:
            goal = self.ids.input1.text.strip()
            important = self.ids.input2.text.strip()
            challenges = self.ids.input3.text.strip()
            positive_outcone = self.ids.input4.text.strip()
            action = self.ids.input5.text.strip()
            
            if goal and important and challenges and positive_outcone and action:  # Ensure fields are not empty
                data = f"Goal: {goal}\n challenges: {challenges}\n important:{important}\n positive_outcome:{positive_outcone}\n action:{action}"
                try:
                    save_loa_form_data(data)
                    print("loaform data is stored")
                except Exception as e:
                    print(f"loa form data is not stored : {e}")
                # Clear Input Fields After Submission
                self.ids.input1.text = ""
                self.ids.input2.text = ""
                self.ids.input3.text = ""
                self.ids.input4.text = ""
                self.ids.input5.text = ""
                self.manager.current = 'lawofattraction'
                # Show Confirmation

            else:
                self.ids.status_label.text = None
        except:
            self.snackbar = Snackbar(text="Please fill the all lines  !",snackbar_x="10dp",snackbar_y="10dp",size_hint_x=(Window.width - (dp(10) * 2)) / Window.width)
            self.snackbar.open()

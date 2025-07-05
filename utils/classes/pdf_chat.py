
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from plyer import filechooser
import threading
from kivymd.uix.boxlayout import MDBoxLayout
from  kivymd.uix.spinner.spinner import MDSpinner
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDIconButton
from kivy.uix.gridlayout import GridLayout
import pandas as pd
from kivymd.uix.snackbar import Snackbar
import io
import requests
import pandas as pd
from typing import Tuple

from utils.gemini.mutlipdf import get_response
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
 

class chat(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard_height=self.adjust_for_keyboard)
        self.dialog = None
        self.book_name = None
        self.book_url = None
        self.category = None
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.show_category_dialog(), 0)
        
    def show_category_dialog(self):
        if self.dialog:
            return

        scroll = MDScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            bar_width=0,
            size_hint=(1, None),
            height=dp(160)
        )

        layout = GridLayout(
            cols=len(self.get_categories()),
            spacing=dp(10),
            padding=[dp(10), dp(10)],
            size_hint_x=None,
            row_default_height=dp(140),
            height=dp(160),
        )
        layout.bind(minimum_width=layout.setter("width"))

        for icon, text in self.get_categories():
            card = MDCard(
                orientation="vertical",
                size_hint=(None, None),
                size=(dp(120), dp(120)),
                ripple_behavior=True,
                md_bg_color=(1, 1, 1, 1),
                elevation=4,
                padding=dp(10),
                on_release=lambda x, t=text: self.select_category(t),
                
            )
            card.add_widget(MDIconButton(icon=icon, icon_size=dp(36),on_release = lambda x, t=text: self.select_category(t)))
            card.add_widget(MDLabel(text=text, halign="center"))
            layout.add_widget(card)

        scroll.add_widget(layout)

        # Fixed content layout height
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None,
            height=dp(180)
        )

        help_text = MDLabel(
            text="\nChoose a category based on what your question is about.",
            halign="left",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20),
            font_style="Caption"
        )

        content.add_widget(help_text)
        content.add_widget(scroll)

        self.dialog = MDDialog(
            title="Choose a Category",
            type="custom",
            content_cls=content,
            size_hint_y=None,
            height=dp(280)  # Prevent shrinkage
        )
        self.dialog.open()

    def get_categories(self):
        return [
                ("help-circle-outline", "help"),
                ("brain", "Psychology"),
                ("emoticon-sad-outline", "Depression"),
                ("emoticon-neutral-outline", "Anxiety"),
                ("cash-multiple", "Finance"),
                ("lightbulb-on-outline", "Life Lessons"),
                ("arrow-up-bold-circle-outline", "Self-Improvement"),
                ("rocket-launch-outline", "Motivation"),
                ("progress-check", "Productivity"),
                ("bandage", "Trauma"),
                ("yin-yang", "Philosophy"),
                ("brain", "Neuroscience"),
                ("meditation", "Spirituality"),
                ("heart-broken-outline", "Love/Breakup"),
                ("heart-plus-outline", "Healing/Grief"),
                ("repeat", "Habit Building"),
                ("account-star-outline", "Confidence/Self-Esteem"),
                ("head-heart-outline", "Emotional Intelligence"),
                ("gesture-double-tap", "Forgiveness"),
                ("account-group-outline", "Relationships"),
                ("school", "Research"),
                ("file-upload", "add_pdf"),
                
        ]

    def select_category(self, category):
        print("Selected:", category)
        
    
        if category == "help":
            self.switch_screen("overview")
        elif category == "add_pdf":
            self.add_pdf()
        else:
            self.book_name = self.get_books_with_urls(category)[0]
            self.book_url = self.get_books_with_urls(category)[1]
            self.category = category

            # self.snackbar = Snackbar(text=f"the book : {self.book_name}",snackbar_x="10dp",snackbar_y="30dp",size_hint_x=(Window.width - (dp(10) * 2)) / Window.width)
            # #self.snackbar.ids.chat_list.text_size = (self.snackbar.width - dp(20), None)
            # self.snackbar.open()
        try:
            self.dialog.dismiss()
            self.dialog = None
        except:
            self.snackbar = Snackbar(text=f"somthing went wrong ",snackbar_x="10dp",snackbar_y="30dp",size_hint_x=(Window.width - (dp(10) * 2)) / Window.width)
            #self.snackbar.ids.chat_list.text_size = (self.snackbar.width - dp(20), None)
            self.snackbar.open()
    
        new_label = MDLabel(
            text=f"{self.book_name} | {category}",
            markup=True,
            halign="center",
            size_hint_y=None,
            font_style = "Caption",
            height=dp(40)
        )

        # Clear previous labels (optional)
        self.ids.book_layout.clear_widgets()

        # Add the new label
        self.ids.book_layout.add_widget(new_label)
        self.ids.book_layout.add_widget(MDIconButton(icon="reload", icon_size=dp(20),on_release = lambda x, t=self.category: self.select_category(t)))



    def add_pdf(self):
        """Opens the file manager to select a PDF file."""
        print("Opening file manager...")
        
        # Open file chooser and filter for PDFs only
        filechooser.open_file(
            filters=[("PDF Files", "*.pdf")], 
            on_selection=self.select_pdf
        )

    def select_pdf(self, selection):
        """Handles the selected PDF file path."""
        if selection:
            pdf_path = selection[0]
            print(f"Selected PDF Path: {pdf_path}")
        else:
            print("No file selected.")
    def switch_screen(self, screen_name):
        """Switches the screen and updates chip colors."""
        self.ids.chat_screen_manager.current = screen_name

    

    
    # def get_books_with_urls(self,selected_genre):
    #     df = pd.read_csv("C:/Machine Learning/Emotion_app/kivy/books_with_urls.csv")
    #     # Filter and shuffle books from that genre
    #     shuffled_books = df[df["Category"] == selected_genre].sample(frac=1).reset_index(drop=True)
 
    #     return shuffled_books["Book Name"][0],shuffled_books["URL"][0]

    def get_books_with_urls(self,selected_genre: str) -> Tuple[str, str]:
        """
        Return a random (book_title, book_url) pair for the requested genre.

        Parameters
        ----------
        selected_genre : str
            The category name as it appears in the CSV’s “Category” column.

        Raises
        ------
        ValueError
            If no rows match the requested genre.
        requests.HTTPError
            If the CSV cannot be downloaded.
        """
        # Raw‑file link (⬅️ note the use of raw.githubusercontent.com, not github.com/blob)
        raw_csv = (
            "https://raw.githubusercontent.com/"
            "Uvais5/Mental-Health-AI-App/master/data/books_with_urls.csv"
        )

        # Grab the file (this avoids pandas mistakenly loading the HTML page)
        csv_text = requests.get(raw_csv, timeout=10)
        csv_text.raise_for_status()        # ↳ bubble up HTTP problems

        # Read into DataFrame
        df = pd.read_csv(io.StringIO(csv_text.text))

        # Case‑insensitive match on category
        genre_df = df[df["Category"].str.lower() == selected_genre.lower()]

        if genre_df.empty:
            raise ValueError(f"No books found for genre: {selected_genre!r}")

        # Pick one row at random and unpack the two fields we need
        row = genre_df.sample(1).iloc[0]
        return row["Book Name"], row["URL"]

    

    
    def show_loading(self):
        """Adds the loading spinner to the chat layout."""
        if not hasattr(self, "loading_container"):  # Ensure it's not added multiple times
            self.loading_container = MDBoxLayout(
                size_hint_y=None,
                height=dp(50),
                orientation="vertical",
                pos_hint={"center_x": 0.5, "top": 0.5},
                opacity=1  # Show the widget
            )

            self.loading_label = MDLabel(
                text="Generating...",
                halign="center",
                font_style="Caption",
                theme_text_color="Secondary"
            )

            self.loading_spinner = MDSpinner(
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                active=True,  # Start spinner
                pos_hint={"center_x": 0.5}
            )

            # Add widgets to loading container
            self.loading_container.add_widget(self.loading_label)
            self.loading_container.add_widget(self.loading_spinner)

            # Add loading container to the main chat layout
            self.ids.chat_list.add_widget(self.loading_container)

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
        self.show_loading()
        thread = threading.Thread(target=self.fake_response, daemon=True)
        thread.start()  # Start bot response in background

    def all_chat_response(self, name, response=""):
        """Updates UI components safely using Kivy's main thread."""
        def update_ui(*args):
            #chat_screen = screen_manager.get_screen('chat')

            if name == "chat_command":
                value = self.ids.text_input.text
                self.ids.text_input.text = ""  # Clear input field in UI thread
                size = min(0.9, max(0.22, len(value) * 0.03))  
                
                self.ids.chat_list.add_widget(Command(text=value, size_hint_x=size, halign="center"))
            elif name == "chat_response":
              
                self.ids.chat_list.add_widget(Response(text=response))  
        
        Clock.schedule_once(update_ui, 0)  # Ensure UI updates in main thread

    def fake_response(self):
        """Background function that only does processing (no UI changes here)."""
        #chat_screen = screen_manager.get_screen('chat')
        value = self.ids.text_input.text.strip()

        if not value:
            response = "Invalid input"
        elif value.lower() == "answer is not available in the context":
            # self.book_name = self.get_books_with_urls(self.category)[0]
            # self.book_url = self.get_books_with_urls(self.category)[1]
            self.select_category(self.category)
            response = "we change your book because your answer is not in this book "
       
           
        else:
            
            response = get_response(f"{value}first analysis this context and gave me answer accourding to you",self.book_url)
        print(self.book_name)
        print(self.book_url)
        # Schedule UI update safely in main thread
        Clock.schedule_once(lambda dt: self.all_chat_response("chat_response", response), 0)
        Clock.schedule_once(lambda dt: self.hide_loading(), 0)



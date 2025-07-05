
from utils.classes.database import get_database_path
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.taptargetview import MDTapTargetView
from kivymd.uix.filemanager import MDFileManager
import sqlite3
import datetime
from kivy.uix.image import Image
from kivymd.theming import ThemeManager
from kivy.metrics import dp
import shutil
from kivy.utils import platform
from kivy.app import App
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from wordcloud import WordCloud
from kivy_garden.matplotlib import FigureCanvasKivyAgg

from utils.classes.customdate import CustomCalendar
from kivy.uix.screenmanager import ScreenManager,Screen
  # Keep it centered
class journal_affirmation(Screen):
    def __init__(self, **kwargs):
        super(journal_affirmation, self).__init__(**kwargs)
        self.tap_target_view = None
        self.final_mood = None
        self.tap_target_view2 = None
        self.init_db()
    def switch_screen(self, screen_name):
        """Switches the screen and updates chip colors."""
        self.ids.journal_screen_manager.current = screen_name
    
    def select_mood(self, instance, selected_mood,num):

        # Reset all buttons to "unselected" outline icons
        if num == "1":
            moods = {
                "Angry": "emoticon-angry-outline",
                "Sad": "emoticon-sad-outline",
                "Happy": "emoticon-happy-outline",
                "Excited": "emoticon-excited-outline"
            }
            for mood, icon in moods.items():
                self.ids[mood].icon = icon  # Reset all icons

            # Set selected button to filled icon
            filled_icons = {
                "Angry": "emoticon-angry",
                "Sad": "emoticon-sad",
                "Happy": "emoticon-happy",
                "Excited": "emoticon-excited"
            }
            instance.icon = filled_icons[selected_mood] 
            self.insert_today_mood(mode="after",mood=selected_mood) 
            print(f"Selected Mood: {selected_mood}")
        else:
            
            moods = {
                "Angry1": "emoticon-angry-outline",
                "Sad1": "emoticon-sad-outline",
                "Happy1": "emoticon-happy-outline",
                "Excited1": "emoticon-excited-outline"
            }
            for mood, icon in moods.items():
                self.ids[mood].icon = icon  # Reset all icons

            # Set selected button to filled icon
            filled_icons = {
                "Angry1": "emoticon-angry",
                "Sad1": "emoticon-sad",
                "Happy1": "emoticon-happy",
                "Excited1": "emoticon-excited"
            }
            instance.icon = filled_icons[selected_mood]  # Change to selected icon
            print(f"Selected Mood: {selected_mood}")
            self.insert_today_mood(mode="pre",mood=selected_mood.replace("1",""))
        
        self.final_mood = selected_mood
        print("final mood",self.final_mood)
    def init_db(self):
        """Initialize the database."""
        
        self.conn = sqlite3.connect(get_database_path()[0])
        self.cursor = self.conn.cursor()
        
        # # Create journal table
        # self.cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS journal (
        #         date TEXT PRIMARY KEY,
        #         pre_journal TEXT,
        #         after_journal TEXT
        #     )
        # """)
        
        # # Create photos table (to allow multiple photos per date)
        # self.cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS photos (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         date TEXT,
        #         photo_path TEXT,
        #         FOREIGN KEY (date) REFERENCES journal (date)
        #     )
        # """)
        # self.cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS mood (
        #         date TEXT UNIQUE,
        #         pre_mood TEXT,
        #         after_mood TEXT
        #     )
        # """)
        self.conn.commit()

    def show_calendar(self):
        """Open the date picker and show journal details."""
        picker = CustomCalendar(callback=self.on_date_selected)
        picker.open()
    def on_device_orientation(self, instance_theme_manager: ThemeManager, orientation_value: str):
        """ Handles changes in device orientation. """
        if hasattr(self, 'date_dialog') and self.date_dialog:
            self.adjust_date_picker_size()
    def on_date_selected(self, date):
        """Fetch and display journal details for the selected date."""
        date_str = date.strftime("%Y-%m-%d")
        print("date_str : ",date_str)
        self.display_journal_details(date_str)

    def display_journal_details(self, date_str):
        """Fetch and display journal details (journal text and multiple photos)."""
        self.cursor.execute("SELECT pre_journal, after_journal FROM journal WHERE date = ?", (date_str,))
        journal_result = self.cursor.fetchone()

        if journal_result:
            print(f"Journal Found: {journal_result}")
            self.ids.pre_journal_text.text = journal_result[0] if journal_result[0] else ""
            self.ids.after_journal_text.text = journal_result[1] if journal_result[1] else ""
            self.adjust_journal_display()
        else:
            print("No journal found for this date.")
            self.ids.pre_journal_text.text = ""
            self.ids.after_journal_text.text = ""
            self.adjust_journal_display()
        # Fetch all photos for the selected date
        self.cursor.execute("SELECT photo_path FROM photos WHERE date = ?", (date_str,))
        photo_results = self.cursor.fetchall()
        self.ids.photos_layout.clear_widgets()

        for photo in photo_results:
            img = Image(source=photo[0], size_hint_y=None, height=200)
            self.ids.photos_layout.add_widget(img)

    def file_manager_open(self):
        """Open KivyMD File Manager."""
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.save_photo,
        )
        self.file_manager.show('/')  

    def exit_file_manager(self, *args):
        """Close KivyMD File Manager."""
        self.file_manager.close()

    def save_photo1(self, image_path):
        """Save the selected photo and store its path in the database."""
        if not image_path:
            return

        photo_name = os.path.basename(image_path)

        # Ensure "photos" folder is created
        save_directory = os.path.join(os.getcwd(), "photos")
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Copy photo to "photos" folder
        new_photo_path = os.path.join(save_directory, photo_name)
        shutil.copy(image_path, new_photo_path)

        # Get current date
        date_str = datetime.date.today().strftime("%Y-%m-%d")

        # Save photo to database
        self.cursor.execute("INSERT INTO photos (date, photo_path) VALUES (?, ?)", (date_str, new_photo_path))
        self.conn.commit()

        self.ids.photos_layout.add_widget(Image(source=new_photo_path, size_hint_y=None, height=200))
        self.exit_file_manager()

    
    def save_photo(self, image_path):
        """Save the selected photo and store its path in the database."""
        if not image_path:
            print("⚠️ No image selected!")
            return

        photo_name = os.path.basename(image_path)

        # ✅ Check if platform is Android or PC
        if platform == "android":
            # Use Android writable directory
            data_dir = App.get_running_app().user_data_dir
            save_directory = os.path.join(data_dir, "utils", "photos")

        else:
            # Use PC directory
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            save_directory = os.path.join(base_dir, "photos")

        # ✅ Ensure "photos" directory exists
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
            print(f"✅ Created photo directory at: {save_directory}")

        # ✅ Copy photo to "photos" folder
        new_photo_path = os.path.join(save_directory, photo_name)
        shutil.copy(image_path, new_photo_path)
        print(f"✅ Photo saved to: {new_photo_path}")

        # ✅ Get current date
        date_str = datetime.date.today().strftime("%Y-%m-%d")

        # ✅ Save photo path to database
        self.cursor.execute(
            "INSERT INTO photos (date, photo_path) VALUES (?, ?)",
            (date_str, new_photo_path)
        )
        self.conn.commit()
        print(f"✅ Photo path added to database for date: {date_str}")

        # ✅ Add photo to layout dynamically
        self.ids.photos_layout.add_widget(
            Image(source=new_photo_path, size_hint_y=None, height=200)
        )
        self.exit_file_manager()

    def save_journal(self, mode):
        """Save either the pre-journal (morning) or the after-journal (night) into the database, ensuring updates work properly."""
        date_str = datetime.date.today().strftime("%Y-%m-%d")

        if mode == "pre":
            pre_journal_text1 = self.ids.pre_text_input1.text.strip()
            pre_journal_text2 = self.ids.pre_text_input2.text.strip()
            pre_journal_text3 = self.ids.pre_text_input3.text.strip()
            pre_journal_text4 = self.ids.pre_text_input4.text.strip()
            pre_journal_text5 = self.ids.pre_text_input5.text.strip()
            pre_journal_text6 = self.ids.pre_text_input6.text.strip()
            pre_journal_text7 = self.ids.pre_text_input7.text.strip()
            pre_journal_text8 = self.ids.pre_text_input8.text.strip()
            pre_journal_text9 = self.ids.pre_text_input9.text.strip()
            pre_journal_text10 = self.ids.pre_text_input10.text.strip()
            pre_journal_text11 = self.ids.pre_text_input11.text.strip()
            if pre_journal_text1 is None:
                Snackbar(text="please fill the first question atleast",snackbar_x="10dp",snackbar_y="10dp",size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
            else:
                if self.final_mood is None:
                    Snackbar(text="please select the mood",snackbar_x="10dp",snackbar_y="10dp",size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
                else:
                    pre_journal_text = f"""1. What is your main goal for today?\n response: {pre_journal_text1}
                                        \n\n2. What small steps will you take to achieve it?\n response: {pre_journal_text2}
                                        \n\n3. How do you want to feel today? (Excited, Focused, Peaceful, etc.)\n response: {pre_journal_text3}
                                        \n\n4. What affirmation or positive thought will guide your day?\n response: {pre_journal_text4}
                                        \n\n5. What challenges might come up, and how will you handle them?\n response: {pre_journal_text5}
                                        \n\n6. What is something you are grateful for this morning?\n response: {pre_journal_text6}
                                        \n\n7. What is something you are excited about today?\n response: {pre_journal_text7}
                                        \n\n8. What song, book, or quote will inspire you today?\n response: {pre_journal_text8}
                                        \n\n9. How can you step out of your comfort zone today?\n response: {pre_journal_text9}
                                        \n\n10. What habit or mindset do you want to improve today?\n response: {pre_journal_text10}
                                        \n\n11. How will you make today better than yesterday?\n response: {pre_journal_text11}\n\n Your Mood {self.final_mood}"""

                    print(f"Saving Pre-Journal for {date_str}: {pre_journal_text}")

                self.cursor.execute("""
                    INSERT INTO journal (date, pre_journal, after_journal)
                    VALUES (?, ?, ?)
                    ON CONFLICT(date) DO UPDATE SET pre_journal = excluded.pre_journal
                """, (date_str, pre_journal_text, None))

        elif mode == "after":
            after_journal_text1 = self.ids.after_text_input1.text.strip()
            after_journal_text2 = self.ids.after_text_input2.text.strip()
            after_journal_text3 = self.ids.after_text_input3.text.strip()
            after_journal_text4 = self.ids.after_text_input4.text.strip()
            after_journal_text5 = self.ids.after_text_input5.text.strip()
            after_journal_text6 = self.ids.after_text_input6.text.strip()
            after_journal_text7 = self.ids.after_text_input7.text.strip()
            after_journal_text8 = self.ids.after_text_input8.text.strip()
            after_journal_text9 = self.ids.after_text_input9.text.strip()
            after_journal_text10 = self.ids.after_text_input10.text.strip()
            after_journal_text11 = self.ids.after_text_input11.text.strip()
            after_journal_text12 = self.ids.after_text_input12.text.strip()
            after_journal_text13 = self.ids.after_text_input13.text.strip()
            if pre_journal_text1 is None:
                Snackbar(text="please fill the first question atleast",snackbar_x="10dp",snackbar_y="10dp",size_hint_x=(Window.width - (dp(10) * 2)) / Window.width).open()
            else:

                after_journal_text = f"""1. Did you complete your main goal for today? (Yes/No – If not, why?)\n response: {after_journal_text1}
                                        \n\n2. What small steps did you successfully  complete?\n response: {after_journal_text2}
                                        \n\n3. What obstacles did you face, and how did you handle them?\n response: {after_journal_text3}
                                        \n\n4. What was the most unexpected thing that happened today?\n response: {after_journal_text4}
                                        \n\n5. Rate your energy levels at the end of the day (1-10)\n response: {after_journal_text5}
                                        \n\n6. What specific event or action had the biggest impact on your mood today?\n response: {after_journal_text6}
                                        \n\n7. What habits or routines helped you maintain positive energy today?\n response: {after_journal_text7}
                                        \n\n8. What was the biggest lesson you learned today?\n response: {after_journal_text8}
                                        \n\n9. If you could redo one thing, what would it be?\n response: {after_journal_text9}
                                        \n\n10. How can you improve your\n approach for tomorrow?\n response: {after_journal_text10}
                                        \n\n11. What was the best part of your day?\n response: {after_journal_text11}
                                        \n\n12. What are you grateful for right now?\n response: {after_journal_text12}
                                        \n\n13. End your day with an affirmation \n for tomorrow 'Tomorrow, I will..\n response: {after_journal_text13}\n\n Your Mood: {self.final_mood}"""

                print(f"Saving After-Journal for {date_str}: {after_journal_text}")

                self.cursor.execute("""
                    INSERT INTO journal (date, pre_journal, after_journal)
                    VALUES (?, ?, ?)
                    ON CONFLICT(date) DO UPDATE SET after_journal = excluded.after_journal
                """, (date_str, None, after_journal_text))

        else:
            print("Invalid mode. Use 'pre' for morning journal and 'after' for night journal.")
            return

        self.conn.commit()
        print(f"Journal ({mode}) saved/updated successfully!")


    def adjust_journal_display(self):
        journal_label = self.ids.pre_journal_text
        box_layout = self.ids.dis_pre

        # Update texture to get the correct size
        journal_label.texture_update()

        # Adjust label height to fit text
        journal_label.height = journal_label.texture_size[1]

        # Ensure MDBoxLayout fits content
        box_layout.height = journal_label.height + dp(20)
          
        journal_label1 = self.ids.after_journal_text
        box_layout1 = self.ids.dis_after

        # Update texture to get the correct size
        journal_label1.texture_update()

        # Adjust label height to fit text
        journal_label1.height = journal_label1.texture_size[1]

        # Ensure MDBoxLayout fits content
        box_layout1.height = journal_label1.height + dp(20)  # Add padding


    def insert_today_mood(self, mode, mood):
        """
        Insert or update today's mood based on mode.
        Mode can be:
        - 'pre': Insert/Update pre-mood for the morning.
        - 'after': Update after-mood for the night.
        """
        today = datetime.date.today().strftime("%Y-%m-%d")

        if mode == "pre":
            pre_mood = mood  # Simulated pre-mood
            after_mood = None  # No after mood in the morning

            # Check if today's mood entry already exists
            self.cursor.execute("SELECT * FROM mood WHERE date = ?", (today,))
            existing_entry = self.cursor.fetchone()

            if existing_entry:
                # If already exists, update only pre-mood if not filled
                if not existing_entry[1]:  # Check if pre_mood is empty
                    self.cursor.execute("""
                        UPDATE mood SET pre_mood = ? WHERE date = ?
                    """, (pre_mood, today))
            else:
                # Insert new entry if no entry exists for today
                self.cursor.execute("""
                    INSERT INTO mood (date, pre_mood, after_mood) VALUES (?, ?, ?)
                """, (today, pre_mood, after_mood))

        elif mode == "after":
            after_mood = mood  # Simulated after-mood

            # Check if today's mood entry exists
            self.cursor.execute("SELECT * FROM mood WHERE date = ?", (today,))
            existing_entry = self.cursor.fetchone()

            if existing_entry:
                # Update after-mood for today
                self.cursor.execute("""
                    UPDATE mood SET after_mood = ? WHERE date = ?
                """, (after_mood, today))
            else:
                # If pre-mood was not added, add new entry with after-mood
                self.cursor.execute("""
                    INSERT INTO mood (date, pre_mood, after_mood) VALUES (?, ?, ?)
                """, (today, None, after_mood))

        else:
            print("Invalid mode. Use 'pre' or 'after'!")
            return

        self.conn.commit()

    def get_mood_data(self):
        """Fetch mood data from the mood table"""
        self.cursor.execute("SELECT date, pre_mood, after_mood FROM mood ORDER BY date ASC")
        return self.cursor.fetchall()
    
    def display_mood_chart(self):
        MOOD_CATEGORIES = [ "Sad", "Angry", "Happy", "Excited"]
        MOOD_MAPPING = {mood: i for i, mood in enumerate(MOOD_CATEGORIES)}
        data = self.get_mood_data()
        if not data:
            print("No mood data found!")
            return

        # Extract actual data from the database
        dates, pre_moods, after_moods = zip(*data)
        dates = [datetime.datetime.strptime(d, "%Y-%m-%d") for d in dates]  # Correct date format
        pre_mood_values = [MOOD_MAPPING.get(mood, None) for mood in pre_moods]  # Convert moods to numeric values
        after_mood_values = [MOOD_MAPPING.get(mood, None) for mood in after_moods]

        # Create figure
        fig, ax = plt.subplots(figsize=(4, 5))  # Set chart dimensions (phone size)
        ax.plot(dates, pre_mood_values, marker="o", linestyle="-", color="blue", label="Pre Mood (Morning)")
        ax.plot(dates, after_mood_values, marker="o", linestyle="-", color="red", label="After Mood (Night)")

        # Set y-axis labels with mood categories
        ax.set_yticks(list(MOOD_MAPPING.values()))
        ax.set_yticklabels(MOOD_CATEGORIES)

        # Set title and labels
        ax.set_title("Mood Progress Before & After Journaling")
        ax.set_xlabel("Date")
        ax.set_ylabel("Mood Level")
        ax.legend()

        # Show only recorded dates
        ax.set_xticks(dates)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))  # Format dates
        plt.xticks(rotation=45)

        # Remove old chart and add new one with size_hint_y = 0.5
        root = self.ids.chart_container
        root.clear_widgets()

        chart_box = BoxLayout(size_hint_y=0.5)
        chart_box.add_widget(FigureCanvasKivyAgg(fig))
        root.add_widget(chart_box)

    def get_journal_text(self):
        """Fetch all journal text from the journal table in journal.db"""
        self.cursor.execute("SELECT pre_journal, after_journal FROM journal")  # Corrected to journal table
        data = self.cursor.fetchall()
        text_data = " ".join([f"{pre} {after}" for pre, after in data if pre or after])
        return text_data.replace("response"," ")

    def display_word_cloud(self):
        """Generate and display a word cloud from journal data"""
        journal_text = self.get_journal_text()
        if not journal_text.strip():
            print("No journal data available for word cloud!")
            return

        # Generate word cloud
        wordcloud = WordCloud(width=800, height=400, background_color="white", colormap="viridis").generate(journal_text)

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 8))  # Word cloud in phone size
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        ax.set_title("Most Used Words in Journals")

        # Remove old word cloud and add new one
        root = self.ids.wordcloud_container
        root.clear_widgets()

        wordcloud_box = BoxLayout(size_hint_y=0.5)
        wordcloud_box.add_widget(FigureCanvasKivyAgg(fig))
        root.add_widget(wordcloud_box)

   
    
    def toggle_tap_target(self,num):
        """
        Toggles the MDTapTargetView (open/close).
        """
        if num == "1":
            if not self.tap_target_view:
                # Create MDTapTargetView if it doesn't exist
                self.tap_target_view = MDTapTargetView(
                    widget=self.ids.button,
                    title_text="Journal Affirmation",
                    title_text_size="30sp",
                    description_text=(
                        "Journal affirmations are positive statements \n"
                        "that you write down in your journal regularly \n"
                        "to reinforce positive beliefs, cultivate self-esteem,\n"
                        "Think of them as a way to have a conversation with\n"
                        "yourself on paper, focusing on what you want to be,\n"
                        " feel, or achieve. Instead of dwelling on negative \n"
                        "thoughts or limitations, journal affirmations."
                        
                    ),
                    description_text_size="10sp",
                    widget_position="top",
                )
                # Bind the on_close event to reset state
                self.tap_target_view.outer_circle_color = (99/255, 108/255, 166/255)
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
                    title_text="Positive Thoughts",
                    title_text_size="20sp",
                    description_text=(
                        "The Law of Attraction (LOA) is a philosophical\n principle stating that like attracts like.\n This means that the energy you put out into\n the universe  through your thoughts,\n feelings, and beliefs will attract back\n to you experiences and circumstances of\n a similar energy."
                        
                        
                    ),
                    description_text_size="10sp",
                    widget_position="top",
                )
                # Bind the on_close event to reset state
                self.tap_target_view2.bind(on_close=self.reset_tap_target)
                self.tap_target_view2.outer_circle_color = (99/255, 108/255, 166/255)
            # Toggle based on current state
            if self.tap_target_view2.state == "close":
                self.tap_target_view2.start()
            else:
                self.tap_target_view2.stop()

    def reset_tap_target(self, *args):
        """
        Resets the state of MDTapTargetView when closed.
        """
        self.tap_target_view.state = "close"
   
    


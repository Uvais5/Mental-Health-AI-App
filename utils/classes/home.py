import threading
import sqlite3

from kivy.uix.screenmanager import Screen
from utils.image_gen.img_gen import image_generator
from threading import Thread

from kivy.clock import Clock
from kivy.animation import Animation
from utils.classes.database import get_database_path
import os
import requests
class HomeScreen(Screen):
   
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auto_scroll_event = None  # Only one clock ref
        self.scroll_pos = 0.0
        self.quotesoftheday = None
        self.data_path = get_database_path()[0]
        self.load_existing_data()
        self.start_auto_scroll()
    
         
    def start_auto_scroll(self):
        # Schedule auto scroll every dt seconds (e.g., 1 second)
        if not self.auto_scroll_event:
            self.auto_scroll_event = Clock.schedule_interval(self.auto_scroll_smooth, 3)
    def stop_auto_scroll(self):
        
        if self.auto_scroll_event:
            print("🛑 Stopping auto scroll")
            self.auto_scroll_event.cancel()
            self.auto_scroll_event = None
    # def on_text_change(self, instance, value):
    #     print("ontext working")
    #     self.stop_auto_scroll()
    #     conn = sqlite3.connect(self.data_path)
    #     c = conn.cursor()
    #     c.execute("SELECT priority FROM textfeild WHERE id = 1")
    #     result = c.fetchone()
    #     old_acceptance = result if result else ("", "")

    #     # Update only changed field
    #     priority_text = self.ids.priority.text.strip() or old_acceptance

    #     # Save new values
    #     c.execute("UPDATE textfeild SET priority = ? WHERE id = 1", (priority_text,))
    #     conn.commit()
    #     conn.close()
    def on_text_change(self, instance, value):
        print("working")
        self.stop_auto_scroll()
        conn = sqlite3.connect(self.data_path)
        c = conn.cursor()

        # Load old value safely
        c.execute("SELECT priority FROM textfeild WHERE id = 1")
        result = c.fetchone()
        old_dare = result[0] if result else ""

        # Get new value from TextField
        new_dare = self.ids.priority.text.strip() or old_dare

        # If it's empty, keep the old value
        if not new_dare:
            new_dare = old_dare

        # Save new value (always a string now)
        c.execute("UPDATE textfeild SET priority=? WHERE id = 1", (new_dare,))
        conn.commit()
        conn.close()

    def load_existing_data(self):
        conn = sqlite3.connect(self.data_path)
        c = conn.cursor()
        c.execute("SELECT  priority FROM textfeild WHERE id = 1")
        result = c.fetchone()
        if result:
            self.ids.priority.text = result[0]
            try:
                cc = conn.cursor()
                cc.execute("SELECT  gen_image FROM textfeild WHERE id = 2")
                result1 = cc.fetchone()
                print("this is image path : ",result1)
                self.ids.goal_image.source = result1[0]
                print("image statues : ",os.path.isfile(result1[0]))
                image_exist_st = os.path.isfile(result1[0])
                if image_exist_st == False:
                    self.ids.goal_image.source = "https://i.pinimg.com/736x/62/5a/91/625a91c138093648b57878efdba7861e.jpg"     
            except:
                self.ids.goal_image.source = "https://i.pinimg.com/736x/62/5a/91/625a91c138093648b57878efdba7861e.jpg"
            
        conn.close()

    def auto_scroll_smooth(self, dt):
        scrollview = self.ids.auto_scroll_view

        # Stop if there's no scrollable content
        if scrollview.scroll_x >= 1.0:
            self.scroll_pos = 0.0
        else:
            self.scroll_pos += 0.33  # Adjust scroll step as needed

        if self.scroll_pos > 1:
            self.scroll_pos = 0

        # Animate the scroll instead of jumping
        anim = Animation(scroll_x=self.scroll_pos, duration=1, t='out_quad')
        anim.start(scrollview)


    def on_start_quotes(self):
        print("HomeScreen API fetch function of quotes is working")
    
        # Start background thread
        threading.Thread(target=self.fetch_quote_background, daemon=True).start()

    def fetch_quote_background(self):
        quote = None

        if self.quotesoftheday is None:
            try:
                url = "https://api.quotable.io/random?"
                response = requests.get(url, verify=False, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    quote = f'"{data["content"]}"\n- {data["author"]}'
            except Exception:
                try:
                    response = requests.get("https://api.adviceslip.com/advice", verify=False, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        quote = data["slip"]["advice"]
                except Exception as e:
                    print("❌ Error fetching fallback quote:", e)

        # Save and update UI on the main thread
        if quote:
            self.quotesoftheday = quote
            Clock.schedule_once(lambda dt: self.update_quote_label())

    def update_quote_label(self):
        self.ids.quote_of_the_day.text = self.quotesoftheday
    def process_response_background(self):
        try:
            img_text = self.ids.text_input.text.strip()
            self.ids.spinner.active = True
            Thread(target=self.generate_image_thread, args=(img_text,), daemon=True).start()
        except Exception as e:
            print("❌ Bot processing failed:", e)

    def generate_image_thread(self, img_text):
        try:
            # Heavy image generation task
            image_path = image_generator(img_text)
            
            # Once done, update the UI on the main thread
            Clock.schedule_once(lambda dt: self.update_image_ui(image_path), 0)
        except Exception as e:
            print("❌ Error in image generation thread:", e)

    def update_image_ui(self, image_path):
        conn = sqlite3.connect(self.data_path)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO textfeild (gen_image) VALUES ('')")
        c.execute("UPDATE textfeild SET  gen_image = ? WHERE id = 2", (image_path,))
        conn.commit()
        conn.close()
        self.ids.spinner.active = False
        self.ids.goal_image.source = image_path
        self.ids.text_input.text = ""
        self.ids.goal_image.reload()  # Ensure the image updates if already set

from kivy.uix.screenmanager import ScreenManager,Screen
import sqlite3
from utils.image_gen.img_gen import image_generator 
from utils.classes.database import get_database_path
from kivy.clock import Clock
from threading import Thread
from kivy.utils import platform
class Afterlove(Screen):
    def on_kv_post(self, base_widget):
       # self.init_db()
        self.data_path = get_database_path()[0]
        # Auto-save whenever user types
        self.ids.acceptance.bind(text=self.on_text_change)
        self.ids.learned.bind(text=self.on_text_change)

    def on_pre_enter(self):
        # Load data when screen is entered (notepad behavior)
        self.load_existing_data()

    

    def load_existing_data(self):
        conn = sqlite3.connect(self.data_path)
        c = conn.cursor()
        c.execute("SELECT acceptance, learned, gen_image FROM textfeild WHERE id = 1")
        result = c.fetchone()
        if result:
            self.ids.acceptance.text = result[0]
            self.ids.learned.text = result[1]
            try:
                self.ids.futureimg.source = result[2]
            except:
                self.ids.futureimg.source = "https://i.pinimg.com/736x/a5/0e/e1/a50ee15e59dd5809e80975c5f35609cd.jpg"
        conn.close()

    def on_text_change(self, instance, value):
        # Load old values
        conn = sqlite3.connect(self.data_path)
        c = conn.cursor()
        c.execute("SELECT acceptance, learned  FROM textfeild WHERE id = 1")
        result = c.fetchone()
        old_acceptance, old_learned = result if result else ("", "")

        # Update only changed field
        new_acceptance = self.ids.acceptance.text.strip() or old_acceptance
        new_learned = self.ids.learned.text.strip() or old_learned

        # Save new values
        c.execute("UPDATE textfeild SET acceptance = ?, learned = ? WHERE id = 1", (new_acceptance, new_learned))
        conn.commit()
        conn.close()

    def next_slide(self):
        self.ids.carousel.load_next()

    def previous_slide(self):
        self.ids.carousel.load_previous()


    
    


    def process_response_background(self):
        try:
            img_text = self.ids.image_text.text.strip()
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
        c.execute("SELECT gen_image  FROM textfeild WHERE id = 1")
        result = c.fetchone()
        
        c.execute("UPDATE textfeild SET  gen_image = ? WHERE id = 1", (image_path,))
        conn.commit()
        conn.close()
        self.ids.spinner.active = False
        self.ids.futureimg.source = image_path
        self.ids.futureimg.reload()  # Ensure the image updates if already set

    def openpodcast(self,pod:str):
        # Loading UI
        if pod == "1":
            youtube_url = "https://www.youtube.com/watch?v=EvuQPpDPM4A&list=PL-vH9r-QDUXMjocj0I6EyD8oa2YmpYl_1&ab_channel=EstherPerel" 
        elif pod == "2":
            youtube_url = "https://www.youtube.com/watch?v=OTQJmkXC2EI&ab_channel=JayShettyPodcast"
        elif pod == "3":
            youtube_url = "https://www.youtube.com/watch?v=mPQBcb9wf8Q&ab_channel=JayShettyPodcast"
        else:
            youtube_url = "https://www.youtube.com/watch?v=Hh_ynaNRpb0&ab_channel=MatthewHussey"
        if platform == "android":
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")

            intent = Intent(Intent.ACTION_VIEW, Uri.parse(youtube_url))
            currentActivity = PythonActivity.mActivity
            currentActivity.startActivity(intent)
        else:
            import webbrowser

            webbrowser.open(youtube_url)

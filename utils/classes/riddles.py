
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.clock import Clock
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
import random
import json

import requests
import json
import io   # <- only needed if you want to treat text as a file‑like object

class reddles(Screen):
    riddles = []
    shown_riddles = []
    current_riddle = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quotes = [
            "You are not alone.", "This too shall pass.", "Breathe. You're doing great.",
            "You are loved.", "Courage grows in quiet moments.", "Every day is a fresh start.",
            "Healing takes time.", "Feelings are valid.", "You’re stronger than you think."
        ]
        Clock.schedule_once(self.start_floating_quotes, 1)
        Clock.schedule_once(self.load_riddles, 0)

    # def load_riddles(self, *args):
    #     try:
    #         with open("C:\\Machine Learning\\Emotion_app\\kivy\\mental_health_riddles_200.json", "r", encoding="utf-8") as f:
    #             self.riddles = json.load(f)
    #     except Exception as e:
    #         print("Error loading riddles:", e)
    #         self.riddles = [
    #             {"riddle": "What has to be broken before you can use it?", "answer": "An egg"},
    #             {"riddle": "I’m tall when I’m young, and I’m short when I’m old. What am I?", "answer": "A candle"},
    #             {"riddle": "What month of the year has 28 days?", "answer": "All of them"}
    #         ]

    def load_riddles(self, *args):
        """
        Populate self.riddles with the 200‑riddle JSON on GitHub.
        Falls back to three hard‑coded riddles if the download fails.
        """
        RAW_URL = (
            "https://raw.githubusercontent.com/"
            "Uvais5/Mental-Health-AI-App/master/data/mental_health_riddles_200.json"
        )

        try:
            resp = requests.get(RAW_URL, timeout=10)
            resp.raise_for_status()           # network / 4xx / 5xx problems → except block
            self.riddles = json.loads(resp.text)
        except Exception as e:
            # Log and fall back gracefully
            print(f"[load_riddles] Error downloading riddles → {e}")
            self.riddles = [
                {"riddle": "What has to be broken before you can use it?", 
                "answer": "An egg"},
                {"riddle": "I’m tall when I’m young, and I’m short when I’m old. What am I?", 
                "answer": "A candle"},
                {"riddle": "What month of the year has 28 days?", 
                "answer": "All of them"},
            ]

    def start_floating_quotes(self, *args):
        for _ in range(40):
            self.spawn_floating_quote(random.choice(self.quotes))

    def spawn_floating_quote(self, quote):
        layout = self.ids.floating_layer
        if layout.width < 200 or layout.height < 50:
            Clock.schedule_once(lambda dt: self.spawn_floating_quote(quote), 0.1)
            return

        label = MDLabel(
            text=quote,
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.9),
            size_hint=(None, None),
            size=(200, 50),
            font_style="Subtitle1",
        )
        label.pos = (
            random.randint(0, int(layout.width - 200)),
            random.randint(0, int(layout.height - 50)),
        )
        layout.add_widget(label)
        self.animate_label(label)

    def animate_label(self, label):
        layout = self.ids.floating_layer
        if layout.width <= 0 or layout.height <= 0:
            Clock.schedule_once(lambda *a: self.animate_label(label), 0.1)
            return

        anim = Animation(
            x=random.randint(0, int(layout.width - 200)),
            y=random.randint(0, int(layout.height - 50)),
            duration=random.uniform(5, 8)
        )
        anim.bind(on_complete=lambda *args: self.animate_label(label))
        anim.start(label)

    def on_rope_drag(self, widget, touch):
        if widget.collide_point(*touch.pos) and touch.dy < -10:
            self.animate_bulb()
            self.show_riddle_banner()

    def animate_bulb(self):
        bulb = self.ids.bulb_icon
        # Rotate down, then back up
        anim = Animation(angle=30, duration=0.1) + Animation(angle=0, duration=0.1)
        anim.start(bulb)

    def show_riddle_banner(self):
        banner = self.ids.quote_banner
        self.ids.img.source="https://i.pinimg.com/736x/a9/b3/7d/a9b37d07c9ca0b2be3ffabcaca483d9b.jpg"
        if banner.opacity == 0:
            anim = Animation(height=dp(350), opacity=1, d=0.3)
            anim.start(banner)
            self.show_next_riddle()

    def show_next_riddle(self, *args):
        if not self.riddles:
            return

        if len(self.shown_riddles) == len(self.riddles):
            self.shown_riddles = []

        remaining = [r for r in self.riddles if r not in self.shown_riddles]
        riddle = random.choice(remaining)
        self.shown_riddles.append(riddle)
        self.current_riddle = riddle

        self.ids.banner_quote.text = f"{riddle['riddle']}"
        self.ids.options_box.clear_widgets()

        correct = riddle["answer"]
        other_answers = list({r["answer"] for r in self.riddles if r["answer"] != correct})
        incorrect = random.sample(other_answers, min(3, len(other_answers)))

        all_options = incorrect + [correct]
        random.shuffle(all_options)

        for option in all_options:
            btn = MDRaisedButton(
                text=option,
                size_hint=(1, None),
                height=dp(40),
                md_bg_color=(43/255, 95/255, 146/255,1),
                on_release=lambda btn, option=option: self.check_answer(option)
            )
            self.ids.options_box.add_widget(btn)

    def check_answer(self, selected_option):
        correct = self.current_riddle["answer"].strip().lower()
        if selected_option.strip().lower() == correct:
            self.ids.banner_quote.text = "Correct! Tap bulb again for new riddle."
        else:
            self.ids.banner_quote.text = f"Nope! It was: {self.current_riddle['answer']}"
        Clock.schedule_once(self.show_next_riddle, 3)



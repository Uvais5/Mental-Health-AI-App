# main.py
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivymd.uix.fitimage import FitImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton as Button
from kivy.clock import Clock
import random
from kivy.core.window import Window
import sqlite3
import time
import random
from kivymd.uix.label import MDLabel
from kivy.properties import ListProperty, StringProperty

from kivy.uix.modalview import ModalView
from kivymd.uix.boxlayout import MDBoxLayout

from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from utils.classes.database import get_database_path



class TestScreen(Screen):
    question_text = StringProperty("Some question text")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.question_text=[]
        self.stroop_words = ["Happy", "Sad", "Fear", "Calm"]
        self.colors = ["red", "green", "blue", "yellow"]
        self.correct_color = random.choice(self.colors)
        self.start_time = None  # Track start time
        self.end_time = None  # Track end time
        self.response_time = None  # Time taken to respond
        self.test_results = {}  # Store individual test results
        self.color=None
        self.db_path = get_database_path()[0]
    options = ListProperty([]) 
    def show_result(self, message, test_name=None):
        if test_name:
            self.test_results[test_name] = message
            self.check_all_tests_completed()
        Popup(title='Result', content=MDLabel(text=message), size_hint=(0.7, 0.3)).open()

    def check_all_tests_completed(self):
        if len(self.test_results) == 4:
            Clock.schedule_once(lambda dt: self.show_conclusion(), 2)

    def show_conclusion(self):
        conclusion = "Conclusion:\n"
        score = 0

        if "optimism" in self.test_results.get("cognitive", "").lower():
            score += 1
        else:
            score -= 1

        if "good focus" in self.test_results.get("stroop", "").lower():
            score += 1
        else:
            score -= 1

        if "heightened" in self.test_results.get("visual", "").lower():
            score += 1
        else:
            score -= 1

        if "promptly" in self.test_results.get("morph", "").lower():
            score += 1
        else:
            score -= 1

        if score >= 3:
            level = "Low signs of depression. Emotional state seems healthy."
        elif score == 1 or score == 2:
            level = "Mild emotional disturbance detected. Monitor yourself."
        else:
            level = "Potential signs of depression or emotional stress."

        conclusion += level
        Popup(title="Final Analysis", content=MDLabel(text=conclusion), size_hint=(0.8, 0.4)).open()

    # --------- Cognitive Test ---------
    def start_cognitive_test(self):
        self.test_data = random.sample([
            {
                "url": "https://i.pinimg.com/736x/9d/db/01/9ddb01e2328f861ce2f50aa76a145b02.jpg",
                "options": ["A young woman", "An old woman"],
                "interpretation": {
                    "A young woman": "You might be someone who sees the bright side of situations. You're probably open to new ideas, hopeful about the future, and often focus on opportunities ahead of you.",
                    "An old woman": "You may be more thoughtful and realistic. You like to prepare for possible problems and may prefer security, stability, and wisdom over taking risks."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/12/6c/ac/126cacad55c63ad3b1cf44255e0b29b0.jpg",
                "options": ["A rabbit", "A duck"],
                "interpretation": {
                    "A rabbit": "You might be imaginative, quick-thinking, and love exploring new or abstract ideas. You probably enjoy creativity, big dreams, and solving problems in unique ways.",
                    "A duck": "You likely enjoy structure and order. You pay attention to fine details and may prefer facts, logic, and careful planning over uncertainty or spontaneity."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/4d/6e/6d/4d6e6d240c8ede790fd0797ef038ea07.jpg",
                "options": ["A lion", "A tree"],
                "interpretation": {
                    "A lion": "You may be bold, passionate, and emotionally driven. You likely face challenges head-on and are seen as a natural leader or someone who values strength and courage.",
                    "A tree": "You are likely calm, balanced, and grounded. You may value peace, personal growth, and long-term progress rather than dramatic or risky action."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/a6/fd/f1/a6fdf196e000c058f00fe8d6486ad431.jpg",
                "options": ["Square A is darker", "Squares A and B are the same shade"],
                "interpretation": {
                    "Square A is darker": "You may take things at face value and rely on your senses and first impressions. This means you tend to trust what you see without questioning it much.",
                    "Squares A and B are the same shade": "You probably question what you see and think deeply before accepting something as true. You’re curious and enjoy uncovering hidden truths or illusions."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/f8/a4/e5/f8a4e52ce16414bb7401cb3e13497321.jpg",
                "options": ["Lines are straight", "Lines are sloped"],
                "interpretation": {
                    "Lines are sloped": "You may trust your instincts and go with your gut feelings. You often rely on intuition and react quickly without overthinking.",
                    "Lines are straight": "You tend to pause and double-check things before making a judgment. This shows strong critical thinking and a desire to understand things clearly."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/e6/83/a3/e683a36e3adaca8892658cf5d0fdb468.jpg",
                "options": ["Two faces", "A vase"],
                "interpretation": {
                    "Two faces": "You’re likely people-oriented and socially aware. You pay attention to emotions, relationships, and human connection, and may enjoy interacting with others.",
                    "A vase": "You may be object- or environment-focused, noticing the background or the bigger picture. You might enjoy working alone, analyzing surroundings, or thinking about concepts more than people."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/5e/47/20/5e4720e1cb2549080a647baba783c4fe.jpg",
                "options": ["Cube pointing down-right", "Cube pointing up-left"],
                "interpretation": {
                    "Cube pointing down-right": "You might be someone who tends to see things from a more traditional or common perspective initially, but you're capable of shifting your viewpoint.",
                    "Cube pointing up-left": "You may have a tendency to look for alternative perspectives or see things differently from the norm. You enjoy exploring multiple possibilities."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/8d/9a/52/8d9a5261f1ff72001cfb8a3d0b671218.jpg",
                "options": ["Spinning clockwise", "Spinning counter-clockwise", "Switches direction"],
                "interpretation": {
                    "Spinning clockwise": "You might be more right-brain dominant, often associated with creativity, intuition, and holistic thinking.",
                    "Spinning counter-clockwise": "You may be more left-brain dominant, often associated with logic, analytical thinking, and attention to detail.",
                    "Switches direction": "You likely have a flexible mind, able to see multiple perspectives and adapt your thinking easily. You might be good at problem-solving by looking at things from different angles."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/30/26/5b/30265b89fae5f81df2591b982a4c7397.jpg",
                "options": ["A white triangle on top", "Three black circles and three angles"],
                "interpretation": {
                    "A white triangle on top": "You tend to see the bigger picture and can easily connect disparate pieces of information to form a cohesive whole. You're good at seeing patterns.",
                    "Three black circles and three angles": "You are detail-oriented and focus on the concrete elements in front of you. You prefer to analyze individual components before looking at the whole."
                }
            },
            {
                "url": "https://how-emotions-are-made.com/w/images/heam/b/b7/M%C3%BCller-Lyer_illusion.png",
                "options": ["Top line is longer", "Bottom line is longer", "Both lines are the same length"],
                "interpretation": {
                    "Top line is longer": "You might be easily influenced by contextual cues and how things are framed. First impressions can be strong for you.",
                    "Bottom line is longer": "You might be easily influenced by contextual cues and how things are framed. First impressions can be strong for you.",
                    "Both lines are the same length": "You have a keen eye for detail and are less swayed by misleading information. You tend to analyze things objectively."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/6d/7e/52/6d7e52f5cdee77a340e97e82c1adb187.jpg",
                "options": ["The blue line is aligned with the black line", "The blue line is aligned with the red line"],
                "interpretation": {
                    "The blue line is aligned with the black line": "You trust your initial visual judgment even when it might be misleading. You might be a quick decision-maker.",
                    "The blue line is aligned with the red line": "You are able to see past immediate distortions and perceive the underlying reality. You likely have good spatial reasoning."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/93/ed/77/93ed779fbd4f7a1441f2f2b23037e54f.jpg",
                "options": ["The long lines are diverging/converging", "The long lines are parallel"],
                "interpretation": {
                    "The long lines are diverging/converging": "You are perceptive to how surrounding elements can influence your overall view. You might be sensitive to subtle influences.",
                    "The long lines are parallel": "You can maintain focus on the primary objects despite distracting patterns. You have a strong sense of objective reality."
                }
            },
            {
                "url": "hhttps://i.pinimg.com/736x/3f/4f/06/3f4f06b437ceac3194a4b457d9b630f5.jpg",
                "options": ["The two vertical lines are bowed outwards", "The two vertical lines are straight and parallel"],
                "interpretation": {
                    "The two vertical lines are bowed outwards": "You tend to perceive things in relation to their background or context, which can sometimes alter your perception of the main subject.",
                    "The two vertical lines are straight and parallel": "You are good at isolating objects from their surroundings and seeing them for what they are. You're not easily fooled by contextual noise."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/73/2f/4d/732f4d6b0e5a56bc0fd6b0c22a8707d8.jpg",
                "options": ["The top yellow line is longer", "The bottom yellow line is longer", "Both yellow lines are the same length"],
                "interpretation": {
                    "The top yellow line is longer": "Your brain is adept at using perspective cues to judge size, which is usually helpful but can be tricked! You might be good at understanding spatial relationships.",
                    "The bottom yellow line is longer": "This is a less common perception and might indicate a unique way of processing visual depth information.",
                    "Both yellow lines are the same length": "You are excellent at focusing on the intrinsic properties of objects, rather than being swayed by contextual depth cues. You are very analytical."
                }
            },
            {
                "url": "https://www.psy.ritsumei.ac.jp/akitaoka/FraserSpiral_vector.jpg",
                "options": ["It's a spiral", "They are concentric circles"],
                "interpretation": {
                    "It's a spiral": "You are easily captivated by patterns that suggest movement or depth. You might have a holistic way of seeing things, where the overall impression dominates.",
                    "They are concentric circles": "You have a sharp eye for detail and can mentally deconstruct complex patterns to see their true components. You are likely very analytical."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/aa/43/26/aa4326424af7aae1180ec715e925c7a7.jpg",
                "options": ["A 3D triangular object", "An impossible 2D representation"],
                "interpretation": {
                    "A 3D triangular object": "You have a strong tendency to interpret 2D images as 3D objects, even when they defy logic. You might be very imaginative.",
                    "An impossible 2D representation": "You quickly recognize inconsistencies and paradoxes. You likely have a logical and analytical mind that enjoys understanding how things work (or don't!)."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/2b/55/61/2b55617bb3b353e3a904cf5d5adf06fe.jpg",
                "options": ["The left orange circle is smaller", "The right orange circle is smaller", "Both orange circles are the same size"],
                "interpretation": {
                    "The left orange circle is smaller": "You are influenced by the relative size of surrounding objects. You might be good at making comparative judgments.",
                    "The right orange circle is smaller": "You are influenced by the relative size of surrounding objects, but in this case, you are focusing on the perceived space around the circle.",
                    "Both orange circles are the same size": "You are adept at ignoring contextual information when assessing the core attributes of an object. You are very objective."
                }
            },
            {
                "url": "https://upload.wikimedia.org/wikipedia/en/c/ca/Shepard_elephant_poster.jpg",
                "options": ["Four legs", "Five legs", "It's impossible to count / Confusing"],
                "interpretation": {
                    "Four legs": "You try to find logical patterns even in ambiguous situations and may focus on the conventional representation.",
                    "Five legs": "You are attentive to all visible elements, even if they create a puzzling overall picture. You notice details that others might overlook.",
                    "It's impossible to count / Confusing": "You recognize ambiguity and paradox. You are likely comfortable with uncertainty and enjoy a good mental puzzle."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/90/fa/1b/90fa1bf0fa04ce4a443828b4265e622c.jpg", 
                "options": ["See an image of Jesus after looking away", "See a blurry afterimage", "See nothing specific"],
                "interpretation": {
                    "See an image of Jesus after looking away": "Your visual system is creating a strong negative afterimage. You might be someone who is highly focused and whose perceptions can be quite vivid.",
                    "See a blurry afterimage": "You experience the common physiological effect of afterimages. You have a typical visual processing system.",
                    "See nothing specific": "You might have shifted your gaze too quickly or not focused long enough. Or, you might be less prone to strong afterimage effects."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/95/47/5a/95475a9361ff34ab3a250e260b7eee0a.jpg", 
                "options": ["See the hidden animal quickly", "Take some time to find the animal", "Cannot find the animal"],
                "interpretation": {
                    "See the hidden animal quickly": "You have excellent observational skills and a knack for spotting patterns or anomalies. You're likely very perceptive.",
                    "Take some time to find the animal": "You are methodical in your observations and will eventually find what you're looking for with persistence.",
                    "Cannot find the animal": "You might be more of a big-picture thinker, or perhaps your attention wasn't fully engaged by this specific type of puzzle."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/ac/a8/67/aca867c0ada2148fbcfce8e4c344f902.jpg", 
                "options": ["A tiger's face", "The words 'THE HIDDEN TIGER' in the stripes"],
                "interpretation": {
                    "A tiger's face": "You are adept at recognizing familiar patterns and forms, focusing on the overall image presented.",
                    "The words 'THE HIDDEN TIGER' in the stripes": "You have a keen eye for detail and can pick out subtle or embedded information that many would miss. You look beyond the obvious."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/49/62/99/4962997ea6369a0ad27cf7cdfa8f2907.jpg",
                "options": ["A functioning waterfall", "An impossible structure"],
                "interpretation": {
                    "A functioning waterfall": "You are initially drawn to the overall scene and its apparent function, showcasing a tendency to accept visual information as presented.",
                    "An impossible structure": "You have a critical eye for detail and logic, quickly noticing when something defies the laws of physics or perspective. You enjoy analyzing complexities."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/aa/30/58/aa3058244d0731cdd74a79125faff11b.jpg", 
                "options": ["The word 'Man'", "The word 'Liar'"],
                "interpretation": {
                    "The word 'Man'": "You may tend to see the more straightforward or common interpretation first. You might have a generally positive or neutral outlook.",
                    "The word 'Liar'": "You might be more inclined to look for hidden meanings or be more critical in your initial assessment. You are perceptive of underlying messages."
                }
            },
            {
                "url": "https://i.pinimg.com/736x/5a/7d/84/5a7d84970ea20e75155bd804c3d99115.jpg",
                "options": ["See grey dots at intersections", "See only white lines and black squares"],
                "interpretation": {
                    "See grey dots at intersections": "Your brain's lateral inhibition process is very active, leading you to perceive these illusory spots. This is a common and normal visual phenomenon.",
                    "See only white lines and black squares": "You might have a way of focusing that minimizes this particular illusion, or your brain processes these contrasts differently. You might be good at filtering out visual 'noise'."
                }
            }
           
        ], 6) # Keep the original 6 and add 20 more

        self.current_index = 0
        self.user_choices = []
        self.show_test_popup()

    def show_test_popup(self):
        if self.current_index >= len(self.test_data):
            self.show_cognitive_result()
            return

        item = self.test_data[self.current_index]
        question = "What do you see?"
        options = item["options"]
        image_url = item["url"]

        # self = self.root.get_screen("custom_popup")

        # Set title, question, and progress
        self.ids.popup_title.text = "Cognitive Bias Test"
        self.ids.popup_progress.text = f"Question {self.current_index + 1} / {len(self.test_data)}"
        self.ids.popup_progress_bar.value = ((self.current_index + 1) / len(self.test_data)) * 100

        # Set question text
        self.question_text = question

        # Clear old buttons and image if needed
        self.ids.option_buttons.clear_widgets()
        
        self.ids.question_image.source = image_url
        # else:
        #     # Dynamically add image if not already present
        #     image = FitImage(source=image_url, id="question_image", size_hint_y=None, height=dp(300))
        #     self.ids.option_buttons.parent.add_widget(image, index=2)  # insert below progress

        # Add option buttons
        for opt in options:
            btn = Button(
                text=opt,
                pos_hint={"center_x": 0.5},
                size_hint=(0.9, None),
                height=dp(48),
                md_bg_color=(70/255, 108/255, 185/255),
                on_release=lambda btn: self.record_choice_and_next(btn.text)

            )
            self.ids.option_buttons.add_widget(btn)

        
        self.ids.testmanager.current = "custom_popup"
    def switch_screen(self,screen_name):
        
        self.ids.testmanager.current = screen_name
    def record_choice_and_next(self, choice):
        self.user_choices.append(choice)
        #self.popup.dismiss()
        self.current_index += 1
        self.show_test_popup()



    def show_cognitive_result(self):
        result_text = "Your choices:\n"
        interpretations = []
        try:
            for i, choice in enumerate(self.user_choices):
                result_text += f"{i + 1}. {choice}\n"
                illusion = self.test_data[i]
                interp = illusion.get("interpretation", {}).get(choice)
                if interp:
                    sentences = interp.strip().split(". ")
                    interpretations.append(f"{i + 1}. {interp}\n" + "-" * 40)
            result_text += "\n\n\nInterpretations:\n\n\n"
            result_text += "\n".join(interpretations)

            self.test_results["cognitive"] = result_text
        except:
            print("stop")
        # Fullscreen modal
        result_popup = ModalView(size_hint=(0.95, 0.8), auto_dismiss=False)

        root_layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))

        # ScrollView for result text
        scroll = MDScrollView()
        scroll_box = MDBoxLayout(orientation="vertical", size_hint_y=None, padding=dp(10), spacing=dp(10))
        scroll_box.bind(minimum_height=scroll_box.setter("height"))

        # Title
        scroll_box.add_widget(MDLabel(
            text="Cognitive Test Result",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=dp(40)
        ))

        # Result text
        result_label = MDLabel(
            text=result_text,
            halign="left",
            theme_text_color="Custom",
            size_hint_y=None,
            color="white",
            markup=True,
            text_size=(Window.width - dp(80), None)  # allow wrapping
        )
        result_label.bind(
            texture_size=lambda instance, value: setattr(instance, 'height', value[1])
        )
        scroll_box.add_widget(result_label)

        scroll.add_widget(scroll_box)
        root_layout.add_widget(scroll)

        # Close button pinned at the bottom
        close_btn = Button(
            text="Close",
            pos_hint={"center_x": 0.5},
            size_hint=(None, None),
            size=(dp(150), dp(48))
        )
        close_btn.bind(on_release=result_popup.dismiss)
        root_layout.add_widget(close_btn)

        result_popup.add_widget(root_layout)
        result_popup.open()

        print(result_text)
    def next_image(self):
        self.popup.dismiss()
        self.current_index += 1
        self.show_test_popup()

    def start_stroop_test(self):
        self.correct_color = random.choice(self.colors)  # Random color selection for correct answer
        layout = MDBoxLayout(orientation='vertical', spacing=20, padding=20)

        # 🔹 Hint text
        hint = MDLabel(
            text="👉 Select the COLOR of the word, not what the word says. Take your time and click the correct color.",
            theme_text_color="Secondary",
            halign="center",
            font_style="Caption"
        )
        layout.add_widget(hint)

        # 🔹 Word with color (the stimulus)
        word = random.choice(self.stroop_words)
        label = MDLabel(
            text=word,
            halign="center",
            font_style="H4",
            theme_text_color="Custom",
            text_color=self.correct_color  # Shows the color of the word
        )
        layout.add_widget(label)

        # Start timer
        self.start_time = time.time()

        # 🔹 Buttons for color choices
        for color in self.colors:
            btn = Button(
                text=color.capitalize(),
                md_bg_color=color,  # MDRaisedButton supports this
                on_release=lambda btn, c=color: self.evaluate_stroop(c == self.correct_color)
            )
            layout.add_widget(btn)

        # 🔹 Show popup
        self.popup = Popup(title='Stroop Test', content=layout, size_hint=(0.8, 0.8))
        self.popup.open()

    def evaluate_stroop(self, is_correct):
        self.end_time = time.time()
        self.response_time = self.end_time - self.start_time

        feedback_text = (
            f" Correct! You took {self.response_time:.2f} seconds."
            if is_correct else
            f"❌ Incorrect! You took {self.response_time:.2f} seconds."
        )

        # Feedback popup
        feedback_popup = Popup(
            title="Feedback",
            content=MDLabel(text=feedback_text, halign="center", theme_text_color="Secondary"),
            size_hint=(0.6, 0.4)
        )
        feedback_popup.open()

        self.popup.dismiss()

        # Show high-level cognitive result
        result = "Good focus and emotional control." if is_correct else "Potential emotional interference."
        self.show_result(result, "stroop")

  
    def start_dass21_test(self):
        self.dass_questions = [
        "I found it hard to wind down",  # Stress
        "I was aware of dryness of my mouth",  # Anxiety
        "I couldn’t seem to experience any positive feeling at all",  # Depression
        "I experienced breathing difficulty",  # Anxiety
        "I found it difficult to work up the initiative",  # Depression
        "I tended to over-react to situations",  # Stress
        "I experienced trembling",  # Anxiety
        "I felt that I was using a lot of nervous energy",  # Stress
        "I was worried about situations in which I might panic",  # Anxiety
        "I felt I had nothing to look forward to",  # Depression
        "I found myself getting agitated",  # Stress
        "I felt sad and depressed",  # Depression
        "I found it difficult to relax",  # Stress
        "I felt down-hearted and blue",  # Depression
        "I was intolerant of anything that kept me from getting on",  # Stress
        "I felt I was close to panic",  # Anxiety
        "I was unable to become enthusiastic",  # Depression
        "I felt I was not worth much",  # Depression
        "I felt that I was rather touchy",  # Stress
        "I was aware of action in my stomach when I was anxious",  # Anxiety
        "I felt scared without any good reason",  # Anxiety
        
        # ➕ Additional Questions:
        "I felt that life was meaningless",  # Depression
        "I had difficulty in swallowing",  # Anxiety
        "I found it hard to calm down after something upset me",  # Stress
        "I felt I was losing control over things",  # Anxiety
        "I felt like I was under pressure all the time",  # Stress
        "I couldn't get going even when I had things to do",  # Depression
        "I felt faint or dizzy for no clear reason",  # Anxiety
        "I was easily startled",  # Anxiety
        "I had trouble managing even small tasks",  # Depression
        "I found myself snapping at others for minor things",  # Stress
        "I had a persistent sense of dread or doom",  # Anxiety
        "I cried for no reason or over small things",  # Depression
        "I felt that my stress was physically draining me",  # Stress
        "I felt mentally exhausted even after small tasks",  # Depression
        "I had racing thoughts that made it hard to focus",  # Anxiety/Stress
    ]

        # self.dass_index = 0
        self.dass_scores = []
        # self.show_dass_question() 
        self.dass_index = 0
        self.user_dass_answers = []
        # random.shuffle(self.dass_questions) 
        self.dass_selected_questions = random.sample(self.dass_questions, 21) # Shuffle the question list randomly
        self.show_dass_question() # Show the first question using the custom screen
    def show_dass_question(self):
        if self.dass_index >= 21:
            self.evaluate_dass_results()  # Show results after the last question
            return

        question = self.dass_selected_questions[self.dass_index]

        # self = self.root.get_screen("custom_popup")
        
        self.ids.question_image.source="https://i.pinimg.com/736x/04/89/29/048929d1c4cdea5f341f254f7d16af5a.jpg"

        # Update title and progress
        self.ids.popup_title.text = "DASS-21 Test"
        self.ids.popup_progress.text = f"Question {self.dass_index + 1} / 21"

        self.ids.popup_progress_bar.value = ((self.dass_index + 1) / 21) * 100

        # Set the question text
        self.question_text = question  # This binds to `popup_question` in the layout

        # Clear previous option buttons
        self.ids.option_buttons.clear_widgets()

        # Add the new set of response buttons dynamically
        responses = [
            "Did not apply",
            "Applied sometimes",
            "Applied often",
            "Applied very much"
        ]
        for i, label in enumerate(responses):
            btn = Button(
                text=label,
                size_hint=(0.9, None),
                height=dp(48),
                pos_hint={"center_x": 0.5},
                md_bg_color=(164/255, 136/255, 221/255),
                on_release=lambda btn, i=i: self.record_dass_score(i)
            )
            self.ids.option_buttons.add_widget(btn)

        # Move to the custom popup screen
        self.ids.testmanager.current = "custom_popup"


    def record_dass_score(self, score):
        self.dass_scores.append(score)
        self.dass_index += 1
        self.show_dass_question()  # Show next question
    def get_dass_description(self, score, level, category):
        symptoms_and_recommendations = {
            "Depression": {
                "Normal": (
                    "**Symptoms**: No or minimal signs of low mood.\n"
                    "**What it means**: You're emotionally balanced.\n\n"
                    "**What to do**:\n"
                    "- Continue using daily **voice affirmations** to stay grounded.\n"
                    "- Use **Pre-Journal** entries to set positive intentions.\n"
                    "- Explore **visualization** to mentally rehearse success and peace."
                ),
                "Mild": (
                    "**Symptoms**: Occasional sadness, loss of interest, or fatigue.\n"
                    "**What it means**: You're feeling a bit low but functioning.\n\n"
                    "**What to do**:\n"
                    "- Use **Thought Reframing (CBT)** to challenge negative patterns.\n"
                    "**Imagery-based CBT** to visualize overcoming emotional blocks.\n"
                    "- Daily **voice affirmations** and **affirmation journaling** to boost hope."
                ),
                "Moderate": (
                    "**Symptoms**: Persistent sadness, withdrawal, or low motivation.\n"
                    "**What it means**: Mood disturbances are more noticeable.\n\n"
                    "**What to do**:\n"
                    "- Use the **CBT Thought Diary** and **Reframing Prompts**.\n"
                    "- Engage in **Imagery CBT** to imagine recovery and safety.\n"
                    "- Journal using both **Pre** and **After** entries to track progress."
                ),
                "Severe": (
                    "**Symptoms**: Deep sadness, hopelessness, sleep/appetite changes.\n"
                    "**What it means**: Your emotional health is significantly impacted.\n\n"
                    "**What to do**:\n"
                    "- Break thoughts into small parts using **structured CBT**.\n"
                    "- Rely on **Law of Attraction** tools: daily **visualization** + **voice affirmations**.\n"
                    "- Use **imagery-based sessions** to reconnect with strength."
                ),
                "Extremely Severe": (
                    "**Symptoms**: Intense emotional pain, disconnection, lack of interest in life.\n"
                    "**What it means**: You're going through serious emotional suffering.\n\n"
                    "**What to do**:\n"
                    "- Commit to daily **visual CBT sessions** and **guided journaling**.\n"
                    "- Repeat **calming affirmations** in your own voice.\n"
                    "- Use **After-Journal** entries to reflect on efforts and emotions each day."
                )
            },
            "Anxiety": {
                "Normal": (
                    "**Symptoms**: Minimal worry, mentally calm.\n"
                    "**What it means**: You're coping well emotionally.\n\n"
                    "**What to do**:\n"
                    "- Maintain balance with **visualization** exercises.\n"
                    "- Reinforce peace with **voice affirmations**.\n"
                    "- Use **journaling** to keep track of calm routines."
                ),
                "Mild": (
                    "**Symptoms**: Occasional restlessness, mild tension.\n"
                    "**What it means**: Slightly anxious but manageable.\n\n"
                    "**What to do**:\n"
                    "- Use the **Worry Tracker** and **CBT Reframing** tools.\n"
                    "- Visualize calming outcomes before stressful tasks.\n"
                    "- Practice **voice affirmations** for nervous system regulation."
                ),
                "Moderate": (
                    "**Symptoms**: Frequent nervousness, racing thoughts.\n"
                    "**What it means**: Anxiety is interfering with focus or comfort.\n\n"
                    "**What to do**:\n"
                    "- Ground yourself with **CBT journaling and breathing tools**.\n"
                    "- Practice **affirmation journaling** to create emotional safety.\n"
                    "- Use **imagery visualization** to simulate peace in anxious situations."
                ),
                "Severe": (
                    "**Symptoms**: Panic, physical tension, overwhelming worry.\n"
                    "**What it means**: Anxiety is disrupting your daily routine.\n\n"
                    "**What to do**:\n"
                    "- Apply **CBT thought breakdowns** to disarm fear.\n"
                    "- Create mental ‘safe zones’ with **visualization techniques**.\n"
                    "- Anchor calm with **daily voice affirmations** and **After-Journals**."
                ),
                "Extremely Severe": (
                    "**Symptoms**: Constant dread, panic, inability to relax.\n"
                    "**What it means**: Anxiety is severe and persistent.\n\n"
                    "**What to do**:\n"
                    "- Use **deep CBT imagery** and **exposure journaling** daily.\n"
                    "- Practice **visualization** to soothe emotional chaos.\n"
                    "- Strengthen confidence with **spoken affirmations** and reflective journaling."
                )
            },
            "Stress": {
                "Normal": (
                    "**Symptoms**: Balanced energy and emotional control.\n"
                    "**What it means**: Stress levels are well managed.\n\n"
                    "**What to do**:\n"
                    "- Use **mini-visualizations** and quick affirmations to stay recharged.\n"
                    "- Use **journals** to reflect on what’s working well."
                ),
                "Mild": (
                    "**Symptoms**: Slight overwhelm, occasional frustration.\n"
                    "**What it means**: Small stressors are starting to affect you.\n\n"
                    "**What to do**:\n"
                    "- Use **CBT stress tracking tools** to identify triggers.\n"
                    "- Take **visualization breaks** to mentally reset.\n"
                    "- Use **affirmations** like “I release pressure” throughout your day."
                ),
                "Moderate": (
                    "**Symptoms**: Physical fatigue, irritability, overthinking.\n"
                    "**What it means**: Chronic stress may be lowering your energy.\n\n"
                    "**What to do**:\n"
                    "- Apply **CBT scheduling + reframing** strategies.\n"
                    "- Journal intentions and recovery using **Pre and After** formats.\n"
                    "- Visualize overcoming stress with success-focused imagery."
                ),
                "Severe": (
                    "**Symptoms**: Constant overwhelm, sleep issues, frustration.\n"
                    "**What it means**: Stress is interfering with functioning.\n\n"
                    "**What to do**:\n"
                    "- Use **CBT task breakdown tools** to manage overload.\n"
                    "- Tap into **Law of Attraction** via visualizations and affirmations.\n"
                    "- Use **imagery** sessions to mentally release control and relax."
                ),
                "Extremely Severe": (
                    "**Symptoms**: Emotional shutdown, burnout, agitation.\n"
                    "**What it means**: Stress may be at a dangerous level.\n\n"
                    "**What to do**:\n"
                    "- Follow structured **CBT workflows** for emotional clarity.\n"
                    "- Use deep **visualizations** and **voice affirmations** for healing.\n"
                    "- Reflect daily using **affirmation journaling** to support recovery."
                )
            }
        }

        return symptoms_and_recommendations[category][level]


    def evaluate_dass_results(self):
        depression_indices = [2, 4, 9, 11, 13, 16, 17]
        anxiety_indices = [1, 3, 6, 8, 15, 19, 20]
        stress_indices = [0, 5, 7, 10, 12, 14, 18]

        depression = sum([self.dass_scores[i] for i in depression_indices]) * 2
        anxiety = sum([self.dass_scores[i] for i in anxiety_indices]) * 2
        stress = sum([self.dass_scores[i] for i in stress_indices]) * 2

        def classify(score, thresholds):
            levels = list(thresholds.items())
            for i, (level, threshold) in enumerate(levels):
                if score <= threshold:
                    return level
            return "Extremely Severe"

        


        dep_level = classify(depression, {"Normal": 9, "Mild": 13, "Moderate": 20, "Severe": 27})
        anx_level = classify(anxiety, {"Normal": 7, "Mild": 9, "Moderate": 14, "Severe": 19})
        str_level = classify(stress, {"Normal": 14, "Mild": 18, "Moderate": 25, "Severe": 33})

        result = f"""
        [b]DASS-21 Clinical Test Results[/b]

        [i]Depression Score[/i]: [b]{depression}[/b] [color=#ff5555]{dep_level}[/color]
        {self.get_dass_description(depression, dep_level, "Depression")}

        [i]Anxiety Score[/i]: [b]{anxiety}[/b]  [color=#ff9900]{anx_level}[/color]
        {self.get_dass_description(anxiety, anx_level, "Anxiety")}

        [i]Stress Score[/i]: [b]{stress}[/b] [color=#ffaa00]{str_level}[/color]
        {self.get_dass_description(stress, str_level, "Stress")}
        """

        self.test_results["dass21"] = result
        self.check_all_tests_completed()
        self.save_test_result(self.db_path,"DAS",result)
        # Fullscreen Modal Popup
        result_popup = ModalView(size_hint=(0.95, 0.8), auto_dismiss=False)

        root_layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))

        scroll = MDScrollView()
        scroll_box = MDBoxLayout(orientation="vertical", size_hint_y=None, padding=dp(10), spacing=dp(10))
        scroll_box.bind(minimum_height=scroll_box.setter("height"))

        # Title
        scroll_box.add_widget(MDLabel(
            text="DASS-21 Result",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=dp(40)
        ))

        # Result Text
        result_label = MDLabel(
            text=result,
            halign="left",
            theme_text_color="Custom",
            size_hint_y=None,
            color="white",
            markup=True,
            text_size=(Window.width - dp(80), None)
        )
        result_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        scroll_box.add_widget(result_label)

        scroll.add_widget(scroll_box)
        root_layout.add_widget(scroll)

        close_btn = Button(
            text="Close",
            pos_hint={"center_x": 0.5},
            size_hint=(None, None),
            size=(dp(150), dp(48))
        )
        close_btn.bind(on_release=result_popup.dismiss)
        root_layout.add_widget(close_btn)

        result_popup.add_widget(root_layout)
        result_popup.open()
    def save_test_result(self,db_path, testtype, description):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if test already exists
            cursor.execute("SELECT * FROM testresult WHERE testtype = ?", (testtype,))
            existing = cursor.fetchone()

            if existing:
                # Update existing test result
                cursor.execute("""
                    UPDATE testresult
                    SET descriptions = ?
                    WHERE testtype = ?
                """, (description, testtype))
                print(f"{testtype} test updated.")
            else:
                # Insert new test result
                cursor.execute("""
                    INSERT INTO testresult (testtype, descriptions)
                    VALUES (?, ?)
                """, (testtype, description))
                print(f"{testtype} test added.")

            conn.commit()
            conn.close()

            

        except Exception as e:
            print(f"Database error: {e}")
            return None
    
    def start_PHQ_GDA_test(self, test_type):
        
        # Define questions only once
        self.phq9_questions = [
            "Little interest or pleasure in doing things?",
            "Feeling down, depressed, or hopeless?",
            "Trouble sleeping (too little or too much)?",
            "Feeling tired or low on energy?",
            "Poor appetite or overeating?",
            "Feeling bad about yourself, or that you're a failure?",
            "Trouble concentrating on things like reading or TV?",
            "Moving or speaking noticeably slowly, or being unusually fidgety or restless?",
            "Thoughts that you'd be better off dead, or of hurting yourself?",
            "Feeling emotionally numb or disconnected?",
            "Losing motivation to take care of daily responsibilities?",
            "Feeling overwhelmed by small tasks?",
            "Avoiding people or isolating yourself?",
            "Crying often or feeling like crying for no clear reason?"
        ]

        self.gad7_questions = [
            "Have you been feeling nervous or constantly on edge?",
            "Do you find it hard to stop or control your worrying?",
            "Do you often worry about a lot of different things?",
            "Have you had trouble calming yourself or relaxing?",
            "Do you feel restless or like you can’t sit still?",
            "Have you been getting easily annoyed or irritated?",
            "Do you feel afraid, like something bad might happen?",
            "Do you find yourself overthinking or replaying situations in your mind a lot?",
            "Do you feel physical tension — like a tight chest or racing heart — from stress or worry?",
            "Have you been avoiding things (places, people, conversations) because of anxiety?",
            "Do you sometimes feel like your mind goes blank when you're stressed?",
            "Has it been hard to fall asleep because of constant worrying or racing thoughts?",
            "Do you get startled easily or feel on edge all the time?"
        ]


        # Set test type
        self.test_type = test_type

        # Choose the appropriate set of questions
        if test_type == "PHQ-9":
            self.current_questions = random.sample(self.gad7_questions, 6)
            self.ids.question_image.source="https://i.pinimg.com/736x/d9/1c/c3/d91cc3e903cebe3284cca4938aa1e15a.jpg"
            self.color = (64/255, 38/255, 115/255)

        elif test_type == "GAD-7":
            self.current_questions = random.sample(self.gad7_questions, 6)
            self.ids.question_image.source="https://i.pinimg.com/736x/c9/e2/2a/c9e22aa661447cb5d1135d5cbbe81578.jpg"
            self.color = (61/255, 114/255, 126/255)
        else:
            print("Unknown test type")
            return

        # Reset state
        self.user_answers = []
        self.current_question_index = 0

        # Show first question
        self.show_next_question()
    

    def show_next_question(self):
        if self.current_question_index < len(self.current_questions):
            question = self.current_questions[self.current_question_index]

            # self = self.root.get_screen("custom_popup")
            
            self.ids.popup_title.text = self.test_type
            self.ids.popup_progress.text = f"Question {self.current_question_index + 1} / {len(self.current_questions)}"

            progress_percent = ((self.current_question_index + 1) / len(self.current_questions)) * 100
            self.ids.popup_progress_bar.value = progress_percent

            self.question_text = question

            self.ids.option_buttons.clear_widgets()
            responses = [
                    "0 - I haven’t felt this at all",
                    "1 - I've felt this on a few days",
                    "2 - I've felt this more than half the week",
                    "3 - I've felt this almost every day"
                ]
            for i, label in enumerate(responses):
                btn = Button(
                    text=label,
                    size_hint=(0.9, None),
                    height=dp(48),
                    pos_hint={"center_x": 0.5},
                    md_bg_color=self.color,
                    on_release=lambda btn, i=i: self.save_answer(i)
                )
                self.ids.option_buttons.add_widget(btn)

            # Show the popup screen
            self.ids.testmanager.current = "custom_popup"
        else:
            self.show_test_result()

    def save_answer(self, value):
        self.user_answers.append(value)
        self.current_question_index += 1
        self.show_next_question()


    def show_test_result(self):
        score = sum(self.user_answers)

        if self.test_type == "PHQ-9":
            if score <= 4:
                level = "Minimal depression\n\n What it means: Your mood is generally stable with few or no signs of depression.\n\n Symptoms might include: Mild fatigue, rare low mood, occasional trouble sleeping.\n\n What to do: Keep up your routine with **voice affirmations** and **visualization**.\n\n- Use the **Pre-Journal** to set daily goals and stay positive."
                
            elif score <= 9:
                level = """Mild depression\n\nWhat it means: You may be experiencing occasional low moods that slightly affect your daily life.\n\n Symptoms might include: Sadness, reduced interest, mild sleep or appetite changes.\n\nWhat to do:Use **Thought Reframing (CBT)** to catch and change negative thinking.\n\n Try **Imagery-based CBT** to visualize emotional strength.\nSupport yourself with daily **affirmations** and **journaling**."""
                
            elif score <= 14:
                level = """Moderate depression\n\nWhat it means: You're experiencing noticeable depression symptoms that interfere with daily activities.\n\n Symptoms might include: Low motivation, difficulty concentrating, social withdrawal.\n\n What to do:Use structured **CBT techniques** like journaling and reframing.\n\nIncorporate **imagery visualization** to boost hope and resilience.\nUse **voice affirmations** to support positive self-talk.\nTrack progress in your **Pre and After Journals**."""
            
            elif score <= 19:
                level = """Moderately severe depression\n\nWhat it means: Your symptoms are significantly affecting your ability to function.\n\n Symptoms might include: Deep sadness, loss of interest, major fatigue, sleep disturbance.\n\n What to do: Commit to daily **CBT-based thought tracking and restructuring**.\n\nUse **Imagery CBT** to create mental scenarios of healing.\nLean into **visualization** and **affirmations** for emotional guidance.\nReflect consistently with **After-Journal** entries."""
                
            else:
                level = """Severe depression\n\nWhat it means: You're experiencing intense emotional suffering that may impact all areas of life.\n\n Symptoms might include: Hopelessness, frequent crying, physical sluggishness, suicidal thoughts.\n\n What to do:Follow intensive **CBT journaling and support prompts** in the app.\n\nUse **visualization** to mentally practice recovery and connection.\nRepeat **voice affirmations** often to rewire your mindset.\nUse **After-Journal** to track emotions and efforts daily.\nConsider seeking professional help alongside app-based tools."""

            
        elif self.test_type == "GAD-7":
            if score <= 4:
                level = (
                    "Minimal Anxiety\n\n"
                    "What it means:\n"
                    "You are currently experiencing very few or no symptoms of anxiety.\n\n"
                    "Is this a concern?:\n"
                    "Not typically. Occasional stress or worry is normal.\n\n"
                    " What to do:\n"
                    "• Use Law of Attraction tools to set positive intentions.\n"
                    "• Practice gratitude journaling and mindful focus.\n"
                    "• Maintain balance with good sleep, exercise, and hydration."
                )
            elif score <= 9:
                level = (
                    "Mild Anxiety\n\n"
                    "What it means:\n"
                    "You may experience occasional anxiety that slightly affects daily life.\n\n"
                    "Symptoms might include:\n"
                    "• Nervousness\n"
                    "• Mild trouble concentrating\n"
                    "• Slight restlessness\n\n"
                    " What to do:\n"
                    "• Try CBT Thought Reframing to challenge negative thinking.\n"
                    "• Use Law of Attraction tools to reframe emotional energy.\n"
                    "• Begin identifying triggers and patterns using the journaling tool."
                )
            elif score <= 14:
                level = (
                    "Moderate Anxiety\n\n"
                    "What it means:\n"
                    "Anxiety is starting to interfere with your daily functioning.\n\n"
                    "Symptoms may include:\n"
                    "• Frequent worrying\n"
                    "• Difficulty relaxing\n"
                    "• Sleep disruption\n\n"
                    " What to do:\n"
                    "• Use both CBT tools: Thought Reframing & CBT Imagery to reduce anxiety loops.\n"
                    "• Engage in daily visualization exercises aligned with Law of Attraction.\n"
                    "• Reflect on values and goals to ground your mindset."
                )
            else:
                level = (
                    "Severe Anxiety\n\n"
                    "What it means:\n"
                    "You may be experiencing significant anxiety that affects daily life, work, and relationships.\n\n"
                    "Symptoms often include:\n"
                    "• Constant fear or worry\n"
                    "• Panic attacks or physical symptoms\n"
                    "• Inability to focus or sleep\n\n"
                    " What to do:\n"
                    "• Begin CBT Thought Reframing sessions to break anxious thinking cycles.\n"
                    "• Use CBT Imagery for calming and exposure to feared scenarios in a safe space.\n"
                    "• Try Law of Attraction scripting to shift attention toward inner power and goals.\n"
                    "• Seek additional support if anxiety becomes overwhelming."
                )
            


        result_text = f"{self.test_type} Score: {score}\nAssessment: {level}"
        self.save_test_result(self.db_path,self.test_type,result_text)
        # Create the popup window
        popup = ModalView(size_hint=(0.9, 0.7))

        # Create the box layout for the popup
        box = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(20))

        # Create a ScrollView to hold the content
        scroll_view = MDScrollView()

        # Create a MDLabel to display the result text, and add it to the ScrollView
        label = MDLabel(text=result_text, halign="center", size_hint_y=None)
        label.bind(texture_size=label.setter('size'))  # This ensures the label expands vertically

        scroll_view.add_widget(label)

        # Add the scroll view to the box layout
        box.add_widget(scroll_view)

        # Create a close button
        close_btn = Button(text="Close")
        close_btn.bind(on_release=popup.dismiss)
        box.add_widget(close_btn)

        # Add the box layout to the popup
        popup.add_widget(box)

        # Open the popup
        popup.open()

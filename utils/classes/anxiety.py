
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton ,MDRectangleFlatButton
from kivy.clock import Clock
import random
from kivy.utils import platform
from utils.image_gen.img_gen import image_generator 

from kivy.clock import Clock

import random
from kivy.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel

from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView

from kivymd.uix.boxlayout import MDBoxLayout

from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton, MDIconButton
from kivymd.uix.card.card import MDSeparator
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from utils.classes.database import get_database_path
import sqlite3
from kivy.clock import Clock
from threading import Thread
class anxiety(Screen):
    dialog = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dare_options = {
            "Dance to music": "Put on a song you love, close your eyes, and just move your body freely. Focus on the rhythm and how your muscles feel.\n\n[b]Why it works: [/b] Physical release, distraction,mood boost from music,connection to body.",
            "Splash water on face": "Use cool or cold water. Focus on the sharp, invigorating sensation on your skin. Notice the temperature and how it makes you feel alert.\n\n[b]Why it works: [/b] Sensory shock (diverts focus), vagus nerve stimulation (calming effect), helps regulate heart rate.",
            "Snuggle a pet": "Really feel their fur, listen to their purr or gentle breathing. Focus on the warmth and comfort they provide.\n\n[b]Why it works: [/b]Oxytocin release (bonding hormone, calming), sensory input (touch, sound), unconditional affection.",
            "Eat something sour": "Take a small bite and let the sourness fill your mouth. Notice the intense flavor and how your mouth reacts. This sharp sensation can cut through anxious thoughts.\n\n[b]Why it works: [/b]Intense sensory input (taste) acts as a powerful distraction and can 'reset' your focus.",
            "Go outside": "Even for a few minutes, notice the air on your skin, the sounds of nature or the city, and something you can see far away. Take a few deep breaths of fresh air.\n\n[b]Why it works: [/b]Change of environment, connection to nature, fresh air, grounding through senses.",
            "Take a deep breath": "Place one hand on your belly. Inhale slowly through your nose for a count of 4, feeling your belly rise. Hold for 4, then exhale slowly through your mouth for 6, feeling your belly fall. Repeat 3-5 times.\n\n[b]Why it works: [/b]Direct activation of the parasympathetic nervous system (rest and digest), lowers heart rate, increases oxygen, promotes calm. This is foundational.",
            "Reach out to someone": "Send a quick text or make a short call to a trusted friend or family member. Share something small about your day, or just say hello. You don't have to talk about your anxiety if you don't want to.\n\n[b]Why it works: [/b]Social connection (reduces feelings of isolation), perspective shift, sense of support.",
            "Watch movies or something": "Choose something lighthearted or comforting that you know well. Really focus on the story, the characters, and the sounds. Let yourself get lost in it for a bit.\n\n[b]Why it works: [/b]Distraction, provides a temporary escape from anxious thoughts, can evoke positive emotions"
        }
        self.dares = list(self.dare_options.keys())
        self.spin_count = 0
        self.selected_dare = None
        self._spin_event = None

        self.db_path = get_database_path()[0]
        self.show_test_results()
        self.load_existing_data()
    def on_kv_post(self, base_widget):
       # self.init_db()
        
        self.ids.after_dare.bind(text=self.on_text_change)
    def _start_worry_audit_dialog(self, instance):
        raw_worries = self.ids.brain_dump_input.text.strip().split('\n')
        self.worries_list = [worry.strip() for worry in raw_worries if worry.strip()]
        self.current_worry_index = 0
        self.processed_worries = []
        self.ids.brain_dump_input.text = ""

        if self.worries_list:
            self._present_next_worry_dialog()
        else:
            self.show_dialog("No Worries Detected", "Please enter some worries in the brain dump.")
    def _present_next_worry_dialog(self):
        if self.current_worry_index < len(self.worries_list):
            worry = self.worries_list[self.current_worry_index]

            # ScrollView with worry text
            scroll_box = MDBoxLayout(
                orientation="vertical",
                padding=dp(10),
                size_hint_y=None,
                spacing=dp(10),
            )

            worry_label = MDLabel(
                text=worry,
                halign="left",
                theme_text_color="Primary",
                size_hint_y=None,
            )
            worry_label.bind(
                texture_size=lambda instance, size: setattr(
                    worry_label, 'height', size[1]
                )
            )
            scroll_box.add_widget(worry_label)

            # Make scroll_box height dynamic
            scroll_box.bind(
                minimum_height=lambda instance, height: setattr(
                    scroll_box, 'height', height
                )
            )

            scroll = ScrollView(size_hint=(1, None), height=dp(200))
            scroll.add_widget(scroll_box)

            # Buttons below the scrollview
            button_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=[dp(20), dp(10), dp(20), dp(10)],
                size_hint_y=None,
            )
            button_layout.add_widget(MDRectangleFlatButton(
                text="I Can Control This",
                on_release=lambda x: self._handle_worry_dialog("control"),
                md_bg_color="green",
                text_color=(1, 1, 1, 1),
                size_hint_x=1,
                size_hint=(1, None),
                height=dp(100)
            ))
            button_layout.add_widget(MDRectangleFlatButton(
                text="I Can Influence This",
                on_release=lambda x: self._handle_worry_dialog("influence"),
                md_bg_color="yellow",
                text_color=(0, 0, 0, 1),
                size_hint_x=1,
                size_hint=(1, None),
                height=dp(100)
            ))
            button_layout.add_widget(MDRectangleFlatButton(
                text="I cannot control this",
                on_release=lambda x: self._handle_worry_dialog("accept"),
                md_bg_color="blue",
                text_color=(1, 1, 1, 1),
                size_hint=(1, None),
                height=dp(100)
            ))

            # Combine scroll and buttons
            content_box = MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=dp(10),
                size_hint_y=None,
            )
            space = MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=dp(10),
                size_hint_y=None,
                height=dp(70)
            )
            content_box.add_widget(scroll)
            content_box.add_widget(space)
            content_box.add_widget(button_layout)

            # Dynamically set the height based on scroll + buttons
            content_box.height = scroll.height + dp(200)

            self.worry_dialog = MDDialog(
                title=f"Worry {self.current_worry_index + 1}",
                type="custom",
                content_cls=content_box,
                size_hint_y=None,
                height=dp(500)
            )
            self.worry_dialog.open()
        else:
            self._show_worry_summary_dialog()



    def get_result_by_testtype(self, db_path, testtype):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT descriptions FROM testresult WHERE testtype = ?", (testtype,))
            result = cursor.fetchone()
            conn.close()
            print(result[0])
            if result:
                return {
                    "testtype": testtype,
                    "description": result[0]
                }
            else:
                return None  # No entry for this test

        except Exception as e:
            print(f"Error retrieving result for {testtype}: {e}")
            return None


    def show_test_results(self):
        test_box = self.ids.test_box
        test_box.clear_widgets()

        result = self.get_result_by_testtype(self.db_path, "GAD-7")
        if not result:
            return

        # Main card
        card = MDCard(
            orientation="vertical",
            size_hint=(1, None),
            padding=dp(15),
            radius=[15],
            md_bg_color=(0.12, 0.12, 0.12, 1),
            elevation=4,
        )

        # Vertical container
        card_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=(0, 0),
            size_hint_y=None
        )

        card_box.bind(minimum_height=card_box.setter("height"))

        # Title
        title_label = MDLabel(
            text=f"[b]{result['testtype']} Test Result[/b]",
            markup=True,
            font_style="H6",
            halign="left",
            size_hint_y=None,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            text_size=(self.width - dp(60), None),
        )
        title_label.bind(
            texture_size=lambda instance, value: setattr(instance, "height", value[1])
        )

        # Description
        desc_label = MDLabel(
            text=result['description'],
            theme_text_color="Secondary",
            halign="left",
            size_hint_y=None,
            text_size=(self.width - dp(60), None),
        )
        desc_label.bind(
            texture_size=lambda instance, value: setattr(instance, "height", value[1])
        )

        # Add to card
        card_box.add_widget(title_label)
        card_box.add_widget(desc_label)
        card.add_widget(card_box)

        # Set total card height after layout is calculated
        def update_card_height(*args):
            card.height = card_box.height + dp(30)

        card_box.bind(height=update_card_height)

        # Add to test box
        test_box.add_widget(card)
    
    def openpodcast(self,pod:str):
        # Loading UI
        if pod == "1":
            youtube_url = "https://www.youtube.com/watch?v=79kpoGF8KWU" 
        elif pod == "2":
            youtube_url = "https://www.youtube.com/watch?v=bjvPbfxE3CI"
        elif pod == "3":
            youtube_url = "https://www.youtube.com/watch?v=plZkm_XpZ4I"
        else:
            youtube_url = "https://www.youtube.com/watch?v=nnSRJ5PRPWQ"
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
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT gen_image  FROM anxiety_textfeild WHERE id = 1")
        result = c.fetchone()
        
        c.execute("UPDATE anxiety_textfeild SET  gen_image = ? WHERE id = 1", (image_path,))
        conn.commit()
        conn.close()
        self.ids.spinner.active = False
        self.ids.calm_canvas.source = image_path
        self.ids.calm_canvas.reload()

    def load_existing_data(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT release_audit, after_dare, gen_image FROM anxiety_textfeild WHERE id = 1")
        result = c.fetchone()
        print(result)
        if result:
            print(result)
            self.ids.after_dare.text = result[1]
            self._finalize_worry_plan_dialog(database_fatch=result[0])
            try:
                self.ids.calm_canvas.source = result[2]
            except:
                self.ids.calm_canvas.source = "https://i.pinimg.com/736x/27/70/3e/27703e160a8aa2c2daa7d553941e428e.jpg"
        conn.close()
        
    def on_text_change(self, instance, value):
        print("working")
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Load old value safely
        c.execute("SELECT after_dare FROM anxiety_textfeild WHERE id = 1")
        result = c.fetchone()
        old_dare = result[0] if result else ""

        # Get new value from TextField
        new_dare = self.ids.after_dare.text.strip()

        # If it's empty, keep the old value
        if not new_dare:
            new_dare = old_dare

        # Save new value (always a string now)
        c.execute("UPDATE anxiety_textfeild SET after_dare=? WHERE id = 1", (new_dare,))
        conn.commit()
        conn.close()


    def next_slide(self):
        self.ids.carousel.load_next()

    def previous_slide(self):
        self.ids.carousel.load_previous()

    def _handle_worry_dialog(self, category):
        self.worry_dialog.dismiss()
        worry_text = self.worries_list[self.current_worry_index]

        content_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            adaptive_height=True
        )

        text_input = MDTextField(
            hint_text="e.g., Your plan here...",

            size_hint_y=None,
            height=dp(100)
        )
        self.current_guidance_input_reference = text_input

        if category == "control":
            content_box.add_widget(MDLabel(text=f"Worry: {worry_text}", halign="left",adaptive_height=True))
            content_box.add_widget(MDSeparator(height=dp(1)))
            content_box.add_widget(MDLabel(text="Action Plan:", halign="left",adaptive_height=True,text_color=(153/255, 102/255, 51/255,1)))
            content_box.add_widget(MDSeparator(height=dp(1)))
            content_box.add_widget(MDLabel(adaptive_height=True,text="Write some actionable steps you can take to address.", halign="left"))
            content_box.add_widget(MDSeparator(height=dp(1)))
            content_box.add_widget(MDLabel(adaptive_height=True,text="Examples", halign="left",text_color=(153/255, 102/255, 51/255,1)))
            
            content_box.add_widget(MDLabel(adaptive_height=True,text="\n•Review my notes and slides.\n•Practice the presentation out loud, timing myself.\n• Arrive early to set up and get comfortable.", halign="left"))
            
            text_input.hint_text = "e.g., 'Practice interview questions'"
        elif category == "influence":
            content_box.add_widget(MDLabel(text="How will you influence this?", halign="left",adaptive_height=True))
            content_box.add_widget(MDSeparator(height=dp(1)))
            content_box.add_widget(MDLabel(adaptive_height=True,text=f"You can't directly control the outcome \n{worry_text}\n, but how can you influence the situation or your response to it? What's within your power?", halign="left"))
            content_box.add_widget(MDSeparator(height=dp(1)))
            content_box.add_widget(MDLabel(adaptive_height=True,text="Examples", halign="left",text_color=(153/255, 102/255, 51/255,1)))
            
            content_box.add_widget(MDLabel(adaptive_height=True,text="\n•I can prepare a summary of my work on the project to make it easier for them to review.\n•I can shift my focus to starting the next task while I wait for feedback, so I'm still productive.\n• Arrive early to set up and get comfortable.", halign="left"))
            
            text_input.hint_text = "e.g., 'Send reminder email'"
        elif category == "accept":
            content_box.add_widget(MDLabel(font_style="Subtitle2",adaptive_height=True,text=f"this worry, \n{worry_text}\n, is outside of your direct control. It's okay to feel that, and now we can practice letting go. Which of these helps you?", halign="left"))
            content_box.add_widget(MDSeparator(height=dp(1)))

            content_box.add_widget(MDLabel(bold="True",font_style="Subtitle1",adaptive_height=True,text="Choose an Acceptance Affirmation and Write ", halign="left"))
            
            content_box.add_widget(MDLabel(font_style="Subtitle2",adaptive_height=True,text="\n•I accept that some things are beyond my control.\n•I am safe even amidst uncertainty.", halign="left"))
            content_box.add_widget(MDSeparator(height=dp(1)))
            content_box.add_widget(MDLabel(font_style="Subtitle1",bold="True",adaptive_height=True,text="Examples", halign="left"))
            content_box.add_widget(MDLabel(adaptive_height=True,text="I can control my breathing by taking slow, deep breaths. I can also choose to focus my attention on something positive right now, like planning my evening, instead of dwelling on the recession.", halign="left"))

            content_box.add_widget(MDSeparator(height=dp(1)))
            content_box.add_widget(MDLabel(adaptive_height=True,text="What can you control in this moment?"))
            text_input.hint_text = "e.g., 'My breath'"

        content_box.add_widget(text_input)
        
        # Horizontal layout for buttons
        button_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        continue_btn = MDFlatButton(
            text="Continue",
            on_release=lambda x: self._finalize_worry_plan_dialog(worry_text, category, text_input.text)
        )
        cancel_btn = MDFlatButton(
            text="Cancel",
            on_release=lambda x: self.category_dialog.dismiss()
        )
        
        button_box.add_widget(cancel_btn)
        button_box.add_widget(continue_btn)
        content_box.add_widget(button_box)

        self.category_dialog = MDDialog(
            title=f"{category.capitalize()} Plan",
            type="custom",
            content_cls=content_box,
            size_hint_y=None,
            height=dp(500)
        )
        self.category_dialog.open()



    def _finalize_worry_plan_dialog(self, worry_text=None, category=None, plan_text=None,database_fatch = None):
        try:
            full_text = (
            f"[b]Worry:[/b] {worry_text}\n\n"
            f"[b]Category:[/b] {category.capitalize()}\n\n"
            f"[b]Plan:[/b] {plan_text.strip()}"
            )
            self.category_dialog.dismiss()
            self.processed_worries.append({
            'worry': worry_text,
            'category': category,
            'plan': plan_text.strip()
        })
        except:
            full_text = database_fatch
        
        
        # Store processed worry
        
        # print("this is label : ",self.processed_worries)
        # lab =  f"[b]Worry:[/b] {worry_text}", (1, 1, 1, 1)) [b]Category:[/b] {category.capitalize()}", (0.8, 0.8, 1, 1)),
        #     (f"[b]Plan:[/b] {plan_text.strip()}", (0.9, 1, 0.9, 1))
        # Reference to braindump layout
        braindump_box = self.ids.braindump
        braindump_box.height = dp(600)  # Expand height

        #  Check and remove existing scroll view
        if hasattr(self, 'my_scroll') and self.my_scroll in braindump_box.children:
            braindump_box.remove_widget(self.my_scroll)

        #  Create new ScrollView and BoxLayout
        scroll = ScrollView(size_hint_y=None, height=dp(200))
        scroll_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(10),
            spacing=dp(10)
        )
        scroll_box.bind(minimum_height=scroll_box.setter('height'))

        # Add worry, category, and plan as labels
        

        label = MDLabel(
            text=full_text,
            markup=True,
            halign="left",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),  # You can pick a blended color or leave it white
            size_hint_y=None
        )

        # Make the height adapt to the content
        label.bind(
            width=lambda instance, value: setattr(instance, "text_size", (value, None)),
            texture_size=lambda instance, value: setattr(instance, "height", value[1])
        )

        scroll_box.add_widget(label)

        print("this is label",full_text)
        scroll.add_widget(scroll_box)

        # ✅ Save reference for future removal
        self.my_scroll = scroll

        # ✅ Add scroll view to braindump
        braindump_box.add_widget(self.my_scroll)

        # Move to next worry
        try:
            self.current_worry_index += 1
        except:
            pass
        
        # self._present_next_worry_dialog()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check if row with id=1 exists
        c.execute("SELECT id FROM anxiety_textfeild WHERE id = 1")
        exists = c.fetchone()

        if exists:
            # Row exists, update it
            c.execute("UPDATE anxiety_textfeild SET release_audit=? WHERE id = 1", (full_text,))
        else:
            # Row doesn't exist, insert it
            c.execute("INSERT INTO anxiety_textfeild (id, release_audit) VALUES (1, ?)", (full_text,))

        conn.commit()
        conn.close()

    def show_reflection_dialog(self, *args):
        content_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            adaptive_height=True,
            padding=dp(10),
        )
        
        prompts = [
            "1. Describe the anxious episode or feeling you're reflecting on. What happened, or what thoughts were present?",
            "2. What did you do in response to the episode or feeling?",
            "3. How effective was your response? What could you improve next time?",
            "4. What positive outcome or lesson did you take from this reflection?"
        ]
        
        self.reflection_inputs = []
        
        for prompt in prompts:
            
            content_box.add_widget(MDLabel(text=prompt, halign="left", adaptive_height=True,
                                        text_color=(153/255, 102/255, 51/255, 1)))
            ti = MDTextField(
                hint_text="Your plan here...",
                size_hint_y=None,
                height=dp(100),
                multiline=True
            )
            content_box.add_widget(ti)
            self.reflection_inputs.append(ti)
        content_box.add_widget(MDSeparator(height=dp(1)))

        scroll = ScrollView(size_hint=(1, None), height=dp(400))

        scroll_content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=content_box.height,
            padding=dp(10),
            spacing=dp(10),
        )
        scroll_content.add_widget(content_box)

        # Bind height of content_box to minimum height to let it adapt to children
        content_box.bind(minimum_height=content_box.setter('height'))
        # Bind scroll_content height to content_box height for proper scrolling
        content_box.bind(height=lambda instance, value: setattr(scroll_content, 'height', value))

        scroll.add_widget(scroll_content)

        def print_inputs(instance):
            values = [ti.text for ti in self.reflection_inputs]
            print("Reflection Inputs:")
            for i, val in enumerate(values, 1):
                print(f"{i}. {val}")
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Reflection & Action Plan",
            type="custom",
            content_cls=scroll,
            buttons=[MDRaisedButton(text="Submit", on_release=print_inputs)],
            auto_dismiss=False
        )
        
        self.dialog.open()


    def _show_worry_summary_dialog(self, instance=None):  
        summary_text = "[b]Worry Audit Complete![/b]\nHere's a breakdown of your worries and your plan:\n\n"
        for item in self.processed_worries:
            summary_text += f"[b]Worry:[/b] {item['worry']}\n"
            summary_text += f"[b]Category:[/b] {item['category'].capitalize()}\n"
            summary_text += f"[b]Plan:[/b] {item['plan'] if item['plan'] else 'No specific plan recorded.'}\n---\n"

        inner_box = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        inner_box.bind(minimum_height=inner_box.setter("height"))

        inner_box.add_widget(MDLabel(text=summary_text, halign="left", markup=True))
        print("this is summary : ",summary_text)
        inner_box.add_widget(MDRectangleFlatButton(
            text="Start New Audit",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: (self._reset_control_audit(x), self.summary_dialog.dismiss())
        ))

        inner_box.add_widget(MDLabel(text="[i]Scroll down to explore other tools.[/i]", halign="center", font_style="Caption", markup=True))

        scroll = MDScrollView(size_hint=(1, None), height=dp(400))
        scroll.add_widget(inner_box)

        self.summary_dialog = MDDialog(
            title="Worry Audit Summary",
            type="custom",
            content_cls=scroll,
            size_hint_y=None,
            height=dp(500)
        )
        self.summary_dialog.open()
    
    def start_spin(self):
        self.ids.spin_label.text = ""
            # Update the spin_title ID with the anxiety-reducing tip
        self.ids.spin_title.text = ""
        self.spin_count = 0
        # When starting the spin, ensure a dare is selected from the valid keys
        self.selected_dare = random.choice(self.dares)

        self.ids.spinner_label.text = "Spinning..."
        # Schedule the roll_dares function to update the spinner display
        self._spin_event = Clock.schedule_interval(self.roll_dares, 0.1)

    def roll_dares(self, dt):
        if self.spin_count >= 30:
            self._spin_event.cancel() # Stop the spinning
            
            # --- This is the key change for showing the tip ---
            # Get the final dare that was selected in start_spin or the last roll
            final_dare_text = self.selected_dare
            # Look up the corresponding tip in your dare_options dictionary
            dare_tip_text = self.dare_options.get(final_dare_text, "No specific tip available for this dare.")

            # Update the main spinner label with just the dare
            self.ids.spinner_label.text = ""
            self.ids.spin_label.text = dare_tip_text
            # Update the spin_title ID with the anxiety-reducing tip
            self.ids.spin_title.text = final_dare_text
            if final_dare_text== "Splash water on face":
                #self.ids.feeling_note.text = "How do you feel when you splash a water on your face?."
                self.ids.back_feeling_img.source ="https://i.pinimg.com/736x/4a/cc/44/4acc44ae52fe5c0283c0c0f801dd9cc6.jpg"
                self.ids.back_feeling_img.opacity="0.3"
            elif final_dare_text == "Dance to music":
                
                self.ids.back_feeling_img.source = "https://i.pinimg.com/736x/d8/4e/91/d84e9182dacea515077b450a3c2ef23a.jpg"
                #self.ids.feeling_note.text = "How do you fell when you dance on a song?."
                
            elif final_dare_text == "Snuggle a pet":
                self.ids.back_feeling_img.source = "https://i.pinimg.com/736x/8d/cc/3e/8dcc3e22e81dab7c326059534cd84878.jpg"
                self.ids.back_feeling_img.opacity="0.3"
                #self.ids.feeling_note.text = "How do you feel when you snuggle a pet?."
                

            elif final_dare_text == "Eat something sour":
                self.ids.back_feeling_img.opacity="0.3"
                self.ids.back_feeling_img.source = "https://i.pinimg.com/736x/f5/85/d9/f585d96e0744be1fc8fa6bded4c70bb7.jpg"
                
                #self.ids.feeling_note.text = "How do you feel when you eat somthing sour?."
            elif final_dare_text == "Go outside":
                self.ids.back_feeling_img.opacity="0.3"
                self.ids.back_feeling_img.source = "https://i.pinimg.com/736x/fe/dd/58/fedd58afedba1f60c649d8921f39c7e4.jpg"
                #self.ids.feeling_note.text = "How do you feel when you Go outside?."
            elif final_dare_text == "Take a deep breath":
                self.ids.back_feeling_img.opacity="0.3"
                self.ids.back_feeling_img.source = "https://i.pinimg.com/736x/ab/12/8c/ab128cfdbfd6ef52b81c8f0933ca0e89.jpg"
                #self.ids.feeling_note.text = "How do you feel when you take a long  deep breath?."
            elif final_dare_text == "Reach out to someone":
                self.ids.back_feeling_img.opacity="0.3"
                #self.ids.feeling_note.text = "How do you feel when you reach out to someone?."
                self.ids.back_feeling_img.source = "https://i.pinimg.com/736x/ab/90/85/ab908510af9b6facbf2c230b84e922f0.jpg"
            elif final_dare_text == "Watch movies or something":
                self.ids.back_feeling_img.opacity="0.3"
                self.ids.back_feeling_img.source = "https://i.pinimg.com/736x/bb/1e/74/bb1e7425933edc5f1eaa7235052b8a48.jpg"
                #self.ids.feeling_note.text = "How do you feel when you watch a movies?."

            return

        # During the spin, keep randomly changing the displayed dare
        self.selected_dare = random.choice(self.dares) # Update selected_dare with each roll
        self.ids.spinner_label.text = self.selected_dare
        self.spin_count += 1


from kivy.lang import Builder
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.app import MDApp
from kivy.core.window import Window
from datetime import datetime
import calendar
from kivy.uix.label import Label
from kivy.uix.button import Button

class CustomCalendar(ModalView):
    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.size_hint = (0.9, 0.55)
        self.selected_date = datetime.now()
        self.primary_color = (148 / 255, 197 / 255, 224 / 255, 1)  # #94c5e0
        self.secondary_color = (1, 1, 1, 1)  # White
        self.layout = BoxLayout(orientation="vertical", padding=[10, 50, 10, 10], spacing=10)

        # Header (Month, Year, Navigation)
        self.header = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.prev_button = MDIconButton(
            icon="chevron-left",
            theme_icon_color="Custom",
            md_bg_color=self.primary_color,
            text_color=self.secondary_color,
        )
        self.prev_button.bind(on_release=self.go_prev_month)

        self.month_label = MDLabel(
            text=self.selected_date.strftime("%B %Y"),
            halign="center",
            theme_text_color="Custom",
            text_color=self.primary_color,
            font_style="H6",
        )

        self.next_button = MDIconButton(
            icon="chevron-right",
            theme_icon_color="Custom",
            md_bg_color=self.primary_color,
            text_color=self.secondary_color,
        )
        self.next_button.bind(on_release=self.go_next_month)

        self.header.add_widget(self.prev_button)
        self.header.add_widget(self.month_label)
        self.header.add_widget(self.next_button)

        # Date Grid Layout
        self.date_grid = GridLayout(cols=7, spacing=5, size_hint_y=None, height=300)
        self.weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        self.populate_weekdays()
        self.populate_dates()

        # Action Buttons
        self.action_buttons = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.cancel_button = MDRaisedButton(
            text="CANCEL", md_bg_color=(0.6, 0.6, 0.6, 1), on_release=self.dismiss
        )
        self.ok_button = MDRaisedButton(
            text="OK", md_bg_color=self.primary_color, on_release=self.confirm_date
        )
        self.action_buttons.add_widget(self.cancel_button)
        self.action_buttons.add_widget(self.ok_button)

        # Add everything to main layout
        self.layout.add_widget(self.header)
        self.layout.add_widget(self.date_grid)
        self.layout.add_widget(self.action_buttons)
        self.add_widget(self.layout)

    def populate_weekdays(self):
        """Add weekday labels."""
        for day in self.weekdays:
            self.date_grid.add_widget(
                MDLabel(
                    text=day,
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(0.7, 0.7, 0.7, 1),
                )
            )

    def populate_dates(self):
        """Generate correct days for the current month."""
        self.date_grid.clear_widgets()
        self.populate_weekdays()  # Re-add weekday labels

        # Get month data
        year, month = self.selected_date.year, self.selected_date.month
        month_days = calendar.monthrange(year, month)[1]
        first_day = calendar.monthrange(year, month)[0]

        # Fill empty slots before month start
        for _ in range(first_day):
            self.date_grid.add_widget(Label(text=""))

        # Add day buttons for the current month
        for day in range(1, month_days + 1):
            day_button = Button(
                text=str(day),
                background_color=self.secondary_color,
                size_hint=(None, None),
                size=(40, 40),
            )
            day_button.bind(on_release=self.select_date)
            self.date_grid.add_widget(day_button)

    def select_date(self, instance):
        """Handles date selection."""
        selected_day = int(instance.text)
        self.selected_date = self.selected_date.replace(day=selected_day)
        for child in self.date_grid.children:
            if isinstance(child, Button):
                child.background_color = (
                    self.primary_color if int(child.text) == selected_day else self.secondary_color
                )

    def go_prev_month(self, instance):
        """Go to the previous month."""
        if self.selected_date.month == 1:
            self.selected_date = self.selected_date.replace(year=self.selected_date.year - 1, month=12)
        else:
            self.selected_date = self.selected_date.replace(month=self.selected_date.month - 1)
        self.update_calendar()

    def go_next_month(self, instance):
        """Go to the next month."""
        if self.selected_date.month == 12:
            self.selected_date = self.selected_date.replace(year=self.selected_date.year + 1, month=1)
        else:
            self.selected_date = self.selected_date.replace(month=self.selected_date.month + 1)
        self.update_calendar()

    def update_calendar(self):
        """Update month label and repopulate dates."""
        self.month_label.text = self.selected_date.strftime("%B %Y")
        self.populate_dates()

    def confirm_date(self, instance):
        """Return the selected date."""
        if self.callback:
            self.callback(self.selected_date)
        self.dismiss()
"""
Like a Local - A travel companion app
Helps users discover local insights about their dream destinations
"""

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock

import json
import os
from api_client import get_api_client


# --------------------------------------------------
# TEMP DATA (will be replaced by GeoNames / SQLite)
# --------------------------------------------------
COUNTRY_CITIES = {
    "United States": ["New York", "Los Angeles", "Chicago", "San Francisco", "Miami"],
    "United Kingdom": ["London", "Manchester", "Birmingham", "Edinburgh"],
    "France": ["Paris", "Marseille", "Lyon", "Nice"],
    "Germany": ["Berlin", "Munich", "Hamburg", "Frankfurt"],
    "Japan": ["Tokyo", "Osaka", "Kyoto", "Nagoya"],
}


# ==================================================
# LOCATION SELECTOR WIDGET
# ==================================================
class LocationSelector(BoxLayout):
    """Reusable country + city selector with autocomplete dropdowns"""

    MAX_RESULTS = 5
    ROW_HEIGHT = 70
    MAX_HEIGHT = 280

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_country = None
        self.selected_city = None
        self.on_selection_callback = None

    def on_country_text_changed(self, text):
        if len(text) < 2:
            self._hide_panel(self.ids.country_panel, self.ids.country_rv)
            return

        matches = [
            c for c in COUNTRY_CITIES.keys()
            if text.lower() in c.lower()
        ][:self.MAX_RESULTS]

        self._show_panel(
            self.ids.country_panel,
            self.ids.country_rv,
            matches,
            self.select_country,
        )

    def select_country(self, country):
        self.selected_country = country
        self.ids.country_input.text = country
        self.ids.city_input.disabled = False
        self.ids.city_input.text = ""
        self.selected_city = None

        self._hide_panel(self.ids.country_panel, self.ids.country_rv)

    def on_city_text_changed(self, text):
        if not self.selected_country or len(text) < 2:
            self._hide_panel(self.ids.city_panel, self.ids.city_rv)
            return

        cities = COUNTRY_CITIES.get(self.selected_country, [])
        matches = [
            c for c in cities
            if text.lower() in c.lower()
        ][:self.MAX_RESULTS]

        self._show_panel(
            self.ids.city_panel,
            self.ids.city_rv,
            matches,
            self.select_city,
        )

    def select_city(self, city):
        self.selected_city = city
        self.ids.city_input.text = city
        self._hide_panel(self.ids.city_panel, self.ids.city_rv)

        # Notify parent if callback is set
        if self.on_selection_callback:
            self.on_selection_callback(self.selected_country, self.selected_city)

    def _show_panel(self, panel, rv, values, on_select):
        if not values:
            self._hide_panel(panel, rv)
            return

        rv.data = [
            {"text": value, "on_press": lambda v=value: on_select(v)}
            for value in values
        ]

        height = min(len(values) * self.ROW_HEIGHT, self.MAX_HEIGHT)
        Animation(height=height, duration=0.3, t="out_quad").start(panel)

    def _hide_panel(self, panel, rv):
        Animation.cancel_all(panel)
        Animation(height=0, duration=0.3, t="out_quad").start(panel)
        rv.data = []
        rv.refresh_from_data()

    def get_selection(self):
        """Returns tuple of (country, city) or (None, None) if incomplete"""
        return (self.selected_country, self.selected_city)


# ==================================================
# SIGNUP PAGE 1
# ==================================================
class SignupPage1(Screen):
    """Where are you from?"""

    def go_to_page2(self):
        location_selector = self.ids.location_selector
        country, city = location_selector.get_selection()

        if not country or not city:
            self._error("Please select both country and city")
            return

        app = App.get_running_app()
        app.temp_country = country
        app.temp_city = city

        self.manager.current = "signup_page2"

    def _error(self, msg):
        popup = Popup(
            title="Error",
            content=Label(text=msg),
            size_hint=(0.8, 0.3),
        )
        popup.open()


# ==================================================
# SIGNUP PAGE 2
# ==================================================
class SignupPage2(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extra_textbox_count = 0

    def add_more_textbox(self):
        self.extra_textbox_count += 1
        self.ids.additional_annoyances.add_widget(
            TextInput(
                hint_text=f"Annoyance {self.extra_textbox_count + 3} (optional)",
                size_hint_y=None,
                height=48,
                multiline=False,
            )
        )

    def submit_signup(self):
        annoyances = []

        if not self.ids.annoyance1.text.strip():
            self._error("At least one annoyance is required")
            return

        annoyances.append(self.ids.annoyance1.text.strip())

        for tid in ("annoyance2", "annoyance3"):
            text = self.ids[tid].text.strip()
            if text:
                annoyances.append(text)

        for child in self.ids.additional_annoyances.children:
            if child.text.strip():
                annoyances.append(child.text.strip())

        app = App.get_running_app()
        data = {
            "country": app.temp_country,
            "city": app.temp_city,
            "annoyances": annoyances,
        }

        with open("user_data.json", "w") as f:
            json.dump(data, f, indent=2)

        self.manager.current = "travel"

    def _error(self, msg):
        Popup(
            title="Error",
            content=Label(text=msg),
            size_hint=(0.8, 0.3),
        ).open()


# ==================================================
# TRAVEL SCREEN
# ==================================================
class TravelScreen(Screen):
    """Main travel search screen"""

    def search_city(self):
        location_selector = self.ids.location_selector
        country, city = location_selector.get_selection()

        if not city:
            return

        container = self.ids.results_container
        container.clear_widgets()

        container.add_widget(
            Label(
                text=f"Searching tips for {city}...",
                size_hint_y=None,
                height=40,
            )
        )

        Clock.schedule_once(lambda *_: self._load_results(city, country), 0.2)

    def _load_results(self, city, country):
        """Fetch and display promoted tips from the API"""
        container = self.ids.results_container
        container.clear_widgets()

        try:
            # Get API client
            api_client = get_api_client()

            # Fetch promoted tips
            promoted_tips = api_client.get_promoted_tips(
                location_name=city,
                location_country=country,
                limit=20
            )

            if not promoted_tips:
                container.add_widget(
                    Label(
                        text=f"No tips found yet for {city}, {country}.\nBe the first to share local insights!",
                        size_hint_y=None,
                        height=80,
                        halign="center"
                    )
                )
                return

            # Display promoted tips
            for tip in promoted_tips:
                # Create a label for each tip showing the text and mention count
                tip_text = tip.get("tip_text", "")
                mention_count = tip.get("mention_count", 0)

                # Create tip display
                tip_label = Label(
                    text=f"• {tip_text}\n   ({mention_count} locals mentioned this)",
                    size_hint_y=None,
                    height=80,
                    halign="left",
                    valign="top",
                    text_size=(350, None),
                    padding=(10, 10)
                )
                container.add_widget(tip_label)

        except Exception as e:
            container.add_widget(
                Label(
                    text=f"Error loading tips: {str(e)}",
                    size_hint_y=None,
                    height=60
                )
            )


# ==================================================
# SETTINGS
# ==================================================
class SettingsScreen(Screen):
    def edit_profile(self):
        self.manager.current = "signup_page1"


# ==================================================
# APP
# ==================================================
class TravelBuddyApp(App):
    def build(self):
        Builder.load_file("main.kv")

        Window.size = (400, 650)

        sm = ScreenManager(transition=SlideTransition(duration=0.3))
        sm.add_widget(SignupPage1(name="signup_page1"))
        sm.add_widget(SignupPage2(name="signup_page2"))
        sm.add_widget(TravelScreen(name="travel"))
        sm.add_widget(SettingsScreen(name="settings"))

        sm.current = "travel" if os.path.exists("user_data.json") else "signup_page1"
        return sm


if __name__ == "__main__":
    TravelBuddyApp().run()

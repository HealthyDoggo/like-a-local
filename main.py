"""
TravelBuddy - A travel companion app
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
import json
import os
from api_client import get_api_client

# Sample country-city data (in a real app, use a proper API or library)
COUNTRY_CITIES = {
    "United States": ["New York", "Los Angeles", "Chicago", "San Francisco", "Miami", "Seattle", "Boston"],
    "United Kingdom": ["London", "Manchester", "Birmingham", "Edinburgh", "Glasgow", "Liverpool"],
    "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes"],
    "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao", "Malaga"],
    "Italy": ["Rome", "Milan", "Naples", "Turin", "Florence", "Venice"],
    "Germany": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne", "Stuttgart"],
    "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama", "Nagoya", "Sapporo"],
    "China": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu", "Hangzhou"],
    "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa", "Edmonton"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Gold Coast"],
    "Brazil": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza", "Belo Horizonte"],
    "Mexico": ["Mexico City", "Guadalajara", "Monterrey", "Cancún", "Puebla", "Tijuana"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Kolkata", "Chennai", "Hyderabad"],
    "Thailand": ["Bangkok", "Chiang Mai", "Phuket", "Pattaya", "Krabi", "Ayutthaya"],
    "Netherlands": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven", "Groningen"],
}


class SignupPage1(Screen):
    """First signup page: Where are you from?"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        """Load country list when screen is entered"""
        countries = sorted(COUNTRY_CITIES.keys())
        self.ids.country_spinner.values = countries

    def on_country_selected(self):
        """When country is selected, populate city dropdown"""
        country = self.ids.country_spinner.text
        if country and country in COUNTRY_CITIES:
            cities = sorted(COUNTRY_CITIES[country])
            self.ids.city_spinner.values = cities
            self.ids.city_spinner.disabled = False
            self.ids.city_spinner.text = "Select City"

    def go_to_page2(self):
        """Navigate to second signup page"""
        country = self.ids.country_spinner.text
        city = self.ids.city_spinner.text

        if country == "Select Country" or not country:
            self.show_error("Please select a country")
            return

        if city == "Select City" or not city:
            self.show_error("Please select a city")
            return

        # Store selections temporarily
        app = App.get_running_app()
        app.temp_country = country
        app.temp_city = city

        # Navigate to page 2
        self.manager.current = 'signup_page2'

    def show_error(self, message):
        """Show error popup"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))

        close_btn = Button(text='OK', size_hint_y=None, height=40)
        content.add_widget(close_btn)

        popup = Popup(
            title='Error',
            content=content,
            size_hint=(0.8, 0.3)
        )

        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class SignupPage2(Screen):
    """Second signup page: What would you like tourists to do less?"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extra_textbox_count = 0

    def add_more_textbox(self):
        """Add an additional textbox for more annoyances"""
        container = self.ids.additional_annoyances
        self.extra_textbox_count += 1

        text_input = TextInput(
            hint_text=f"Annoyance {self.extra_textbox_count + 3} (optional)",
            size_hint_y=None,
            height=48,
            multiline=False
        )
        container.add_widget(text_input)

    def submit_signup(self):
        """Submit signup and save user data"""
        # Get all annoyances
        annoyances = []

        # Get required first annoyance
        ann1 = self.ids.annoyance1.text.strip()
        if not ann1:
            self.show_error("Please enter at least one thing tourists should do less")
            return

        annoyances.append(ann1)

        # Get optional annoyances
        ann2 = self.ids.annoyance2.text.strip()
        if ann2:
            annoyances.append(ann2)

        ann3 = self.ids.annoyance3.text.strip()
        if ann3:
            annoyances.append(ann3)

        # Get extra annoyances from dynamically added textboxes
        container = self.ids.additional_annoyances
        for child in container.children:
            if isinstance(child, TextInput):
                text = child.text.strip()
                if text:
                    annoyances.append(text)

        # Get location from temp storage
        app = App.get_running_app()
        country = getattr(app, 'temp_country', '')
        city = getattr(app, 'temp_city', '')

        # Save user data
        user_data = {
            'country': country,
            'city': city,
            'annoyances': annoyances
        }

        with open('user_data.json', 'w') as f:
            json.dump(user_data, f, indent=2)

        # Navigate to home screen
        self.manager.current = 'travel'

    def show_error(self, message):
        """Show error popup"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))

        close_btn = Button(text='OK', size_hint_y=None, height=40)
        content.add_widget(close_btn)

        popup = Popup(
            title='Error',
            content=content,
            size_hint=(0.8, 0.3)
        )

        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class TravelScreen(Screen):
    """Home screen: Where are you going?"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        """Load country list when screen is entered"""
        countries = sorted(COUNTRY_CITIES.keys())
        self.ids.country_spinner.values = countries

    def on_country_selected(self):
        """When country is selected, populate city dropdown"""
        country = self.ids.country_spinner.text
        if country and country in COUNTRY_CITIES:
            cities = sorted(COUNTRY_CITIES[country])
            self.ids.city_spinner.values = cities
            self.ids.city_spinner.disabled = False
            self.ids.city_spinner.text = "Select City"

    def search_city(self):
        """Search for a city and display tips"""
        country = self.ids.country_spinner.text
        city = self.ids.city_spinner.text

        if city == "Select City" or not city:
            return

        # Clear previous results
        results_container = self.ids.results_container
        results_container.clear_widgets()

        # Show loading message
        loading_label = Label(
            text=f'Searching for tips about {city}...',
            size_hint_y=None,
            height=40,
            color=(238/255, 244/255, 237/255, 1)  # Light text
        )
        results_container.add_widget(loading_label)

        # Try to get tips from API
        api_client = get_api_client()
        tips = []

        try:
            # Get location from API
            location = api_client.get_location_by_name(city, country)
            if location:
                tips_data = api_client.get_location_tips(location['id'])

                # Extract tip texts
                for tip_data in tips_data:
                    tip_text = tip_data.get('translated_text') or tip_data.get('tip_text', '')
                    if tip_text:
                        tips.append(tip_text)
        except Exception as e:
            print(f"Error fetching tips from API: {e}")

        # Clear loading message
        results_container.clear_widgets()

        if not tips:
            # Show no results message
            no_results = Label(
                text=f'No tips found for {city} yet.',
                size_hint_y=None,
                height=80,
                color=(238/255, 244/255, 237/255, 1),
                halign='center'
            )
            no_results.bind(size=no_results.setter('text_size'))
            results_container.add_widget(no_results)
        else:
            # Display tips
            for tip in tips:
                # Create card for each tip
                tip_card = BoxLayout(
                    orientation='vertical',
                    padding=16,
                    spacing=8,
                    size_hint_y=None,
                    height=100
                )

                # White background with rounded corners
                from kivy.graphics import Color, RoundedRectangle
                with tip_card.canvas.before:
                    Color(1, 1, 1, 1)
                    tip_card.bg_rect = RoundedRectangle(
                        pos=tip_card.pos,
                        size=tip_card.size,
                        radius=[12]
                    )

                def update_rect(instance, value):
                    instance.bg_rect.pos = instance.pos
                    instance.bg_rect.size = instance.size

                tip_card.bind(pos=update_rect, size=update_rect)

                tip_label = Label(
                    text=tip,
                    color=(11/255, 37/255, 69/255, 1),  # Dark text on white card
                    halign='left',
                    valign='top',
                    text_size=(Window.width - 120, None)
                )
                tip_label.bind(size=tip_label.setter('text_size'))

                tip_card.add_widget(tip_label)
                results_container.add_widget(tip_card)


class SettingsScreen(Screen):
    """Settings screen with dark mode toggle"""

    def toggle_dark_mode(self):
        """Toggle dark mode (placeholder for now)"""
        # In a full implementation, this would switch between COLOR_BG_DARK and COLOR_BG_LIGHT
        # For now, we just print the state
        is_dark = self.ids.dark_mode_toggle.active
        print(f"Dark mode: {'ON' if is_dark else 'OFF'}")

        # TODO: Implement actual dark mode switching
        # This would require dynamically changing all canvas.before colors
        # Or reloading the .kv file with different color variables

    def edit_profile(self):
        """Navigate back to signup page 1 to edit profile"""
        self.manager.current = 'signup_page1'


class TravelBuddyApp(App):
    """Main application class"""

    def build(self):
        # Load KV file
        Builder.load_file('main.kv')

        # Set window size (useful for development)
        Window.size = (400, 650)

        # Create screen manager with smooth transitions
        sm = ScreenManager(transition=SlideTransition(duration=0.3))

        # Add screens
        sm.add_widget(SignupPage1(name='signup_page1'))
        sm.add_widget(SignupPage2(name='signup_page2'))
        sm.add_widget(TravelScreen(name='travel'))
        sm.add_widget(SettingsScreen(name='settings'))

        # Check if user data exists
        if os.path.exists('user_data.json'):
            sm.current = 'travel'
        else:
            sm.current = 'signup_page1'

        return sm


if __name__ == '__main__':
    TravelBuddyApp().run()

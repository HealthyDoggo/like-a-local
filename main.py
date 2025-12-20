"""
TravelBuddy - A travel companion app
Helps users discover local insights about their dream destinations
"""

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import json
import os
from api_client import get_api_client

# migrate to kv
class SignupScreen(Screen):
    """Screen for user signup and survey"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'signup'
        pass
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # Title
        title = Label(
            text='Welcome to TravelBuddy!',
            font_size='32sp',
            size_hint_y=0.15,
            bold=True
        )
        layout.add_widget(title)
        
        # Survey form
        form_layout = GridLayout(cols=1, spacing=15, size_hint_y=0.7)
        
        # Name
        form_layout.add_widget(Label(text='What\'s your name?', size_hint_y=None, height=40))
        self.name_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=40,
            hint_text='Enter your name'
        )
        form_layout.add_widget(self.name_input)
        
        # Hometown
        form_layout.add_widget(Label(text='Where are you from? (Hometown)', size_hint_y=None, height=40))
        self.hometown_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=40,
            hint_text='e.g., San Francisco, USA'
        )
        form_layout.add_widget(self.hometown_input)
        
        # Current location
        form_layout.add_widget(Label(text='Where do you currently live?', size_hint_y=None, height=40))
        self.current_location_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=40,
            hint_text='e.g., New York, USA'
        )
        form_layout.add_widget(self.current_location_input)
        
        layout.add_widget(form_layout)
        
        # Submit button
        submit_btn = Button(
            text='Start Exploring',
            size_hint_y=0.15,
            background_color=(0.2, 0.6, 0.8, 1),
            font_size='20sp'
        )
        submit_btn.bind(on_press=self.submit_signup)
        layout.add_widget(submit_btn)
        
        self.add_widget(layout)
    
    def submit_signup(self, instance):
        """Save user data and navigate to destinations screen"""
        user_data = {
            'name': self.name_input.text,
            'hometown': self.hometown_input.text,
            'current_location': self.current_location_input.text
        }
        
        # Save user data
        with open('user_data.json', 'w') as f:
            json.dump(user_data, f)
        
        # Navigate to destinations screen
        self.manager.current = 'destinations'


class DestinationsScreen(Screen):
    """Screen showing available destinations"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'destinations'
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        
        title = Label(
            text='Where do you want to travel?',
            font_size='24sp',
            bold=True,
            size_hint_x=0.8
        )
        header_layout.add_widget(title)
        
        # Back button (to edit profile)
        back_btn = Button(
            text='Edit Profile',
            size_hint_x=0.2,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'signup'))
        header_layout.add_widget(back_btn)
        
        layout.add_widget(header_layout)
        
        # Scrollable destination list
        scroll = ScrollView(size_hint=(1, 0.9))
        self.destinations_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=10
        )
        self.destinations_layout.bind(minimum_height=self.destinations_layout.setter('height'))
        
        scroll.add_widget(self.destinations_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Load destinations when screen is displayed"""
        self.load_destinations()
    
    def load_destinations(self):
        """Load and display destinations"""
        self.destinations_layout.clear_widgets()
        
        # Load destinations from JSON file
        destinations = self.load_destinations_data()
        
        for dest_id, dest_data in destinations.items():
            # Create destination button
            btn_layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=120,
                padding=10
            )
            
            dest_btn = Button(
                text=f"{dest_data['name']}\n{dest_data['country']}",
                font_size='18sp',
                background_color=(0.2, 0.6, 0.8, 1),
                size_hint_y=None,
                height=100
            )
            dest_btn.bind(on_press=lambda x, d=dest_id: self.show_destination_details(d))
            
            btn_layout.add_widget(dest_btn)
            self.destinations_layout.add_widget(btn_layout)
    
    def load_destinations_data(self):
        """Load destinations from JSON file"""
        data_file = 'data/destinations.json'
        
        # Create default data if file doesn't exist
        if not os.path.exists(data_file):
            os.makedirs('data', exist_ok=True)
            default_data = {
                'tokyo': {
                    'name': 'Tokyo',
                    'country': 'Japan',
                    'tips': [
                        'Learn a few basic Japanese phrases - locals really appreciate it!',
                        'Get a Suica or Pasmo card for easy train travel',
                        'Visit small ramen shops in residential areas for authentic meals',
                        'Convenience stores (konbini) are amazing and have great food',
                        'Take your shoes off when entering homes and some restaurants'
                    ]
                },
                'paris': {
                    'name': 'Paris',
                    'country': 'France',
                    'tips': [
                        'Say "Bonjour" when entering any shop - it\'s considered polite',
                        'The best croissants are in small neighborhood bakeries',
                        'Museum pass can save you time and money',
                        'Metro is efficient but watch out for pickpockets',
                        'Restaurants outside tourist areas are cheaper and more authentic'
                    ]
                },
                'barcelona': {
                    'name': 'Barcelona',
                    'country': 'Spain',
                    'tips': [
                        'Dinner is typically eaten after 9 PM - restaurants open late',
                        'Book Sagrada Familia tickets online in advance',
                        'Try tapas at local bars in El Born or Gracia neighborhoods',
                        'Learn the difference between Catalan and Spanish culture',
                        'Beach is nice but there are better beaches outside the city'
                    ]
                },
                'nyc': {
                    'name': 'New York City',
                    'country': 'USA',
                    'tips': [
                        'Walk fast and keep to the right on sidewalks',
                        'Get a MetroCard for the subway - fastest way around',
                        'Explore neighborhoods beyond Manhattan for authentic food',
                        'Free museums on certain days - check websites',
                        'Don\'t eat in Times Square - overpriced tourist traps'
                    ]
                },
                'bali': {
                    'name': 'Bali',
                    'country': 'Indonesia',
                    'tips': [
                        'Dress modestly when visiting temples',
                        'Negotiate prices at markets (except grocery stores)',
                        'Rent a scooter to get around like locals',
                        'Avoid Kuta if you want authentic Balinese experience',
                        'Try local warungs (small restaurants) for cheap amazing food'
                    ]
                }
            }
            
            with open(data_file, 'w') as f:
                json.dump(default_data, f, indent=2)
            
            return default_data
        else:
            with open(data_file, 'r') as f:
                return json.load(f)
    
    def show_destination_details(self, dest_id):
        """Navigate to details screen for selected destination"""
        details_screen = self.manager.get_screen('details')
        details_screen.load_destination(dest_id)
        self.manager.current = 'details'


class DetailsScreen(Screen):
    """Screen showing tips for a specific destination"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'details'
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.add_widget(self.layout)
    
    def load_destination(self, dest_id):
        """Load and display destination details"""
        self.layout.clear_widgets()
        self.dest_id = dest_id
        
        # Load destination data from local JSON
        with open('data/destinations.json', 'r') as f:
            destinations = json.load(f)
        
        dest_data = destinations.get(dest_id, {})
        dest_name = dest_data.get('name', 'Unknown')
        dest_country = dest_data.get('country', '')
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        
        back_btn = Button(
            text='← Back',
            size_hint_x=0.2,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'destinations'))
        header_layout.add_widget(back_btn)
        
        title = Label(
            text=f"{dest_name}, {dest_country}",
            font_size='24sp',
            bold=True,
            size_hint_x=0.8
        )
        header_layout.add_widget(title)
        
        self.layout.add_widget(header_layout)
        
        # Tips section
        tips_label = Label(
            text='Local Tips & Insights',
            font_size='20sp',
            bold=True,
            size_hint_y=0.08
        )
        self.layout.add_widget(tips_label)
        
        # Scrollable tips
        scroll = ScrollView(size_hint=(1, 0.7))
        tips_layout = GridLayout(
            cols=1,
            spacing=15,
            size_hint_y=None,
            padding=10
        )
        tips_layout.bind(minimum_height=tips_layout.setter('height'))
        
        # Try to fetch tips from API first
        api_client = get_api_client()
        api_tips = []
        
        try:
            # Get location from API
            location = api_client.get_location_by_name(dest_name, dest_country)
            if location:
                api_tips = api_client.get_location_tips(location['id'])
        except Exception as e:
            print(f"Error fetching tips from API: {e}")
        
        # Combine API tips and local tips
        all_tips = []
        
        # Add API tips (processed tips)
        for tip_data in api_tips:
            tip_text = tip_data.get('translated_text') or tip_data.get('tip_text', '')
            if tip_text:
                all_tips.append(tip_text)
        
        # Add local tips if no API tips found
        if not all_tips:
            all_tips = dest_data.get('tips', [])
        
        # Display tips
        for tip in all_tips:
            tip_box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=80,
                padding=10
            )
            
            bullet = Label(
                text='💡',
                font_size='24sp',
                size_hint_x=0.1
            )
            tip_box.add_widget(bullet)
            
            tip_label = Label(
                text=tip,
                font_size='16sp',
                text_size=(Window.width * 0.7, None),
                halign='left',
                valign='middle',
                size_hint_x=0.9
            )
            tip_label.bind(size=tip_label.setter('text_size'))
            tip_box.add_widget(tip_label)
            
            tips_layout.add_widget(tip_box)
        
        scroll.add_widget(tips_layout)
        self.layout.add_widget(scroll)
        
        # Add tip submission section
        submit_layout = BoxLayout(orientation='vertical', size_hint_y=0.2, padding=10, spacing=5)
        
        submit_label = Label(
            text='Submit a Tip',
            font_size='16sp',
            bold=True,
            size_hint_y=0.3
        )
        submit_layout.add_widget(submit_label)
        
        tip_input_layout = BoxLayout(orientation='horizontal', size_hint_y=0.4, spacing=5)
        self.tip_input = TextInput(
            multiline=True,
            hint_text='Enter your tip in any language...',
            size_hint_x=0.75
        )
        tip_input_layout.add_widget(self.tip_input)
        
        submit_btn = Button(
            text='Submit',
            size_hint_x=0.25,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        submit_btn.bind(on_press=self.submit_tip)
        tip_input_layout.add_widget(submit_btn)
        
        submit_layout.add_widget(tip_input_layout)
        self.layout.add_widget(submit_layout)
    
    def submit_tip(self, instance):
        """Submit a tip to the backend"""
        tip_text = self.tip_input.text.strip()
        if not tip_text:
            return
        
        # Get destination data
        with open('data/destinations.json', 'r') as f:
            destinations = json.load(f)
        
        dest_data = destinations.get(self.dest_id, {})
        dest_name = dest_data.get('name', '')
        dest_country = dest_data.get('country', '')
        
        # Submit to API
        api_client = get_api_client()
        try:
            result = api_client.submit_tip(
                tip_text=tip_text,
                location_name=dest_name,
                location_country=dest_country
            )
            if result:
                self.tip_input.text = ''
                # Show success message (could be improved with a popup)
                print(f"Tip submitted successfully! ID: {result.get('id')}")
            else:
                print("Failed to submit tip. Check API connection.")
        except Exception as e:
            print(f"Error submitting tip: {e}")


class TravelBuddyApp(App):
    """Main application class"""
    
    def build(self):
        # Set window size (useful for development)
        Builder.load_file('main.kv')
        Window.size = (400, 650)
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(SignupScreen())
        sm.add_widget(DestinationsScreen())
        sm.add_widget(DetailsScreen())
        
        # Check if user data exists
        if os.path.exists('user_data.json'):
            sm.current = 'destinations'
        else:
            sm.current = 'signup'
        
        return sm


if __name__ == '__main__':
    TravelBuddyApp().run()

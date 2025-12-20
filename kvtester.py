from kivy.lang import Builder
from kivy.app import App

class TravelBuddyApp(App):
    def build(self):
        return Builder.load_file('main.kv')

if __name__ == '__main__':
    TravelBuddyApp().run()
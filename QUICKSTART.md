# TravelBuddy - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Run the Setup Script

```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies (Kivy, KivyMD, etc.)
- Set everything up for you

### Step 2: Activate the Virtual Environment

```bash
source venv/bin/activate
```

You'll see `(venv)` in your terminal prompt when activated.

### Step 3: Run the App

```bash
python main.py
```

## 🎯 What to Expect

### First Time Running

1. **Signup Screen** will appear
   - Enter your name
   - Enter your hometown
   - Enter where you currently live
   - Click "Start Exploring"

2. **Destinations Screen** shows travel destinations
   - Click any destination to see local tips
   - Use "Edit Profile" to change your info

3. **Details Screen** shows tips from locals
   - Read insider knowledge about the destination
   - Click "← Back" to browse more destinations

## 📝 Sample Destinations Included

The app comes with 5 sample destinations:
- 🗼 **Tokyo, Japan** - Tech, food, and culture tips
- 🗼 **Paris, France** - Museum, dining, and etiquette advice
- 🏖️ **Barcelona, Spain** - Catalan culture and nightlife
- 🗽 **New York City, USA** - Transit and neighborhood guides
- 🏝️ **Bali, Indonesia** - Temple etiquette and local experiences

## 🛠️ Customization

### Add Your Own Destinations

Edit `data/destinations.json` (created automatically on first run):

```json
{
  "london": {
    "name": "London",
    "country": "United Kingdom",
    "tips": [
      "Stand on the right side of escalators",
      "Oyster card is essential for the Tube",
      "Free museums everywhere!",
      "Pub culture is real - try a Sunday roast",
      "Weather changes fast - always carry an umbrella"
    ]
  }
}
```

### Customize the UI

The app uses Kivy's styling system. Key parameters in `main.py`:

- **Window size**: `Window.size = (400, 650)` - Change for different screen sizes
- **Colors**: `background_color=(R, G, B, A)` - Values between 0-1
- **Font sizes**: `font_size='24sp'` - Adjust for readability

## 🔄 Development Workflow

```bash
# 1. Activate virtual environment (if not already active)
source venv/bin/activate

# 2. Make your changes to main.py or data files

# 3. Run the app to test
python main.py

# 4. When done for the day
deactivate
```

## 🐛 Troubleshooting

### "Command not found: python3"
- Install Python 3.8+ from python.org or use `brew install python3`

### Kivy installation fails
- On macOS, you might need: `brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer`
- On Ubuntu: `sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev`

### Window doesn't appear
- Check if you're running in SSH or remote terminal
- Kivy requires a display server (X11, Wayland, or native display)

### "ModuleNotFoundError: No module named 'kivy'"
- Make sure virtual environment is activated: `source venv/bin/activate`
- You should see `(venv)` in your terminal prompt

## 📚 Next Steps

1. **Read ARCHITECTURE.md** to understand the code structure
2. **Customize destinations** in `data/destinations.json`
3. **Experiment with UI** - change colors, sizes, layouts
4. **Add features** - see enhancement ideas in ARCHITECTURE.md

## 💡 Tips for Development

- The app window is sized like a mobile phone (400x650) for easier testing
- User data is saved in `user_data.json` - delete it to reset signup
- The app automatically creates sample destinations on first run
- Hot tip: Restart the app after changing data files

## 🎨 Making It Your Own

Some ideas to customize:
- Change the color scheme to match your brand
- Add more fields to the signup (travel preferences, budget, etc.)
- Create destination categories (beach, city, adventure, etc.)
- Add photos or icons to destinations
- Implement a search feature

Enjoy building with TravelBuddy! 🌍✈️





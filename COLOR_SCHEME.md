# Color Scheme Configuration

## How to Change Colors

The color scheme for TravelBuddy can be easily changed by editing the color variables at the top of the `main.kv` file.

### Location

Open `main.kv` and find the color palette section at lines 7-13:

```kv
#:set COLOR_PRIMARY   (60/255, 127/255, 204/255, 1)   # 3C7FCC - Bright blue
#:set COLOR_SECONDARY (33/255, 75/255, 135/255, 1)    # 214B87 - Medium blue
#:set COLOR_DARK      (11/255, 37/255, 69/255, 1)     # 0B2545 - Dark blue
#:set COLOR_LIGHT     (141/255, 169/255, 196/255, 1)  # 8DA9C4 - Light blue
#:set COLOR_BG        (238/255, 244/255, 237/255, 1)  # EEF4ED - Off-white
#:set COLOR_TEXT_DARK (11/255, 37/255, 69/255, 1)     # 0B2545
#:set COLOR_TEXT_LIGHT (238/255, 244/255, 237/255, 1) # EEF4ED
```

### Current Color Scheme

Based on the coolors.co palette you provided:

| Color Variable    | Hex Code | RGB Values      | Usage                                    |
|-------------------|----------|-----------------|------------------------------------------|
| COLOR_PRIMARY     | #3C7FCC  | 60, 127, 204    | Main accent color (buttons, headings)    |
| COLOR_SECONDARY   | #214B87  | 33, 75, 135     | Secondary elements (bottom nav)          |
| COLOR_DARK        | #0B2545  | 11, 37, 69      | Dark accents                             |
| COLOR_LIGHT       | #8DA9C4  | 141, 169, 196   | Light accents (chips, secondary buttons) |
| COLOR_BG          | #EEF4ED  | 238, 244, 237   | Background color                         |
| COLOR_TEXT_DARK   | #0B2545  | 11, 37, 69      | Text on light backgrounds                |
| COLOR_TEXT_LIGHT  | #EEF4ED  | 238, 244, 237   | Text on dark backgrounds                 |

### How to Convert Hex to Kivy Format

Kivy uses normalized RGBA values (0.0 to 1.0). To convert from hex:

1. Convert hex to RGB (0-255)
2. Divide each value by 255
3. Add alpha channel (usually 1 for opaque)

**Example:** Converting `#FF5733` (coral red)
- Hex: `#FF5733`
- RGB: `255, 87, 51`
- Kivy format: `(255/255, 87/255, 51/255, 1)`

### Quick Color Change Examples

#### Purple/Pink Theme
```kv
#:set COLOR_PRIMARY   (156/255, 39/255, 176/255, 1)   # 9C27B0 - Purple
#:set COLOR_SECONDARY (233/255, 30/255, 99/255, 1)    # E91E63 - Pink
#:set COLOR_DARK      (74/255, 20/255, 140/255, 1)    # 4A148C - Deep purple
#:set COLOR_LIGHT     (240/255, 98/255, 146/255, 1)   # F06292 - Light pink
#:set COLOR_BG        (250/255, 250/255, 250/255, 1)  # FAFAFA - Light gray
```

#### Green/Teal Theme
```kv
#:set COLOR_PRIMARY   (0/255, 150/255, 136/255, 1)    # 009688 - Teal
#:set COLOR_SECONDARY (76/255, 175/255, 80/255, 1)    # 4CAF50 - Green
#:set COLOR_DARK      (0/255, 77/255, 64/255, 1)      # 004D40 - Dark teal
#:set COLOR_LIGHT     (129/255, 199/255, 132/255, 1)  # 81C784 - Light green
#:set COLOR_BG        (245/255, 245/255, 245/255, 1)  # F5F5F5 - Off-white
```

#### Dark Mode
```kv
#:set COLOR_PRIMARY   (33/255, 150/255, 243/255, 1)   # 2196F3 - Blue
#:set COLOR_SECONDARY (63/255, 81/255, 181/255, 1)    # 3F51B5 - Indigo
#:set COLOR_DARK      (18/255, 18/255, 18/255, 1)     # 121212 - Almost black
#:set COLOR_LIGHT     (97/255, 97/255, 97/255, 1)     # 616161 - Gray
#:set COLOR_BG        (30/255, 30/255, 30/255, 1)     # 1E1E1E - Dark gray
#:set COLOR_TEXT_DARK (255/255, 255/255, 255/255, 1)  # FFFFFF - White
#:set COLOR_TEXT_LIGHT (255/255, 255/255, 255/255, 1) # FFFFFF - White
```

### Tips

1. **Contrast**: Ensure good contrast between text and background colors for readability
2. **Consistency**: PRIMARY should be your main brand color, SECONDARY for accents
3. **Testing**: After changing colors, restart the app to see changes
4. **Online Tools**: Use [coolors.co](https://coolors.co) to generate harmonious color palettes

### Applying Changes

After editing `main.kv`:
1. Save the file
2. Restart the app with `python main.py`
3. The new colors will be applied throughout the entire interface

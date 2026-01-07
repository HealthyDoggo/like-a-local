## User Flow

## UI Design

### Signup Page 1 - Location Selection

**Purpose:** Collect user's home location to provide relevant local insights

**Components:**
- Dark blue background (COLOR_BG_DARK)
- Large serif heading: "Where are you from?" (Georgia, 32sp, centered)
- **LocationSelector widget** - Reusable country/city selection component with:
  - Country input field with autocomplete dropdown
  - City input field (enabled after country selection) with autocomplete dropdown
  - Animated dropdown panels that expand on typing (min 2 characters)
  - Dropdown items styled with COLOR_DARK background
- "Next" button (RoundedButton) to proceed to Signup Page 2

**Interaction:**
1. User types in country field → autocomplete dropdown appears
2. User selects country → city field becomes enabled, dropdown closes
3. User types in city field → autocomplete dropdown shows cities from selected country
4. User selects city → dropdown closes
5. User clicks "Next" → validates both fields are selected → proceeds to Signup Page 2

### Signup Page 2 - Local Annoyances

**Purpose:** Collect user's perspective as a local about tourist behavior

**Components:**
- Dark blue background (COLOR_BG_DARK)
- Large serif heading: "What would you like tourists to do less?" (Georgia, 28sp, centered)
- Three initial text input fields (only first is required)
- "+ Add More" button to dynamically add additional input fields
- "Submit" button at bottom

**Interaction:**
1. User fills in at least one annoyance (required)
2. Optionally fills additional fields
3. Can click "+ Add More" to add extra text fields
4. Clicks "Submit" → saves to user_data.json → proceeds to Travel Screen

**Data Saved:**
- Country and city from Signup Page 1
- List of annoyances submitted

### Travel Screen (Home Page)

**Purpose:** Main screen where users search for tips about their travel destination

**Components:**
- Dark blue background (COLOR_BG_DARK)
- Large serif heading: "Where are you going?" (Georgia, 32sp, centered)
- **LocationSelector widget** (same reusable component as Signup Page 1)
- "Search" button (RoundedButton)
- ScrollView for displaying results
- Bottom navigation bar with Travel (✈️) and Settings (⚙️) buttons

**Interaction:**
1. User selects country and city using LocationSelector
2. Clicks "Search" button
3. Results container shows "Searching tips for {city}..."
4. Backend queries tips from locals about that location
5. Tips displayed ranked by similarity clustering (embedding-based)

### Settings Screen

**Purpose:** App configuration and profile management

**Components:**
- Dark blue background (COLOR_BG_DARK)
- Large serif heading: "Settings" (Georgia, 32sp, centered)
- Dark Mode toggle (currently always on - app uses dark theme)
- "Edit Profile" button → navigates back to Signup Page 1
- About section showing app version
- Bottom navigation bar

**Interaction:**
- Dark mode toggle (placeholder - theme is always dark currently)
- "Edit Profile" allows user to update their home location

---

## Technical Architecture

### Reusable Components

#### LocationSelector Widget
**File:** Defined in main.kv, logic in main.py

**Purpose:** Standardized country/city selection with autocomplete

**Structure:**
```
LocationSelector (BoxLayout)
├── FloatLayout (Country)
│   ├── TextInput (country_input)
│   └── SuggestionPanel (country_panel)
│       └── RecycleView (country_rv)
│           └── SuggestionItem buttons
└── FloatLayout (City)
    ├── TextInput (city_input, disabled until country selected)
    └── SuggestionPanel (city_panel)
        └── RecycleView (city_rv)
            └── SuggestionItem buttons
```

**Key Features:**
- Autocomplete triggers after 2+ characters typed
- Smooth animations (0.3s expand, 0.25s collapse)
- Dropdown height: 70px per item, max 280px (5 items)
- Data binding: RecycleView height = 0 when data is empty
- City field disabled until country is selected
- Returns selection via `get_selection()` method

**Used In:**
- SignupPage1 (id: location_selector)
- TravelScreen (id: location_selector)

### Data Flow

1. **User Location (Signup):**
   - LocationSelector → SignupPage1.go_to_page2() → App.temp_country/temp_city → SignupPage2.submit_signup() → user_data.json

2. **Travel Search:**
   - LocationSelector → TravelScreen.search_city() → Backend API → Results displayed

### App Initialization

- If `user_data.json` exists → Start at TravelScreen
- If no user data → Start at SignupPage1 (signup flow)
"""Comprehensive database seeding script with diverse tips across multiple cities"""
import sys
import os
import json
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import Location, Tip
from backend.config import settings


# Tip templates by category - realistic travel tips
TIP_TEMPLATES = {
    "Food & Dining": [
        "Don't tip in {city} - it's not customary and can be considered rude.",
        "Try the local street food at {market} - it's authentic and delicious.",
        "Book restaurants in advance, especially on weekends in {city}.",
        "Lunch is usually the main meal in {city}, with dinner served late.",
        "Ask for the local specialty at any restaurant - they'll appreciate it.",
        "Food markets open early, around 6-7 AM, for the freshest produce.",
        "Many traditional restaurants only accept cash, so come prepared.",
        "The best local cuisine is often found away from tourist areas.",
        "Try eating where locals eat - if it's crowded, it's usually good.",
        "Don't be afraid to try something new - local specialties are worth it!",
        "Water is usually safe to drink, but locals often prefer bottled.",
        "Vegetarian options are becoming more common but may be limited.",
        "Learn a few food-related phrases - it helps with ordering.",
        "Street vendors are generally safe and offer authentic local flavors.",
        "Tipping isn't expected, but small change is appreciated for great service."
    ],
    "Getting Around": [
        "Get a transit card on arrival - it's much cheaper than individual tickets.",
        "Download the local transit app - it has real-time schedules and routes.",
        "Avoid rush hour (7-9 AM, 5-7 PM) on public transport if possible.",
        "Taxis should use meters - insist on it or agree on price beforehand.",
        "Walking is often the best way to explore the historic center.",
        "Bike rentals are available and a great way to see the city.",
        "The metro is fast and efficient - use it for longer distances.",
        "Keep your phone on silent on public transport.",
        "Buy multi-day passes if you're staying for several days.",
        "Apps like Uber or local alternatives are widely available.",
        "Night buses run after metro hours - check schedules in advance.",
        "Stand on the right on escalators to let others pass on the left.",
        "Public transport is generally very safe, even late at night.",
        "Get a local SIM card for navigation and transport apps.",
        "Airport shuttles are often cheaper and more reliable than taxis."
    ],
    "Culture & Etiquette": [
        "Greet shopkeepers when entering and leaving stores.",
        "Dress modestly when visiting religious sites.",
        "Remove shoes before entering homes and some traditional venues.",
        "It's polite to wait for everyone's food before starting to eat.",
        "Learn basic greetings in the local language - it's appreciated.",
        "Public displays of affection are frowned upon in some areas.",
        "Photography may not be allowed in certain locations - always ask.",
        "Punctuality is important for meetings and reservations.",
        "Handshakes are the standard greeting in business contexts.",
        "Locals appreciate when visitors make an effort to speak the language.",
        "Queuing is taken seriously - don't cut in line.",
        "Eye contact during conversation shows respect and engagement.",
        "Small talk is common and a good way to connect with locals.",
        "Accept hospitality when offered - refusing can be seen as rude.",
        "Be mindful of noise levels, especially in residential areas."
    ],
    "Safety & Health": [
        "Keep copies of important documents separately from the originals.",
        "Pharmacies are well-stocked and pharmacists can help with minor issues.",
        "Emergency number is {emergency} - save it in your phone.",
        "Tap water is safe to drink in most areas.",
        "Travel insurance is highly recommended for medical emergencies.",
        "Petty theft can occur in crowded areas - secure your belongings.",
        "Know the location of your country's embassy or consulate.",
        "Vaccinations aren't required for most travelers, but check current requirements.",
        "Walking at night is generally safe in well-lit, populated areas.",
        "Keep some cash for emergencies - not everywhere accepts cards.",
        "Sun protection is important, especially during summer months.",
        "Air quality can vary - check AQI if you have respiratory issues.",
        "Download offline maps in case you lose internet connection.",
        "Local police are helpful - don't hesitate to ask for assistance.",
        "Register with your embassy if staying for an extended period."
    ],
    "Money & Budget": [
        "Credit cards are widely accepted, but carry some cash.",
        "ATMs are common and usually the best exchange rate.",
        "Notify your bank before traveling to avoid card blocks.",
        "Split bills are usually accommodated at restaurants.",
        "Many museums offer free admission on certain days or times.",
        "Student and senior discounts are often available - always ask.",
        "Book accommodations in advance to get better rates.",
        "Local markets are cheaper than supermarkets for groceries.",
        "Coffee shops and casual eateries are budget-friendly options.",
        "Skip the expensive tourist traps - ask locals for recommendations.",
        "Public transport day passes offer great value for sightseeing.",
        "Bargaining isn't common except at specific markets.",
        "Set a daily budget and track your spending with an app.",
        "Free walking tours are a great way to orient yourself.",
        "Check if your accommodation includes breakfast - it saves money."
    ],
    "Sightseeing": [
        "Visit major attractions early morning or late afternoon to avoid crowds.",
        "Buy tickets online in advance to skip long queues.",
        "Free walking tours offer great insights into local history and culture.",
        "Many museums are free on the first Sunday of the month.",
        "Get the city pass if you plan to visit multiple attractions.",
        "Ask locals for hidden gems - they know the best spots.",
        "Wear comfortable shoes - you'll be doing a lot of walking.",
        "Check opening hours before visiting - they vary by season.",
        "Photography is usually allowed but no flash in museums.",
        "Audio guides are available at most major sites.",
        "Sunset viewpoints are spectacular but can get crowded.",
        "Public parks are perfect for a relaxing break between sightseeing.",
        "Local festivals and events are worth planning your trip around.",
        "Book guided tours for deeper insights into historical sites.",
        "Download offline guides for self-paced exploration."
    ],
    "Accommodation": [
        "Book accommodations in neighborhoods well-connected by public transit.",
        "Check reviews on multiple platforms before booking.",
        "Breakfast included is common and offers good value.",
        "Late check-in should be arranged in advance.",
        "Keep the front desk number handy for any issues.",
        "Ask about luggage storage if you have a late flight.",
        "Quiet hours are typically enforced after 10 PM.",
        "Hotel staff can often get better restaurant reservations.",
        "Check if there's a safe for valuables in your room.",
        "Ask for recommendations from hotel staff - they know the area best.",
        "Some accommodations offer free city maps and transit passes.",
        "Early check-in may be possible if you ask nicely.",
        "Negotiate rates for extended stays directly with the property.",
        "Read cancellation policies carefully before booking.",
        "Local guesthouses offer more authentic experiences than chain hotels."
    ],
    "Shopping": [
        "Major stores accept credit cards, but street markets prefer cash.",
        "Sales tax is often included in displayed prices.",
        "Keep receipts for customs if buying expensive items.",
        "Souvenir shops near attractions are typically overpriced.",
        "Local markets open early and close by early afternoon.",
        "Bargaining is expected at outdoor markets but not in stores.",
        "Quality crafts can be found at artisan cooperatives.",
        "Duty-free shopping at the airport can offer good deals.",
        "Vintage and thrift stores have unique local finds.",
        "Sunday markets are great for local products and atmosphere.",
        "Check if you can get VAT refunds as a tourist.",
        "Support local artisans rather than mass-produced souvenir shops.",
        "Department stores are a safe bet for authentic local brands.",
        "Food items make great portable souvenirs.",
        "Designer goods are often cheaper in their country of origin."
    ],
    "Language": [
        "English is widely spoken in tourist areas.",
        "Learn basic phrases: hello, thank you, excuse me, where is...",
        "Translation apps work well for reading menus and signs.",
        "Locals appreciate any attempt to speak their language.",
        "Many younger people speak English, especially in cities.",
        "Restaurant staff usually have English menus available.",
        "Download offline translation tools before traveling.",
        "Speaking slowly and clearly helps with communication.",
        "Learn numbers 1-10 for shopping and ordering.",
        "Pointing and gestures work when words fail.",
        "Keep a translation app handy for complex situations.",
        "Written addresses are helpful when taking taxis.",
        "Language exchange meetups are fun ways to practice.",
        "Local language schools often offer short tourist courses.",
        "Carry a phrasebook as a backup to digital tools."
    ],
    "Weather & Seasons": [
        "Pack layers - weather can change throughout the day.",
        "Summer is peak tourist season - expect crowds and higher prices.",
        "Shoulder seasons (spring/fall) offer the best value and weather.",
        "Check weather forecasts before planning outdoor activities.",
        "Umbrella is essential - rain can come unexpectedly.",
        "Winter months can be very cold - bring appropriate clothing.",
        "Air conditioning isn't universal - a portable fan can help.",
        "Sunscreen and sunglasses are must-haves in summer.",
        "Indoor attractions are perfect for rainy days.",
        "Book ahead for holiday periods - everything fills up fast.",
        "Local weather patterns can differ from forecasts - ask locals.",
        "Heat waves in summer can be intense - stay hydrated.",
        "Some attractions close during the off-season.",
        "Festival seasons bring crowds but incredible atmosphere.",
        "Check sunrise/sunset times to plan your day effectively."
    ]
}

# City-specific tips that add local flavor
CITY_SPECIFIC_TIPS = {
    "Tokyo": [
        "Get a JR Pass if traveling beyond Tokyo - it pays for itself quickly.",
        "Convenience stores (konbini) have surprisingly good food 24/7.",
        "Train stations can be confusing - arrive early for connections.",
        "Bowing is a respectful greeting - a slight nod is fine for tourists.",
        "Remove shoes at temple entrances and traditional restaurants.",
        "Speaking on phone on trains is considered rude.",
        "Vending machines are everywhere and accept IC cards.",
        "Tsukiji Outer Market is perfect for fresh sushi breakfast."
    ],
    "Paris": [
        "Say 'Bonjour' when entering shops - it's considered polite.",
        "Cafés charge more if you sit rather than stand at the bar.",
        "The Métro is efficient but can be crowded during rush hour.",
        "Museum Pass saves time and money if visiting multiple sites.",
        "Dinner reservations are essential at popular restaurants.",
        "Many shops close on Sundays and Monday mornings.",
        "Free water ('une carafe d'eau') is available at restaurants.",
        "Picnicking in parks is a local tradition - join in!"
    ],
    "Barcelona": [
        "Siesta time (2-5 PM) means many shops close - plan accordingly.",
        "Sagrada Família tickets must be booked weeks in advance.",
        "Beach pickpockets are common - don't bring valuables.",
        "Dinner starts at 9 PM or later - embrace the late schedule.",
        "Las Ramblas is touristy - explore Gothic Quarter instead.",
        "Metro runs until midnight on weekdays, 2 AM on weekends.",
        "Learn the difference between Catalan and Spanish language.",
        "Sunday paella on the beach is a Barcelona tradition."
    ],
    "London": [
        "Oyster card or contactless payment makes transport easy.",
        "Stand on right side of escalators, walk on left.",
        "Many museums and galleries are free - take advantage!",
        "Pubs close early - last orders around 11 PM.",
        "Sunday roast is a must-try British tradition.",
        "Tipping 10-15% is standard in restaurants.",
        "Weather changes frequently - always carry an umbrella.",
        "Theaters offer cheap day tickets - queue early."
    ],
    "New York": [
        "Get a MetroCard for subway and buses - most convenient option.",
        "Walking is often faster than driving in Manhattan.",
        "Brunch is huge here - expect long waits at popular spots.",
        "Tipping 18-20% is standard and expected.",
        "Broadway shows offer lottery tickets for discount prices.",
        "Times Square is overwhelming - see it once then move on.",
        "Food carts and delis offer authentic, affordable meals.",
        "Central Park is massive - rent a bike to explore it."
    ],
    "Rome": [
        "Vatican Museums are huge - book skip-the-line tickets.",
        "Aperitivo (6-8 PM) includes free snacks with drinks.",
        "Cover charge (coperto) at restaurants is standard.",
        "Toss coin in Trevi Fountain for luck and a return visit.",
        "Free water fountains (nasoni) throughout the city.",
        "Sunday mass at Vatican is free but arrive very early.",
        "Metro doesn't reach all sites - be ready to walk.",
        "Gelato should cost €2-3 - avoid neon-colored tourist traps."
    ],
    "Amsterdam": [
        "Rent a bike - it's how locals get around.",
        "Watch for bikes when crossing streets - they have right of way.",
        "Museum Quarter requires several days to explore properly.",
        "Coffee shops sell cannabis - cafés sell coffee!",
        "Canal tours are touristy but worth it at least once.",
        "Many places only accept cards - cash isn't always needed.",
        "Stroopwafels fresh from market stalls are incredible.",
        "Visit during tulip season (April-May) for flower fields."
    ],
    "Bangkok": [
        "Use Grab app for safe, metered taxi service.",
        "Dress modestly when visiting temples - cover shoulders and knees.",
        "Street food is safe and delicious - follow the crowds.",
        "Learn to say 'mai phet' (not spicy) if you can't handle heat.",
        "BTS Skytrain avoids traffic - much faster than taxis.",
        "Bargain at markets but not in malls or restaurants.",
        "Stay hydrated - Bangkok is hot and humid year-round.",
        "River taxis are scenic and practical for sightseeing."
    ]
}


def load_cities_data():
    """Load cities data from JSON file"""
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "cities.json"
    )

    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_or_create_location(db: Session, name: str, country: str, latitude: float = None, longitude: float = None) -> Location:
    """Get existing location or create new one"""
    location = db.query(Location).filter(
        Location.name == name,
        Location.country == country
    ).first()

    if not location:
        location = Location(
            name=name,
            country=country,
            latitude=latitude,
            longitude=longitude
        )
        db.add(location)
        db.commit()
        db.refresh(location)

    return location


def generate_tips_for_city(city_name: str, city_data: dict, country_name: str, tips_per_category: int = 5):
    """Generate diverse tips for a specific city"""
    tips = []

    # Add city-specific tips if available
    if city_name in CITY_SPECIFIC_TIPS:
        for tip_text in CITY_SPECIFIC_TIPS[city_name]:
            tips.append({
                "tip_text": tip_text,
                "location_name": city_name,
                "location_country": country_name,
                "latitude": city_data.get("latitude"),
                "longitude": city_data.get("longitude"),
                "language": "en",
                "category": "Local Tips"
            })

    # Generate tips from templates for each category
    for category, templates in TIP_TEMPLATES.items():
        # Select random templates for this category
        selected_templates = random.sample(
            templates,
            min(tips_per_category, len(templates))
        )

        for template in selected_templates:
            # Replace placeholders if any
            tip_text = template.replace("{city}", city_name)
            tip_text = tip_text.replace("{market}", f"{city_name} Central Market")
            tip_text = tip_text.replace("{emergency}", "112")

            tips.append({
                "tip_text": tip_text,
                "location_name": city_name,
                "location_country": country_name,
                "latitude": city_data.get("latitude"),
                "longitude": city_data.get("longitude"),
                "language": "en",
                "category": category
            })

    return tips


def seed_comprehensive_data(
    max_countries: int = None,
    max_cities_per_country: int = None,
    tips_per_category: int = 3,
    clear_existing: bool = False
):
    """
    Seed database with comprehensive location and tip data

    Args:
        max_countries: Maximum number of countries to seed (None = all)
        max_cities_per_country: Maximum cities per country (None = all)
        tips_per_category: Number of tips to generate per category per city
        clear_existing: Whether to clear existing data first
    """
    db = SessionLocal()

    try:
        # Clear existing data if requested
        if clear_existing:
            print("⚠️  Clearing existing data...")
            db.query(Tip).delete()
            db.query(Location).delete()
            db.commit()
            print("✅ Cleared existing data")

        # Load cities data
        print("📂 Loading cities data...")
        cities_data = load_cities_data()
        countries = cities_data["countries"]

        if max_countries:
            countries = countries[:max_countries]

        print(f"🌍 Processing {len(countries)} countries...")

        total_locations = 0
        total_tips = 0

        for country in countries:
            country_name = country["name"]
            cities = country["cities"]

            if max_cities_per_country:
                cities = cities[:max_cities_per_country]

            print(f"\n📍 {country_name} ({len(cities)} cities)")

            for city_data in cities:
                city_name = city_data["name"]

                # Create or get location
                location = get_or_create_location(
                    db,
                    city_name,
                    country_name,
                    city_data.get("latitude"),
                    city_data.get("longitude")
                )
                total_locations += 1

                # Generate tips for this city
                tips = generate_tips_for_city(
                    city_name,
                    city_data,
                    country_name,
                    tips_per_category
                )

                # Create tip records
                for tip_data in tips:
                    tip = Tip(
                        tip_text=tip_data["tip_text"],
                        location_id=location.id,
                        original_language=tip_data.get("language", "en"),
                        status="pending"
                    )
                    db.add(tip)
                    total_tips += 1

                print(f"   ✓ {city_name}: {len(tips)} tips")

        # Commit all changes
        db.commit()

        print(f"\n{'='*60}")
        print(f"✅ Seeding complete!")
        print(f"   📍 Locations created: {total_locations}")
        print(f"   💡 Tips created: {total_tips}")
        print(f"   📊 Categories: {len(TIP_TEMPLATES)}")
        print(f"{'='*60}")

        # Show database summary
        pending_count = db.query(Tip).filter(Tip.status == "pending").count()
        processed_count = db.query(Tip).filter(Tip.status == "processed").count()

        print(f"\n📈 Database summary:")
        print(f"   Pending tips: {pending_count}")
        print(f"   Processed tips: {processed_count}")
        print(f"   Total tips: {pending_count + processed_count}")
        print(f"   Total locations: {db.query(Location).count()}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed database with comprehensive location and tip data"
    )
    parser.add_argument(
        "--countries",
        type=int,
        default=None,
        help="Maximum number of countries to process (default: all)"
    )
    parser.add_argument(
        "--cities",
        type=int,
        default=None,
        help="Maximum cities per country (default: all)"
    )
    parser.add_argument(
        "--tips-per-category",
        type=int,
        default=3,
        help="Number of tips per category per city (default: 3)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before seeding (WARNING: deletes all tips and locations!)"
    )

    args = parser.parse_args()

    print("🌟 TravelBuddy Comprehensive Data Seeder 🌟\n")

    if args.clear:
        confirm = input("⚠️  This will DELETE all existing tips and locations. Continue? (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ Seeding cancelled")
            sys.exit(0)

    seed_comprehensive_data(
        max_countries=args.countries,
        max_cities_per_country=args.cities,
        tips_per_category=args.tips_per_category,
        clear_existing=args.clear
    )

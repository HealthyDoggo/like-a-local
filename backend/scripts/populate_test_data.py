"""Script to populate database with test tips for processing"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import Location, Tip
from backend.config import settings


# Sample tips in various languages
TEST_TIPS = [
    # English tips
    {
        "tip_text": "Visit the local markets early in the morning for the freshest produce and best prices.",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "en"
    },
    {
        "tip_text": "Learn basic Japanese phrases - locals really appreciate the effort!",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "en"
    },
    {
        "tip_text": "Get a Suica card for easy train travel around the city.",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "en"
    },
    
    # Spanish tips
    {
        "tip_text": "Cena después de las 9 PM - los restaurantes abren tarde en Barcelona.",
        "location_name": "Barcelona",
        "location_country": "Spain",
        "language": "es"
    },
    {
        "tip_text": "Reserva las entradas para la Sagrada Familia en línea con anticipación.",
        "location_name": "Barcelona",
        "location_country": "Spain",
        "language": "es"
    },
    {
        "tip_text": "Prueba las tapas en los bares locales de El Born o Gracia.",
        "location_name": "Barcelona",
        "location_country": "Spain",
        "language": "es"
    },
    {
        "tip_text": "Aprende la diferencia entre la cultura catalana y española.",
        "location_name": "Barcelona",
        "location_country": "Spain",
        "language": "es"
    },
    
    # French tips
    {
        "tip_text": "Dites 'Bonjour' en entrant dans n'importe quel magasin - c'est considéré comme poli.",
        "location_name": "Paris",
        "location_country": "France",
        "language": "fr"
    },
    {
        "tip_text": "Les meilleurs croissants se trouvent dans les petites boulangeries de quartier.",
        "location_name": "Paris",
        "location_country": "France",
        "language": "fr"
    },
    {
        "tip_text": "Le pass musée peut vous faire gagner du temps et de l'argent.",
        "location_name": "Paris",
        "location_country": "France",
        "language": "fr"
    },
    {
        "tip_text": "Le métro est efficace mais attention aux pickpockets.",
        "location_name": "Paris",
        "location_country": "France",
        "language": "fr"
    },
    
    # German tips
    {
        "tip_text": "Besuchen Sie die lokalen Märkte am frühen Morgen für frische Produkte.",
        "location_name": "Berlin",
        "location_country": "Germany",
        "language": "de"
    },
    {
        "tip_text": "Lernen Sie ein paar grundlegende deutsche Phrasen - die Einheimischen schätzen es wirklich!",
        "location_name": "Berlin",
        "location_country": "Germany",
        "language": "de"
    },
    
    # Japanese tips
    {
        "tip_text": "朝早く地元の市場を訪れて、新鮮な食材と最良の価格を手に入れましょう。",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "ja"
    },
    {
        "tip_text": "基本的な日本語のフレーズを学びましょう - 地元の人々は本当に感謝します！",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "ja"
    },
    
    # Chinese tips
    {
        "tip_text": "早上参观当地市场，购买最新鲜的农产品和最优惠的价格。",
        "location_name": "Beijing",
        "location_country": "China",
        "language": "zh"
    },
    {
        "tip_text": "学习一些基本的中文短语 - 当地人真的很感激！",
        "location_name": "Beijing",
        "location_country": "China",
        "language": "zh"
    },
    
    # Italian tips
    {
        "tip_text": "Visita i mercati locali la mattina presto per i prodotti più freschi.",
        "location_name": "Rome",
        "location_country": "Italy",
        "language": "it"
    },
    {
        "tip_text": "Impara alcune frasi italiane di base - i locali lo apprezzano davvero!",
        "location_name": "Rome",
        "location_country": "Italy",
        "language": "it"
    },
    
    # Portuguese tips
    {
        "tip_text": "Visite os mercados locais de manhã cedo para os produtos mais frescos.",
        "location_name": "Lisbon",
        "location_country": "Portugal",
        "language": "pt"
    },
    
    # Russian tips
    {
        "tip_text": "Посетите местные рынки рано утром для самых свежих продуктов.",
        "location_name": "Moscow",
        "location_country": "Russia",
        "language": "ru"
    },
    
    # Arabic tips
    {
        "tip_text": "قم بزيارة الأسواق المحلية في الصباح الباكر للحصول على المنتجات الطازجة.",
        "location_name": "Cairo",
        "location_country": "Egypt",
        "language": "ar"
    },
    
    # Hindi tips
    {
        "tip_text": "सुबह जल्दी स्थानीय बाजारों में जाएं ताकि ताज़ी उपज और सर्वोत्तम कीमतें मिल सकें।",
        "location_name": "Delhi",
        "location_country": "India",
        "language": "hi"
    },
    
    # Thai tips
    {
        "tip_text": "ไปตลาดท้องถิ่นในตอนเช้าตรู่เพื่อผลผลิตที่สดใหม่และราคาที่ดีที่สุด",
        "location_name": "Bangkok",
        "location_country": "Thailand",
        "language": "th"
    },
    
    # Indonesian tips
    {
        "tip_text": "Kunjungi pasar lokal di pagi hari untuk produk terbaru dan harga terbaik.",
        "location_name": "Bali",
        "location_country": "Indonesia",
        "language": "id"
    },
    
    # Vietnamese tips
    {
        "tip_text": "Thăm các chợ địa phương vào sáng sớm để có sản phẩm tươi nhất và giá tốt nhất.",
        "location_name": "Ho Chi Minh City",
        "location_country": "Vietnam",
        "language": "vi"
    },
    
    # Korean tips
    {
        "tip_text": "가장 신선한 농산물과 최고의 가격을 위해 이른 아침에 현지 시장을 방문하세요.",
        "location_name": "Seoul",
        "location_country": "South Korea",
        "language": "ko"
    },
]


def get_or_create_location(db: Session, name: str, country: str) -> Location:
    """Get existing location or create new one"""
    location = db.query(Location).filter(
        Location.name == name,
        Location.country == country
    ).first()
    
    if not location:
        location = Location(name=name, country=country)
        db.add(location)
        db.commit()
        db.refresh(location)
        print(f"Created location: {name}, {country}")
    
    return location


def create_tip(db: Session, tip_data: dict, location: Location) -> Tip:
    """Create a tip in the database"""
    tip = Tip(
        tip_text=tip_data["tip_text"],
        location_id=location.id,
        original_language=tip_data.get("language", "en"),
        status="pending"
    )
    db.add(tip)
    return tip


def populate_database(num_tips: int = None):
    """Populate database with test tips"""
    db = SessionLocal()
    
    try:
        print(f"Populating database with test tips...")
        print(f"Total tips available: {len(TEST_TIPS)}")
        
        tips_to_add = TEST_TIPS
        if num_tips:
            tips_to_add = TEST_TIPS[:num_tips]
            print(f"Adding {num_tips} tips...")
        
        created_count = 0
        location_cache = {}
        
        for tip_data in tips_to_add:
            # Get or create location
            loc_key = (tip_data["location_name"], tip_data["location_country"])
            if loc_key not in location_cache:
                location = get_or_create_location(
                    db,
                    tip_data["location_name"],
                    tip_data["location_country"]
                )
                location_cache[loc_key] = location
            else:
                location = location_cache[loc_key]
            
            # Create tip
            tip = create_tip(db, tip_data, location)
            created_count += 1
        
        # Commit all tips
        db.commit()
        
        print(f"\n✅ Successfully created {created_count} tips")
        print(f"   Locations: {len(location_cache)}")
        
        # Show summary
        pending_count = db.query(Tip).filter(Tip.status == "pending").count()
        processed_count = db.query(Tip).filter(Tip.status == "processed").count()
        
        print(f"\nDatabase summary:")
        print(f"   Pending tips: {pending_count}")
        print(f"   Processed tips: {processed_count}")
        print(f"   Total tips: {pending_count + processed_count}")
        
        # Show tips by location
        print(f"\nTips by location:")
        for (name, country), location in location_cache.items():
            count = db.query(Tip).filter(Tip.location_id == location.id).count()
            print(f"   {name}, {country}: {count} tips")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error populating database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Populate database with test tips")
    parser.add_argument(
        "-n", "--num-tips",
        type=int,
        default=None,
        help="Number of tips to add (default: all)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all existing tips before adding (WARNING: deletes all tips!)"
    )
    
    args = parser.parse_args()
    
    if args.clear:
        db = SessionLocal()
        try:
            print("⚠️  WARNING: Clearing all existing tips...")
            db.query(Tip).delete()
            db.query(Location).delete()
            db.commit()
            print("✅ Cleared all tips and locations")
        except Exception as e:
            db.rollback()
            print(f"❌ Error clearing database: {e}")
            sys.exit(1)
        finally:
            db.close()
    
    populate_database(num_tips=args.num_tips)


"""SQLAlchemy database models"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, DECIMAL, REAL, Boolean, Index, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.connection import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False)
    hashed_password = Column(String(255), nullable=True)  # Null for OAuth users

    # OAuth fields
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    auth_provider = Column(String(20), nullable=False)  # 'email' or 'google'

    # Profile
    full_name = Column(String(255), nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    preferred_language = Column(String(10), default='en')

    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())
    last_login = Column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    tips = relationship("Tip", back_populates="user")


class RefreshToken(Base):
    """Refresh token model for JWT refresh"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    revoked = Column(Boolean, default=False)


class Location(Base):
    """Location model"""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=True)
    longitude = Column(DECIMAL(11, 8), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        Index('idx_location_name_country', 'name', 'country'),
    )


class Tip(Base):
    """Tip model"""
    __tablename__ = "tips"

    id = Column(Integer, primary_key=True, index=True)
    tip_text = Column(Text, nullable=False)
    original_language = Column(String(10), nullable=True)
    translated_text = Column(Text, nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for optional auth
    submitted_at = Column(TIMESTAMP, server_default=func.now())
    processed_at = Column(TIMESTAMP, nullable=True)
    status = Column(String(20), default="pending", nullable=False)
    category_id = Column(String(50), nullable=True)
    category_confidence = Column(DECIMAL(4, 3), nullable=True)
    category_assigned_at = Column(TIMESTAMP, nullable=True)
    category_manual = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="tips")

    __table_args__ = (
        Index('idx_tip_status', 'status'),
        Index('idx_tip_location', 'location_id'),
        Index('idx_tip_submitted', 'submitted_at'),
        Index('idx_tip_category', 'category_id'),
        Index('idx_tip_location_category', 'location_id', 'category_id'),
    )


class Embedding(Base):
    """Embedding model"""
    __tablename__ = "embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    tip_id = Column(Integer, ForeignKey("tips.id"), nullable=False, unique=True)
    embedding = Column(ARRAY(REAL), nullable=False)  # Vector of 384 dimensions
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        Index('idx_embedding_tip', 'tip_id'),
    )


class TipPromotion(Base):
    """Tip promotion model"""
    __tablename__ = "tip_promotions"

    id = Column(Integer, primary_key=True, index=True)
    tip_text = Column(Text, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    source_tip_id = Column(Integer, ForeignKey("tips.id"), nullable=True)  # Representative tip for translations
    mention_count = Column(Integer, default=1, nullable=False)
    similarity_score = Column(DECIMAL(5, 4), nullable=True)
    promoted_at = Column(TIMESTAMP, server_default=func.now())
    category_id = Column(String(50), nullable=True)

    __table_args__ = (
        Index('idx_promotion_location', 'location_id'),
        Index('idx_promotion_mentions', 'mention_count'),
        Index('idx_promotion_category', 'category_id'),
    )


class TipTranslation(Base):
    """Tip translation model for multi-language support"""
    __tablename__ = "tip_translations"

    id = Column(Integer, primary_key=True, index=True)
    tip_id = Column(Integer, ForeignKey("tips.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(10), nullable=False)
    translated_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())

    __table_args__ = (
        Index('idx_translation_tip_lang', 'tip_id', 'language_code', unique=True),
        Index('idx_translation_language', 'language_code'),
    )


class TipSave(Base):
    """Tracks unique saves on promoted tips for aggregate counts."""
    __tablename__ = "tip_saves"

    id = Column(Integer, primary_key=True, index=True)
    promoted_tip_id = Column(Integer, ForeignKey("tip_promotions.id", ondelete="CASCADE"), nullable=False)
    saver_id = Column(String(64), nullable=False)
    saved_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        Index('idx_tip_save_unique', 'promoted_tip_id', 'saver_id', unique=True),
        Index('idx_tip_save_promoted', 'promoted_tip_id'),
    )


class Category(Base):
    """Category model for tip classification"""
    __tablename__ = "categories"

    id = Column(String(50), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(JSON, nullable=False)  # Array of description phrases
    embedding = Column(JSON, nullable=False)  # Array of embedding arrays
    icon_name = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    display_order = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        Index('idx_category_order', 'display_order'),
    )


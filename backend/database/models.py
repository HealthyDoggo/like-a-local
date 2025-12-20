"""SQLAlchemy database models"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, DECIMAL, REAL, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from backend.database.connection import Base


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
    user_id = Column(Integer, nullable=True)
    submitted_at = Column(TIMESTAMP, server_default=func.now())
    processed_at = Column(TIMESTAMP, nullable=True)
    status = Column(String(20), default="pending", nullable=False)
    
    __table_args__ = (
        Index('idx_tip_status', 'status'),
        Index('idx_tip_location', 'location_id'),
        Index('idx_tip_submitted', 'submitted_at'),
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
    mention_count = Column(Integer, default=1, nullable=False)
    similarity_score = Column(DECIMAL(5, 4), nullable=True)
    promoted_at = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        Index('idx_promotion_location', 'location_id'),
        Index('idx_promotion_mentions', 'mention_count'),
    )


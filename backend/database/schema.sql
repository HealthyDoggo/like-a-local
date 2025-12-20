-- PostgreSQL schema for TravelBuddy backend
-- Note: This assumes pgvector extension is installed
-- Run: CREATE EXTENSION IF NOT EXISTS vector;

-- Locations table
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_location_name_country ON locations(name, country);

-- Tips table (raw submissions)
CREATE TABLE IF NOT EXISTS tips (
    id SERIAL PRIMARY KEY,
    tip_text TEXT NOT NULL,
    original_language VARCHAR(10),
    translated_text TEXT,
    location_id INTEGER REFERENCES locations(id),
    user_id INTEGER,
    submitted_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tip_status ON tips(status);
CREATE INDEX IF NOT EXISTS idx_tip_location ON tips(location_id);
CREATE INDEX IF NOT EXISTS idx_tip_submitted ON tips(submitted_at);

-- Embeddings table
-- Note: Using ARRAY instead of vector type for compatibility
-- If pgvector is available, can use: embedding vector(384)
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    tip_id INTEGER REFERENCES tips(id) UNIQUE NOT NULL,
    embedding REAL[] NOT NULL,  -- Array of 384 float values
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_embedding_tip ON embeddings(tip_id);

-- Tip aggregations for promotion
CREATE TABLE IF NOT EXISTS tip_promotions (
    id SERIAL PRIMARY KEY,
    tip_text TEXT NOT NULL,
    location_id INTEGER REFERENCES locations(id) NOT NULL,
    mention_count INTEGER DEFAULT 1 NOT NULL,
    similarity_score DECIMAL(5, 4),
    promoted_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_promotion_location ON tip_promotions(location_id);
CREATE INDEX IF NOT EXISTS idx_promotion_mentions ON tip_promotions(mention_count);


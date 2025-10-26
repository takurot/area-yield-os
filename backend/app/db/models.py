"""SQLAlchemy ORM models"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    role = Column(String(50), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)

    # Relationships
    analysis_results = relationship("AnalysisResult", back_populates="user")


class AnalysisResult(Base):
    """Analysis result model"""

    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(128), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Input data
    address = Column(Text, nullable=False)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    # Judgment
    judgment = Column(String(20), nullable=False, index=True)  # Go/Amber/Stop
    score = Column(Float, nullable=False)

    # Detailed scores
    profitability_score = Column(Float, nullable=True)
    licensing_score = Column(Float, nullable=True)
    regulation_risk_score = Column(Float, nullable=True)

    # Result data (JSON)
    profitability_data = Column(JSON, nullable=True)
    licensing_data = Column(JSON, nullable=True)
    regulation_risk_data = Column(JSON, nullable=True)
    market_stats_data = Column(JSON, nullable=True)

    # Metadata
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    data_freshness = Column(String(50), nullable=True)
    model_version = Column(String(50), nullable=True)

    # Relationships
    user = relationship("User", back_populates="analysis_results")

    __table_args__ = (
        Index("idx_analysis_results_user_judgment", "user_id", "judgment"),
        Index("idx_analysis_results_analyzed_at", "analyzed_at"),
    )


class DataSource(Base):
    """Data source model"""

    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String(128), unique=True, index=True, nullable=False)
    source_type = Column(
        String(50), nullable=False, index=True
    )  # airdna, council_minutes, etc.
    source_url = Column(Text, nullable=True)
    publisher = Column(String(255), nullable=True)

    # Location
    prefecture = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)

    # Timing
    collected_at = Column(DateTime, nullable=False, index=True)
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Metadata
    license = Column(String(255), nullable=True)
    meta_data = Column(JSON, nullable=True)

    __table_args__ = (Index("idx_data_sources_type_city", "source_type", "city"),)


class ZoningArea(Base):
    """Zoning area model (用途地域)"""

    __tablename__ = "zoning_areas"

    id = Column(Integer, primary_key=True, index=True)
    area_code = Column(String(50), unique=True, index=True, nullable=False)

    # Location
    prefecture = Column(String(100), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    district = Column(String(255), nullable=True)

    # Zoning classification
    zoning_type = Column(String(100), nullable=False, index=True)

    # Geometry (stored as GeoJSON)
    geometry = Column(JSON, nullable=True)

    # Building regulations
    building_coverage_ratio = Column(Float, nullable=True)  # 建ぺい率
    floor_area_ratio = Column(Float, nullable=True)  # 容積率

    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (Index("idx_zoning_areas_city_type", "city", "zoning_type"),)


class School(Base):
    """School/nursery location model"""

    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    school_code = Column(String(50), unique=True, index=True, nullable=False)

    # Basic info
    name = Column(String(255), nullable=False)
    school_type = Column(
        String(50), nullable=False, index=True
    )  # elementary, nursery, etc.

    # Location
    prefecture = Column(String(100), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    address = Column(Text, nullable=True)
    lat = Column(Float, nullable=False, index=True)
    lng = Column(Float, nullable=False, index=True)

    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_schools_location", "lat", "lng"),
        Index("idx_schools_city_type", "city", "school_type"),
    )

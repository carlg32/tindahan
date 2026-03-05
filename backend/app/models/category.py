"""Category model for product categorization."""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.product import Product


class Category(Base):
    """Category model for organizing products.
    
    Attributes:
        id: Primary key
        name: Unique category name
        description: Category description
        color: Color code for UI display (hex format)
        sort_order: Display order for sorting
        product_count: Cached count of products in category
        is_active: Whether category is active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="Category name"
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Category description"
    )
    color: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
        default="#3B82F6",
        comment="Color code for UI (hex format, e.g., #3B82F6)"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Display order for sorting"
    )
    product_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Cached count of products in this category"
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Whether category is active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category_obj",
        lazy="selectin"
    )

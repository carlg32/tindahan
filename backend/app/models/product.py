"""Product model for inventory items."""
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Numeric, Integer, Boolean, DateTime, Text, Index, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.stock_movement import StockMovement
    from app.models.category import Category


class Product(Base):
    """Product model representing inventory items.
    
    Attributes:
        id: Primary key
        sku: Unique Stock Keeping Unit
        name: Product name
        description: Product description
        category: Product category
        unit_price: Price per unit
        current_stock: Current quantity in stock
        min_stock_level: Minimum stock before reorder alert
        barcode: Unique barcode (EAN/UPC)
        is_active: Whether product is active in system
        created_at: Product creation timestamp
    """
    
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="Unique Stock Keeping Unit"
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Product name"
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Product description"
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Category ID"
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Price per unit"
    )
    current_stock: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Current quantity in stock"
    )
    min_stock_level: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Minimum stock before reorder alert"
    )
    barcode: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        comment="Unique barcode (EAN/UPC)"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether product is active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Product creation timestamp"
    )
    
    # Relationships
    stock_movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="product",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    category_obj: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
        lazy="selectin"
    )
    
    __table_args__ = (
        # Ensure positive values for price and stock
        CheckConstraint("unit_price >= 0", name="check_unit_price_positive"),
        CheckConstraint("current_stock >= 0", name="check_current_stock_positive"),
        CheckConstraint("min_stock_level >= 0", name="check_min_stock_positive"),
        
        # Partial unique index for barcode (only for non-null barcodes)
        Index("ix_products_barcode", "barcode", unique=True, postgresql_where="barcode IS NOT NULL"),
        
        # Composite index for common query patterns
        Index("ix_products_category_active", "category_id", "is_active"),
        Index("ix_products_sku_active", "sku", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, sku={self.sku}, name={self.name})>"
    
    @property
    def is_low_stock(self) -> bool:
        """Check if product stock is below minimum level."""
        return self.current_stock <= self.min_stock_level

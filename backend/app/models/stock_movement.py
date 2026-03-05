"""Stock movement model for tracking inventory changes."""
import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Enum, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class MovementType(str, enum.Enum):
    """Stock movement type enumeration."""
    IN = "in"              # Stock received/purchased
    OUT = "out"            # Stock sold/used/shipped
    ADJUSTMENT = "adjustment"  # Manual inventory adjustment


class StockMovement(Base):
    """Stock movement model for tracking all inventory changes.
    
    Attributes:
        id: Primary key
        product_id: Reference to the product
        user_id: Reference to the user who made the movement
        type: Movement type (in/out/adjustment)
        quantity: Quantity change (always positive for in, negative for out)
        reason: Reason for the movement
        created_at: Movement timestamp
    """
    
    __tablename__ = "stock_movements"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the product"
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to the user who made the movement"
    )
    type: Mapped[MovementType] = mapped_column(
        Enum(MovementType, name="movement_type"),
        nullable=False,
        comment="Movement type: in, out, or adjustment"
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Quantity change"
    )
    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for the movement"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="Movement timestamp"
    )
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="stock_movements")
    user: Mapped["User | None"] = relationship("User", back_populates="stock_movements")
    
    __table_args__ = (
        # Ensure quantity is not zero
        CheckConstraint("quantity != 0", name="check_quantity_not_zero"),
        
        # Composite indexes for common queries
        Index("ix_stock_movements_product_created", "product_id", "created_at"),
        Index("ix_stock_movements_user_created", "user_id", "created_at"),
        Index("ix_stock_movements_type_created", "type", "created_at"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<StockMovement(id={self.id}, product_id={self.product_id}, "
            f"type={self.type.value}, quantity={self.quantity})>"
        )
    
    @property
    def signed_quantity(self) -> int:
        """Get signed quantity based on movement type.
        
        Returns:
            Positive for 'in', negative for 'out', 
            actual value for 'adjustment'
        """
        if self.type == MovementType.IN:
            return abs(self.quantity)
        elif self.type == MovementType.OUT:
            return -abs(self.quantity)
        else:  # adjustment
            return self.quantity

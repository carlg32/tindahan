"""User model for authentication and authorization."""
import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, Enum, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.stock_movement import StockMovement
    from app.models.audit_log import AuditLog


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    STAFF = "staff"


class User(Base):
    """User model for system authentication and authorization.
    
    Attributes:
        id: Primary key
        username: Unique username for login
        hashed_password: BCrypt hashed password
        role: User role (admin or staff)
        is_active: Whether the user account is active
        created_at: Account creation timestamp
    """
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        index=True,
        nullable=False,
        comment="Unique username for login"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="BCrypt hashed password"
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        default=UserRole.STAFF,
        nullable=False,
        comment="User role: admin or staff"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the account is active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Account creation timestamp"
    )
    
    # Relationships
    stock_movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="user",
        lazy="selectin"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        lazy="selectin"
    )
    
    __table_args__ = (
        Index("ix_users_username_active", "username", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role.value})>"

"""Audit log model for tracking all data changes."""
import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Enum, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class AuditAction(str, enum.Enum):
    """Audit action type enumeration."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class AuditLog(Base):
    """Audit log model for tracking all database changes.
    
    Attributes:
        id: Primary key
        user_id: Reference to the user who made the change
        table_name: Name of the affected table
        record_id: ID of the affected record
        action: Type of action (create/update/delete)
        old_values: Previous values as JSON
        new_values: New values as JSON
        created_at: Audit timestamp
    """
    
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to the user who made the change"
    )
    table_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Name of the affected table"
    )
    record_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="ID of the affected record"
    )
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, name="audit_action"),
        nullable=False,
        index=True,
        comment="Type of action: create, update, or delete"
    )
    old_values: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Previous values as JSON"
    )
    new_values: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        comment="New values as JSON"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="Audit timestamp"
    )
    
    # Relationships
    user: Mapped["User | None"] = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        # Composite indexes for common queries
        Index("ix_audit_logs_table_record", "table_name", "record_id"),
        Index("ix_audit_logs_table_action", "table_name", "action"),
        Index("ix_audit_logs_user_created", "user_id", "created_at"),
        Index("ix_audit_logs_table_created", "table_name", "created_at"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, table={self.table_name}, "
            f"record_id={self.record_id}, action={self.action.value})>"
        )
    
    @property
    def summary(self) -> str:
        """Generate a human-readable summary of the audit entry."""
        user_info = f"by user {self.user_id}" if self.user_id else "by system"
        return f"{self.action.value.upper()} on {self.table_name} (ID: {self.record_id}) {user_info}"

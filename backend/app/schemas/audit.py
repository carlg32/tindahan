"""Pydantic schemas for audit log operations."""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.audit_log import AuditAction


class AuditLogResponse(BaseModel):
    """Schema for audit log entry in responses.
    
    Provides complete audit trail information.
    """
    id: int
    user_id: int | None
    table_name: str
    record_id: int
    action: AuditAction
    old_values: dict[str, Any] | None
    new_values: dict[str, Any] | None
    created_at: datetime
    
    # Additional info for display
    username: str | None = None
    summary: str | None = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 2,
                "username": "johndoe",
                "table_name": "products",
                "record_id": 5,
                "action": "update",
                "old_values": {"unit_price": "29.99", "name": "Old Name"},
                "new_values": {"unit_price": "34.99", "name": "New Name"},
                "created_at": "2024-01-15T10:30:00Z",
                "summary": "UPDATE on products (ID: 5) by user 2"
            }
        }
    )


class AuditLogList(BaseModel):
    """Schema for paginated audit log list."""
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    pages: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 500,
                "page": 1,
                "page_size": 20,
                "pages": 25
            }
        }
    )


class AuditLogFilter(BaseModel):
    """Schema for audit log filtering."""
    user_id: int | None = None
    table_name: str | None = Field(None, max_length=100)
    record_id: int | None = None
    action: AuditAction | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "table_name": "products",
                "action": "update",
                "date_from": "2024-01-01T00:00:00Z",
                "date_to": "2024-01-31T23:59:59Z"
            }
        }
    )


class AuditSummary(BaseModel):
    """Schema for audit statistics summary."""
    total_records: int
    actions_by_type: dict[str, int]
    tables_affected: list[str]
    date_range: dict[str, datetime]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_records": 1500,
                "actions_by_type": {
                    "create": 500,
                    "update": 800,
                    "delete": 200
                },
                "tables_affected": ["products", "users", "stock_movements"],
                "date_range": {
                    "earliest": "2024-01-01T00:00:00Z",
                    "latest": "2024-01-31T23:59:59Z"
                }
            }
        }
    )

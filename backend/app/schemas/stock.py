"""Pydantic schemas for stock movement operations."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.stock_movement import MovementType


class StockMovementBase(BaseModel):
    """Base stock movement schema."""
    type: MovementType
    quantity: int = Field(..., gt=0, description="Positive quantity value")
    reason: str | None = Field(None, max_length=500)


class StockMovementCreate(StockMovementBase):
    """Schema for creating a stock movement.
    
    Used when recording inventory changes.
    """
    product_id: int = Field(..., gt=0, description="ID of the product")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 1,
                "type": "in",
                "quantity": 50,
                "reason": "Restocked from supplier"
            }
        }
    )


class StockAdjustmentCreate(BaseModel):
    """Schema for stock adjustment (sets absolute quantity).
    
    Used when correcting inventory counts.
    """
    product_id: int = Field(..., gt=0)
    new_quantity: int = Field(..., ge=0, description="Absolute quantity to set")
    reason: str = Field(..., min_length=1, max_length=500)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 1,
                "new_quantity": 45,
                "reason": "Physical count adjustment"
            }
        }
    )


class StockMovementResponse(StockMovementBase):
    """Schema for stock movement data in responses."""
    id: int
    product_id: int
    user_id: int | None
    signed_quantity: int
    created_at: datetime
    
    # Nested data for convenience
    product_sku: str | None = None
    product_name: str | None = None
    username: str | None = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "product_id": 1,
                "user_id": 2,
                "type": "in",
                "quantity": 50,
                "signed_quantity": 50,
                "reason": "Restocked from supplier",
                "created_at": "2024-01-15T10:30:00Z",
                "product_sku": "PROD-001",
                "product_name": "Wireless Mouse",
                "username": "johndoe"
            }
        }
    )


class StockMovementList(BaseModel):
    """Schema for paginated stock movement list."""
    items: list[StockMovementResponse]
    total: int
    page: int
    page_size: int
    pages: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 200,
                "page": 1,
                "page_size": 20,
                "pages": 10
            }
        }
    )


class StockMovementFilter(BaseModel):
    """Schema for stock movement filtering."""
    product_id: int | None = None
    user_id: int | None = None
    type: MovementType | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 1,
                "type": "in",
                "date_from": "2024-01-01T00:00:00Z",
                "date_to": "2024-01-31T23:59:59Z"
            }
        }
    )


class StockLevelResponse(BaseModel):
    """Schema for current stock level of a product."""
    product_id: int
    sku: str
    name: str
    current_stock: int
    min_stock_level: int
    available_stock: int
    reserved_stock: int = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 1,
                "sku": "PROD-001",
                "name": "Wireless Mouse",
                "current_stock": 50,
                "min_stock_level": 10,
                "available_stock": 50,
                "reserved_stock": 0
            }
        }
    )


class BulkStockMovementItem(BaseModel):
    """Single item for bulk stock movement."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    reason: str | None = Field(None, max_length=500)


class BulkStockMovementCreate(BaseModel):
    """Schema for bulk stock movement (e.g., receiving shipment)."""
    type: MovementType
    items: list[BulkStockMovementItem] = Field(..., min_length=1, max_length=50)
    global_reason: str | None = Field(None, max_length=500)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "in",
                "global_reason": "Weekly restock",
                "items": [
                    {"product_id": 1, "quantity": 20, "reason": "Hot seller"},
                    {"product_id": 2, "quantity": 15}
                ]
            }
        }
    )

"""Pydantic schemas for dashboard and analytics."""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class DashboardStats(BaseModel):
    """Schema for main dashboard statistics."""
    
    # Product counts
    total_products: int
    active_products: int
    low_stock_count: int
    out_of_stock_count: int
    
    # Inventory value
    total_inventory_value: Decimal
    
    # Movement stats (today)
    movements_today: int
    stock_in_today: int
    stock_out_today: int
    
    # Movement stats (this week)
    movements_this_week: int
    stock_in_week: int
    stock_out_week: int
    
    # User stats
    total_users: int
    active_users: int
    
    # Category breakdown
    products_by_category: dict[str, int]
    
    # Recent activity timestamp
    last_updated: datetime
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_products": 500,
                "active_products": 450,
                "low_stock_count": 25,
                "out_of_stock_count": 5,
                "total_inventory_value": "125000.00",
                "movements_today": 15,
                "stock_in_today": 100,
                "stock_out_today": 45,
                "movements_this_week": 120,
                "stock_in_week": 850,
                "stock_out_week": 420,
                "total_users": 10,
                "active_users": 8,
                "products_by_category": {
                    "Electronics": 150,
                    "Clothing": 100,
                    "Food": 80,
                    "Other": 120
                },
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }
    )


class LowStockAlert(BaseModel):
    """Schema for low stock alert item."""
    product_id: int
    sku: str
    name: str
    category: str | None
    current_stock: int
    min_stock_level: int
    deficit: int
    unit_price: Decimal
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 5,
                "sku": "PROD-005",
                "name": "Premium Headphones",
                "category": "Electronics",
                "current_stock": 3,
                "min_stock_level": 10,
                "deficit": 7,
                "unit_price": "79.99"
            }
        }
    )


class LowStockAlertList(BaseModel):
    """Schema for list of low stock alerts."""
    alerts: list[LowStockAlert]
    total_alerts: int
    total_deficit_value: Decimal
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "alerts": [],
                "total_alerts": 25,
                "total_deficit_value": "5000.00"
            }
        }
    )


class InventoryTrend(BaseModel):
    """Schema for inventory trend data point."""
    date: datetime
    total_stock: int
    stock_value: Decimal
    movements_in: int
    movements_out: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2024-01-15T00:00:00Z",
                "total_stock": 5000,
                "stock_value": "125000.00",
                "movements_in": 50,
                "movements_out": 30
            }
        }
    )


class TopProduct(BaseModel):
    """Schema for top product by movement volume."""
    product_id: int
    sku: str
    name: str
    category: str | None
    total_movements: int
    stock_in: int
    stock_out: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": 1,
                "sku": "PROD-001",
                "name": "Wireless Mouse",
                "category": "Electronics",
                "total_movements": 50,
                "stock_in": 200,
                "stock_out": 150
            }
        }
    )


class DashboardActivity(BaseModel):
    """Schema for recent dashboard activity item."""
    id: int
    type: str  # "movement", "product_update", "audit"
    description: str
    user: str | None
    timestamp: datetime
    details: dict | None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "type": "movement",
                "description": "Stock IN: 50 units of Wireless Mouse",
                "user": "johndoe",
                "timestamp": "2024-01-15T10:30:00Z",
                "details": {"product_id": 1, "quantity": 50}
            }
        }
    )


class DateRangeFilter(BaseModel):
    """Schema for date range filtering."""
    start_date: datetime
    end_date: datetime
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-31T23:59:59Z"
            }
        }
    )

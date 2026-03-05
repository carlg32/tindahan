"""Pydantic schemas for product-related operations."""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class ProductBase(BaseModel):
    """Base product schema with common fields."""
    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    category_id: int | None = Field(None, description="Category ID")
    unit_price: Decimal = Field(..., ge=0, decimal_places=2)
    min_stock_level: int = Field(default=0, ge=0)
    barcode: str | None = Field(None, max_length=50)
    is_active: bool = Field(default=True)


class ProductCreate(ProductBase):
    """Schema for creating a new product.
    
    Used when adding new inventory items.
    """
    current_stock: int = Field(default=0, ge=0)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sku": "PROD-001",
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse with USB receiver",
                "category_id": 1,
                "unit_price": "29.99",
                "current_stock": 50,
                "min_stock_level": 10,
                "barcode": "123456789012",
                "is_active": True
            }
        }
    )


class ProductUpdate(BaseModel):
    """Schema for updating product information.
    
    All fields are optional for partial updates.
    SKU cannot be changed after creation.
    """
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    category_id: int | None = Field(None, description="Category ID")
    unit_price: Decimal | None = Field(None, ge=0, decimal_places=2)
    min_stock_level: int | None = Field(None, ge=0)
    barcode: str | None = Field(None, max_length=50)
    is_active: bool | None = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Wireless Mouse Pro",
                "unit_price": "34.99",
                "min_stock_level": 15
            }
        }
    )


class ProductResponse(ProductBase):
    """Schema for product data in responses.
    
    Includes computed fields and full product details.
    """
    id: int
    current_stock: int
    is_low_stock: bool
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "sku": "PROD-001",
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse with USB receiver",
                "category": "Electronics",
                "unit_price": "29.99",
                "current_stock": 50,
                "min_stock_level": 10,
                "barcode": "123456789012",
                "is_active": True,
                "is_low_stock": False,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
    )


class ProductList(BaseModel):
    """Schema for paginated product list response."""
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    pages: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "pages": 5
            }
        }
    )


class ProductFilter(BaseModel):
    """Schema for product filtering parameters."""
    category_id: int | None = Field(None, description="Filter by category ID")
    is_active: bool | None = None
    is_low_stock: bool | None = None
    search: str | None = Field(None, max_length=100)
    sort_by: Literal["name", "sku", "category_id", "current_stock", "unit_price", "created_at"] = "name"
    sort_order: Literal["asc", "desc"] = "asc"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category_id": 1,
                "is_active": True,
                "search": "mouse",
                "sort_by": "name",
                "sort_order": "asc"
            }
        }
    )


class BulkProductCreate(BaseModel):
    """Schema for bulk product creation."""
    products: list[ProductCreate] = Field(..., min_length=1, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "products": [
                    {
                        "sku": "PROD-001",
                        "name": "Product 1",
                        "unit_price": "19.99",
                        "current_stock": 10
                    },
                    {
                        "sku": "PROD-002",
                        "name": "Product 2",
                        "unit_price": "29.99",
                        "current_stock": 20
                    }
                ]
            }
        }
    )

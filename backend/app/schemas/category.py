"""Category schemas for request/response validation."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel):
    """Base category schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: str | None = Field(None, max_length=500, description="Category description")
    color: str | None = Field(
        default="#3B82F6",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Color code for UI (hex format, e.g., #3B82F6)"
    )
    sort_order: int = Field(default=0, ge=0, description="Display order for sorting")
    is_active: bool = Field(default=True, description="Whether category is active")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    sort_order: int | None = Field(None, ge=0)
    is_active: bool | None = None


class CategoryResponse(CategoryBase):
    """Schema for category response with all fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product_count: int = Field(default=0, description="Number of products in this category")
    created_at: datetime
    updated_at: datetime


class CategoryList(BaseModel):
    """Schema for paginated category list response."""
    items: list[CategoryResponse]
    total: int
    page: int
    page_size: int
    pages: int


class CategoryFilter(BaseModel):
    """Schema for filtering categories."""
    search: str | None = Field(None, max_length=100, description="Search by name or description")
    is_active: bool | None = Field(None, description="Filter by active status")
    sort_by: str = Field(default="sort_order", description="Field to sort by")
    sort_order: str = Field(default="asc", pattern=r"^(asc|desc)$")

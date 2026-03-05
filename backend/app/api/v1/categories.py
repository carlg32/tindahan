"""Category API endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Category, User
from app.schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryList,
    CategoryFilter,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=CategoryList)
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search by name or description"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    sort_by: str = Query("sort_order", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
):
    """List all categories with optional filtering and pagination."""
    # Build base query
    query = select(Category)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Category.name.ilike(search_filter)) |
            (Category.description.ilike(search_filter))
        )
    
    if is_active is not None:
        query = query.where(Category.is_active == is_active)
    
    # Get total count
    count_query = select(func.count(Category.id))
    if search:
        count_query = count_query.where(
            (Category.name.ilike(search_filter)) |
            (Category.description.ilike(search_filter))
        )
    if is_active is not None:
        count_query = count_query.where(Category.is_active == is_active)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply sorting
    sort_column = getattr(Category, sort_by, Category.sort_order)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return CategoryList(
        items=[CategoryResponse.model_validate(c) for c in categories],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/all", response_model=list[CategoryResponse])
async def get_all_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    is_active: bool | None = Query(None, description="Filter by active status"),
):
    """Get all categories without pagination (for dropdowns)."""
    query = select(Category)
    
    if is_active is not None:
        query = query.where(Category.is_active == is_active)
    
    query = query.order_by(asc(Category.sort_order), asc(Category.name))
    
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a single category by ID."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return CategoryResponse.model_validate(category)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Create a new category."""
    # Check if category name already exists
    existing = await db.execute(
        select(Category).where(Category.name == category_data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category_data.name}' already exists"
        )
    
    category = Category(**category_data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return CategoryResponse.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Update an existing category."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check name uniqueness if updating name
    if category_data.name and category_data.name != category.name:
        existing = await db.execute(
            select(Category).where(Category.name == category_data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_data.name}' already exists"
            )
    
    # Update fields
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    await db.commit()
    await db.refresh(category)
    
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Delete a category."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if category has products
    if category.product_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with {category.product_count} products. Please reassign or delete products first."
        )
    
    await db.delete(category)
    await db.commit()

"""Product API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductList


router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductList)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name or SKU"),
    category: Optional[str] = Query(None),
    low_stock: Optional[bool] = Query(None, description="Filter low stock items"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all products with optional filtering."""
    query = select(Product).where(Product.is_active == True)
    
    if search:
        query = query.where(
            (Product.name.ilike(f"%{search}%")) | 
            (Product.sku.ilike(f"%{search}%"))
        )
    
    if category:
        query = query.where(Product.category.ilike(f"%{category}%"))
    
    if low_stock:
        query = query.where(Product.current_stock <= Product.min_stock_level)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Calculate pagination
    skip = (page - 1) * page_size
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    # Get paginated results
    query = query.offset(skip).limit(page_size).order_by(Product.name)
    result = await db.execute(query)
    products = result.scalars().all()
    
    return ProductList(
        items=products,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single product by ID."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new product (admin only)."""
    # Check for duplicate SKU
    existing = await db.execute(
        select(Product).where(Product.sku == product_data.sku)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product_data.sku}' already exists"
        )
    
    # Check for duplicate barcode if provided
    if product_data.barcode:
        existing_barcode = await db.execute(
            select(Product).where(Product.barcode == product_data.barcode)
        )
        if existing_barcode.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with barcode '{product_data.barcode}' already exists"
            )
    
    product = Product(**product_data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a product (admin only)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check for duplicate barcode if being updated
    if product_data.barcode and product_data.barcode != product.barcode:
        existing = await db.execute(
            select(Product).where(
                (Product.barcode == product_data.barcode) & 
                (Product.id != product_id)
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with barcode '{product_data.barcode}' already exists"
            )
    
    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    await db.commit()
    await db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Soft delete a product by setting is_active to False (admin only)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product.is_active = False
    await db.commit()
    
    return None


@router.get("/low-stock/alerts", response_model=ProductList)
async def get_low_stock_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get products with low stock (current_stock <= min_stock_level)."""
    query = select(Product).where(
        (Product.is_active == True) &
        (Product.current_stock <= Product.min_stock_level)
    )
    
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    skip = (page - 1) * page_size
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    query = query.offset(skip).limit(page_size).order_by(Product.current_stock)
    result = await db.execute(query)
    products = result.scalars().all()
    
    return ProductList(
        items=products,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
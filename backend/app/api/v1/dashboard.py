"""Dashboard API routes for statistics and overview."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.product import Product
from app.models.user import User
from app.schemas.dashboard import DashboardStats, LowStockAlert, LowStockAlertList


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard statistics and overview data."""
    # Total products count
    total_products_result = await db.execute(
        select(func.count()).select_from(Product)
    )
    total_products = total_products_result.scalar()
    
    # Active products count
    active_products_result = await db.execute(
        select(func.count()).select_from(Product).where(Product.is_active == True)
    )
    active_products = active_products_result.scalar()
    
    # Low stock count
    low_stock_result = await db.execute(
        select(func.count()).select_from(Product).where(
            (Product.is_active == True) &
            (Product.current_stock <= Product.min_stock_level) &
            (Product.current_stock > 0)
        )
    )
    low_stock_count = low_stock_result.scalar()
    
    # Out of stock count
    out_of_stock_result = await db.execute(
        select(func.count()).select_from(Product).where(
            (Product.is_active == True) & (Product.current_stock == 0)
        )
    )
    out_of_stock_count = out_of_stock_result.scalar()
    
    # Total inventory value
    inventory_value_result = await db.execute(
        select(func.sum(Product.unit_price * Product.current_stock)).where(
            Product.is_active == True
        )
    )
    total_inventory_value = inventory_value_result.scalar() or 0
    
    # User stats
    total_users_result = await db.execute(
        select(func.count()).select_from(User)
    )
    total_users = total_users_result.scalar()
    
    active_users_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_active == True)
    )
    active_users = active_users_result.scalar()
    
    # Category breakdown
    category_result = await db.execute(
        select(Product.category, func.count()).where(
            Product.is_active == True
        ).group_by(Product.category)
    )
    products_by_category = {}
    for row in category_result.all():
        category = row.category or "Uncategorized"
        products_by_category[category] = row.count
    
    return DashboardStats(
        total_products=total_products,
        active_products=active_products,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        total_inventory_value=total_inventory_value,
        movements_today=0,  # Placeholder - would need stock_movement table queries
        stock_in_today=0,
        stock_out_today=0,
        movements_this_week=0,
        stock_in_week=0,
        stock_out_week=0,
        total_users=total_users,
        active_users=active_users,
        products_by_category=products_by_category,
        last_updated=datetime.now(timezone.utc),
    )


@router.get("/low-stock-alerts", response_model=LowStockAlertList)
async def get_low_stock_alerts(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get products with low stock alerts."""
    result = await db.execute(
        select(Product).where(
            (Product.is_active == True) &
            (Product.current_stock <= Product.min_stock_level) &
            (Product.current_stock > 0)
        ).order_by(Product.current_stock).limit(limit)
    )
    products = result.scalars().all()
    
    alerts = []
    total_deficit_value = 0
    
    for product in products:
        deficit = product.min_stock_level - product.current_stock
        total_deficit_value += deficit * product.unit_price
        alerts.append(LowStockAlert(
            product_id=product.id,
            sku=product.sku,
            name=product.name,
            category=product.category,
            current_stock=product.current_stock,
            min_stock_level=product.min_stock_level,
            deficit=deficit,
            unit_price=product.unit_price,
        ))
    
    return LowStockAlertList(
        alerts=alerts,
        total_alerts=len(alerts),
        total_deficit_value=total_deficit_value,
    )
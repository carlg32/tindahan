"""Pydantic schemas package.

This module exports all Pydantic schemas for request/response validation.
"""
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenData,
    PasswordChange,
)
from app.schemas.product import (
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductList,
    ProductFilter,
    BulkProductCreate,
)
from app.schemas.stock import (
    StockMovementBase,
    StockMovementCreate,
    StockAdjustmentCreate,
    StockMovementResponse,
    StockMovementList,
    StockMovementFilter,
    StockLevelResponse,
    BulkStockMovementItem,
    BulkStockMovementCreate,
)
from app.schemas.audit import (
    AuditLogResponse,
    AuditLogList,
    AuditLogFilter,
    AuditSummary,
)
from app.schemas.dashboard import (
    DashboardStats,
    LowStockAlert,
    LowStockAlertList,
    InventoryTrend,
    TopProduct,
    DashboardActivity,
    DateRangeFilter,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenData",
    "PasswordChange",
    # Product schemas
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductList",
    "ProductFilter",
    "BulkProductCreate",
    # Stock schemas
    "StockMovementBase",
    "StockMovementCreate",
    "StockAdjustmentCreate",
    "StockMovementResponse",
    "StockMovementList",
    "StockMovementFilter",
    "StockLevelResponse",
    "BulkStockMovementItem",
    "BulkStockMovementCreate",
    # Audit schemas
    "AuditLogResponse",
    "AuditLogList",
    "AuditLogFilter",
    "AuditSummary",
    # Dashboard schemas
    "DashboardStats",
    "LowStockAlert",
    "LowStockAlertList",
    "InventoryTrend",
    "TopProduct",
    "DashboardActivity",
    "DateRangeFilter",
]

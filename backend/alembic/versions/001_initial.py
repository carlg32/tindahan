"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    user_role = postgresql.ENUM('admin', 'staff', name='user_role', create_type=False)
    movement_type = postgresql.ENUM('in', 'out', 'adjustment', name='movement_type', create_type=False)
    audit_action = postgresql.ENUM('create', 'update', 'delete', name='audit_action', create_type=False)
    
    user_role.create(op.get_bind(), checkfirst=True)
    movement_type.create(op.get_bind(), checkfirst=True)
    audit_action.create(op.get_bind(), checkfirst=True)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', user_role, nullable=False, server_default='staff'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        comment='User accounts for system authentication'
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_username_active', 'users', ['username', 'is_active'])
    
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sku', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('current_stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('min_stock_level', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('barcode', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('unit_price >= 0', name='check_unit_price_positive'),
        sa.CheckConstraint('current_stock >= 0', name='check_current_stock_positive'),
        sa.CheckConstraint('min_stock_level >= 0', name='check_min_stock_positive'),
        comment='Product inventory items'
    )
    op.create_index('ix_products_id', 'products', ['id'])
    op.create_index('ix_products_sku', 'products', ['sku'], unique=True)
    op.create_index('ix_products_barcode', 'products', ['barcode'], unique=True, postgresql_where=sa.text('barcode IS NOT NULL'))
    op.create_index('ix_products_category', 'products', ['category'])
    op.create_index('ix_products_category_active', 'products', ['category', 'is_active'])
    op.create_index('ix_products_sku_active', 'products', ['sku', 'is_active'])
    
    # Create stock_movements table
    op.create_table(
        'stock_movements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('type', movement_type, nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('quantity != 0', name='check_quantity_not_zero'),
        comment='Stock movement history'
    )
    op.create_index('ix_stock_movements_id', 'stock_movements', ['id'])
    op.create_index('ix_stock_movements_product_id', 'stock_movements', ['product_id'])
    op.create_index('ix_stock_movements_user_id', 'stock_movements', ['user_id'])
    op.create_index('ix_stock_movements_created_at', 'stock_movements', ['created_at'])
    op.create_index('ix_stock_movements_type', 'stock_movements', ['type'])
    op.create_index('ix_stock_movements_product_created', 'stock_movements', ['product_id', 'created_at'])
    op.create_index('ix_stock_movements_user_created', 'stock_movements', ['user_id', 'created_at'])
    op.create_index('ix_stock_movements_type_created', 'stock_movements', ['type', 'created_at'])
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('table_name', sa.String(100), nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=False),
        sa.Column('action', audit_action, nullable=False),
        sa.Column('old_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        comment='Audit trail for all data changes'
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_table_name', 'audit_logs', ['table_name'])
    op.create_index('ix_audit_logs_record_id', 'audit_logs', ['record_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('ix_audit_logs_table_record', 'audit_logs', ['table_name', 'record_id'])
    op.create_index('ix_audit_logs_table_action', 'audit_logs', ['table_name', 'action'])
    op.create_index('ix_audit_logs_user_created', 'audit_logs', ['user_id', 'created_at'])
    op.create_index('ix_audit_logs_table_created', 'audit_logs', ['table_name', 'created_at'])


def downgrade() -> None:
    # Drop audit_logs table
    op.drop_table('audit_logs')
    
    # Drop stock_movements table
    op.drop_table('stock_movements')
    
    # Drop products table
    op.drop_table('products')
    
    # Drop users table
    op.drop_table('users')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS user_role')
    op.execute('DROP TYPE IF EXISTS movement_type')
    op.execute('DROP TYPE IF EXISTS audit_action')

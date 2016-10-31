from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
productCoupon_identifier = Table('productCoupon_identifier', pre_meta,
    Column('coupon_id', VARCHAR(length=8)),
    Column('product_id', INTEGER),
)

association = Table('association', post_meta,
    Column('product_id', Integer),
    Column('coupon_id', String(length=8)),
)

coupon = Table('coupon', post_meta,
    Column('id', String(length=8), primary_key=True, nullable=False),
    Column('name', String(length=140)),
    Column('multiplier', Float),
    Column('upto', Integer),
    Column('flatoff', Integer),
)

product = Table('product', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('name', VARCHAR(length=140)),
    Column('price', INTEGER),
    Column('timestamp', TIMESTAMP),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['productCoupon_identifier'].drop()
    post_meta.tables['association'].create()
    post_meta.tables['coupon'].columns['upto'].create()
    pre_meta.tables['product'].columns['timestamp'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['productCoupon_identifier'].create()
    post_meta.tables['association'].drop()
    post_meta.tables['coupon'].columns['upto'].drop()
    pre_meta.tables['product'].columns['timestamp'].create()

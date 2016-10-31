from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.dialects import postgresql

from app import db,lm


class User(UserMixin, db.Model):
    # __tablename__ = 'users'
    id = db.Column(db.String(64), primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    name = db.Column(db.String(64), nullable=False)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @lm.user_loader
    def load_user(id):
        return User.query.get(id)

    def __repr__(self):
        return '<User %r>' % (self.name)

association_table = db.Table('association', db.Model.metadata,
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('coupon_id', db.String(8), db.ForeignKey('coupon.id'))
)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(140))
    price = db.Column(db.Integer)
    quantity = db.Column(db.BigInteger)
    coupons = db.relationship("Coupon",
                    secondary=association_table,
                    backref="products")

class Coupon(db.Model):
    __tablename__ = 'coupon'
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(140))
    multiplier = db.Column(db.Float)
    upto = db.Column(db.Integer)
    flatoff = db.Column(db.Integer)
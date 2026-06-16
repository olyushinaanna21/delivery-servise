from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from DB.DBconnect import Base


#таблица users
class UserDB(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    address = Column(String, nullable=True)
    region = Column(Integer, nullable=True)
    role = Column(String(20), nullable=False, default="customer")
    api_key = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)


    courier = relationship("CourierDB", back_populates="user", uselist=False)
    orders = relationship("OrderDB", back_populates="user")
    carts = relationship("CartDB", back_populates="user")


#таблица couriers
class CourierDB(Base):
    __tablename__ = "couriers"

    id_courier = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"), unique=True, nullable=False)
    courier_type = Column(String(10), nullable=False)
    regions = Column(JSON, nullable=False)
    working_hours = Column(JSON, nullable=False)
    max_load = Column(Integer, nullable=False)


    user = relationship("UserDB", back_populates="courier")
    orders = relationship("OrderDB", back_populates="courier")


#таблица products
class ProductDB(Base):
    __tablename__ = "products"

    id_product = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    category = Column(String(50), nullable=True)


    order_items = relationship("OrderItemDB", back_populates="product")
    carts = relationship("CartDB", back_populates="product")


#таблица orders
class OrderDB(Base):
    __tablename__ = "orders"

    id_order = Column(Integer, primary_key=True, index=True)
    order_number = Column(Integer, unique=True, nullable=False, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"), nullable=False)
    id_courier = Column(Integer, ForeignKey("couriers.id_courier"), nullable=True)
    weight = Column(Float, nullable=False)
    region = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    delivery_hours = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="available")
    total_price = Column(Float, nullable=True)
    assign_time = Column(DateTime, nullable=True)
    complete_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


    user = relationship("UserDB", back_populates="orders")
    courier = relationship("CourierDB", back_populates="orders")
    items = relationship("OrderItemDB", back_populates="order")


#таблица order_items
class OrderItemDB(Base):
    __tablename__ = "order_items"

    id_item = Column(Integer, primary_key=True, index=True)
    id_order = Column(Integer, ForeignKey("orders.id_order"), nullable=False)
    id_product = Column(Integer, ForeignKey("products.id_product"), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(Float, nullable=False)
    weight_at_time = Column(Float, nullable=False)


    order = relationship("OrderDB", back_populates="items")
    product = relationship("ProductDB", back_populates="order_items")


#таблица carts
class CartDB(Base):
    __tablename__ = "carts"

    id_cart = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"), nullable=False)
    id_product = Column(Integer, ForeignKey("products.id_product"), nullable=False)
    quantity = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.now)

    # Связи
    user = relationship("UserDB", back_populates="carts")
    product = relationship("ProductDB", back_populates="carts")
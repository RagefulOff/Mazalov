from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from db.engine import Base


# ====================== СПРАВОЧНИКИ ======================
class OrderStatuses(Base):
    __tablename__ = "OrderStatuses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False, unique=True)

    orders = relationship("Orders", back_populates="status")


class MechanicSpecializations(Base):
    __tablename__ = "MechanicSpecializations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    mechanics = relationship(
        "Mechanics",
        secondary="MechanicSpecializationsLink",
        back_populates="specializations"
    )


class MechanicSpecializationsLink(Base):
    __tablename__ = "MechanicSpecializationsLink"
    mechanic_id = Column(Integer, ForeignKey('Mechanics.id', ondelete="CASCADE"), primary_key=True)
    specialization_id = Column(Integer, ForeignKey('MechanicSpecializations.id', ondelete="CASCADE"), primary_key=True)


# ====================== ОСНОВНЫЕ СУЩНОСТИ ======================
class Users(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String(100), nullable=False)
    login = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


class Clients(Base):
    __tablename__ = "Clients"
    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True)

    cars = relationship("Cars", back_populates="client", cascade="all, delete-orphan")
    orders = relationship("Orders", back_populates="client")


class Cars(Base):
    __tablename__ = "Cars"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('Clients.id', ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    year = Column(Integer)
    vin = Column(String(17), unique=True, nullable=False)

    client = relationship("Clients", back_populates="cars")
    orders = relationship("Orders", back_populates="car")


class Mechanics(Base):
    __tablename__ = "Mechanics"
    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True)

    specializations = relationship(
        "MechanicSpecializations",
        secondary="MechanicSpecializationsLink",
        back_populates="mechanics"
    )
    orders = relationship("Orders", back_populates="mechanic")


class Suppliers(Base):
    __tablename__ = "Suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100), unique=True)

    parts = relationship("Parts", back_populates="supplier")


class Parts(Base):
    __tablename__ = "Parts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    supplier_id = Column(Integer, ForeignKey('Suppliers.id'), nullable=False)
    price = Column(Numeric(12, 2), CheckConstraint('price >= 0'), nullable=False)
    quantity_in_stock = Column(Integer, CheckConstraint('quantity_in_stock >= 0'), default=0)

    supplier = relationship("Suppliers", back_populates="parts")
    order_parts = relationship("OrderParts", back_populates="part")


class Works(Base):
    __tablename__ = "Works"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    base_price = Column(Numeric(12, 2), CheckConstraint('base_price > 0'), nullable=False)

    order_works = relationship("OrderWorks", back_populates="work")


# ====================== ЗАКАЗЫ ======================
class Orders(Base):
    __tablename__ = "Orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('Clients.id'), nullable=False)
    car_id = Column(Integer, ForeignKey('Cars.id'), nullable=False)
    mechanic_id = Column(Integer, ForeignKey('Mechanics.id'))
    status_id = Column(Integer, ForeignKey('OrderStatuses.id'), nullable=False)
    created_date = Column(Date, nullable=False)
    completed_date = Column(Date)

    client = relationship("Clients", back_populates="orders")
    car = relationship("Cars", back_populates="orders")
    mechanic = relationship("Mechanics", back_populates="orders")
    status = relationship("OrderStatuses", back_populates="orders")

    works = relationship("OrderWorks", back_populates="order", cascade="all, delete-orphan")
    parts = relationship("OrderParts", back_populates="order", cascade="all, delete-orphan")


class OrderWorks(Base):
    __tablename__ = "OrderWorks"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('Orders.id', ondelete="CASCADE"), nullable=False)
    work_id = Column(Integer, ForeignKey('Works.id'), nullable=False)
    quantity = Column(Integer, CheckConstraint('quantity > 0'), default=1)
    price = Column(Numeric(12, 2), CheckConstraint('price >= 0'), nullable=False)
    is_completed = Column(Boolean, CheckConstraint('is_completed IN (0,1)'), default=False)

    order = relationship("Orders", back_populates="works")
    work = relationship("Works", back_populates="order_works")


class OrderParts(Base):
    __tablename__ = "OrderParts"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('Orders.id', ondelete="CASCADE"), nullable=False)
    part_id = Column(Integer, ForeignKey('Parts.id'), nullable=False)
    quantity = Column(Integer, CheckConstraint('quantity > 0'), nullable=False)
    price = Column(Numeric(12, 2), CheckConstraint('price >= 0'), nullable=False)

    order = relationship("Orders", back_populates="parts")
    part = relationship("Parts", back_populates="order_parts")
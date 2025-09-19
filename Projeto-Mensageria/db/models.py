from sqlalchemy import (
    Column, Integer, String, DECIMAL, Date, ForeignKey, Boolean, DateTime,
    Text, BigInteger, UUID
)
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

# As classes abaixo representam as tabelas do seu banco de dados.
# O nome da tabela é definido em __tablename__.

class Customer(Base):
    __tablename__ = 'customer'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    document = Column(String(20), nullable=False, unique=True)
    
    # Relação com a tabela Bookings
    bookings = relationship("Booking", back_populates="customer")

class Hotel(Base):
    __tablename__ = 'hotel'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    
    # Relação com a tabela Bookings
    bookings = relationship("Booking", back_populates="hotel")

class RoomSubCategory(Base):
    __tablename__ = 'room_sub_categories'

    id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    
    # Relação com a tabela RoomCategory
    room_categories = relationship("RoomCategory", back_populates="sub_category")

class RoomCategory(Base):
    __tablename__ = 'room_categories'

    id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    sub_category_id = Column(String(10), ForeignKey('room_sub_categories.id'))
    
    # Relações
    sub_category = relationship("RoomSubCategory", back_populates="room_categories")
    booked_rooms = relationship("BookedRoom", back_populates="room_category")

class Booking(Base):
    __tablename__ = 'bookings'

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    customer_id = Column(BigInteger, ForeignKey('customer.id'), nullable=False)
    hotel_id = Column(Integer, ForeignKey('hotel.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    indexed_at = Column(DateTime(timezone=True), nullable=False)
    type = Column(String(20), nullable=False)
    source = Column(String(50), nullable=False)
    user_agent = Column(Text)
    ip_address = Column(String)

    # Relações com outras tabelas
    customer = relationship("Customer", back_populates="bookings")
    hotel = relationship("Hotel", back_populates="bookings")
    booked_rooms = relationship("BookedRoom", back_populates="booking", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")

class BookedRoom(Base):
    __tablename__ = 'booked_rooms'
    
    id = Column(BigInteger, primary_key=True)
    booking_uuid = Column(UUID(as_uuid=True), ForeignKey('bookings.uuid', ondelete='CASCADE'), nullable=False)
    room_category_id = Column(String(10), ForeignKey('room_categories.id'), nullable=False)
    room_number = Column(String(10))
    daily_rate = Column(DECIMAL(10, 2), nullable=False)
    number_of_days = Column(Integer, nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False) # Total computado
    checkin_date = Column(Date, nullable=False)
    checkout_date = Column(Date, nullable=False)
    guests = Column(Integer, nullable=False)
    breakfast_included = Column(Boolean, default=False)
    status = Column(String(20), nullable=False)

    # Relações
    booking = relationship("Booking", back_populates="booked_rooms")
    room_category = relationship("RoomCategory", back_populates="booked_rooms")

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    booking_uuid = Column(UUID(as_uuid=True), ForeignKey('bookings.uuid', ondelete='CASCADE'), nullable=False)
    transaction_id = Column(String(255), unique=True)
    method = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    
    # Relação
    booking = relationship("Booking", back_populates="payments")
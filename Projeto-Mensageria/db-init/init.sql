CREATE TABLE customer (
    id BIGINT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    document VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE hotel (
    id INT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL
);

CREATE TABLE room_sub_categories (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE room_categories (
    id VARCHAR(10) PRIMARY KEY,
    sub_category_id VARCHAR(10) REFERENCES room_sub_categories(id),
    name VARCHAR(100) NOT NULL
);

CREATE TABLE bookings (
    uuid UUID PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customer(id),
    hotel_id INT NOT NULL REFERENCES hotel(id),
    created_at TIMESTAMPTZ NOT NULL,
    indexed_at TIMESTAMPTZ NOT NULL,
    type VARCHAR(20) NOT NULL,
    source VARCHAR(50) NOT NULL,
    user_agent TEXT,
    ip_address INET
);

CREATE TABLE booked_rooms (
    id BIGINT PRIMARY KEY,
    booking_uuid UUID NOT NULL REFERENCES bookings(uuid) ON DELETE CASCADE,
    room_category_id VARCHAR(10) NOT NULL REFERENCES room_categories(id),
    room_number VARCHAR(10),
    daily_rate DECIMAL(10, 2) NOT NULL,
    number_of_days INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    checkin_date DATE NOT NULL,
    checkout_date DATE NOT NULL,
    guests INT NOT NULL,
    breakfast_included BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    booking_uuid UUID NOT NULL REFERENCES bookings(uuid) ON DELETE CASCADE,
    transaction_id VARCHAR(255) UNIQUE,
    method VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL
);
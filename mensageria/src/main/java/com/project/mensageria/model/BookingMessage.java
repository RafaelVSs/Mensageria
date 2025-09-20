package com.project.mensageria.model;

import com.fasterxml.jackson.annotation.JsonProperty;


import java.math.BigDecimal;
import java.util.List;

public class BookingMessage {

    public String uuid;
    @JsonProperty("created_at")
    public String createdAt;
    public String type;

    public Customer customer;
    public Hotel hotel;
    @JsonProperty("rooms")
    public List<BookedRoom> rooms;
    public Payment payment;
    public Metadata metadata;


    public static class Customer {
        public long id;
        public String name;
        public String email;
        public String document;
    }

    public static class Hotel {
        public int id;
        public String name;
        public String city;
        public String state;
    }

    public static class BookedRoom {
        public long id;
        @JsonProperty("room_number")
        public String roomNumber;
        @JsonProperty("daily_rate")
        public BigDecimal dailyRate;
        @JsonProperty("number_of_days")
        public int numberOfDays;
        @JsonProperty("checkin_date")
        public String checkinDate;
        @JsonProperty("checkout_date")
        public String checkoutDate;
        @JsonProperty("category")
        public RoomCategory category;
        public String status;
        public int guests;
        @JsonProperty("breakfast_included")
        public boolean breakfastIncluded;
    }

    public static class RoomCategory {
        public String id;
        public String name;
        @JsonProperty("sub_category")
        public RoomSubCategory subCategory;
    }

    public static class RoomSubCategory {
        public String id;
        public String name;
    }

    public static class Payment {
        public String method;
        public String status;
        @JsonProperty("transaction_id")
        public String transactionId;
        public BigDecimal amount;
    }

    public static class Metadata {
        public String source;
        @JsonProperty("user_agent")
        public String userAgent;
        @JsonProperty("ip_address")
        public String ipAddress;
    }
}
package com.project.mensageria.service;

import com.project.mensageria.entity.*;
import com.project.mensageria.model.BookingMessage;
import com.project.mensageria.repository.*;
import jakarta.persistence.EntityManager; // Importar EntityManager se necessário para merge
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors; // Usar streams pode ser mais limpo
import java.util.UUID;

@Service
public class BookingService {

    @Autowired private CustomerRepository customerRepository;
    @Autowired private HotelRepository hotelRepository;
    @Autowired private RoomSubCategoryRepository roomSubCategoryRepository;
    @Autowired private RoomCategoryRepository roomCategoryRepository;
    @Autowired private BookingRepository bookingRepository;


    @Transactional
    public void processAndSaveBooking(BookingMessage message) {

        Customer customer = findOrCreateCustomer(message.customer);
        Hotel hotel = findOrCreateHotel(message.hotel);

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss").withZone(ZoneOffset.UTC);

        Booking booking = new Booking();
        booking.setUuid(UUID.fromString(message.uuid));
        booking.setCreatedAt(OffsetDateTime.parse(message.createdAt, formatter));
        booking.setIndexedAt(OffsetDateTime.now());
        booking.setType(message.type);
        booking.setSource(message.metadata.source);
        booking.setUserAgent(message.metadata.userAgent);
        booking.setIpAddress(message.metadata.ipAddress);
        booking.setCustomer(customer);
        booking.setHotel(hotel);

        List<BookedRoom> rooms = createBookedRooms(message.rooms, booking);
        booking.setRooms(rooms);

        BigDecimal totalAmount = calculateTotalAmount(message.rooms);

        Payment payment = createPayment(message.payment, booking, totalAmount);
        booking.setPayment(payment);

        bookingRepository.save(booking);
    }

    // O 'save' do Spring Data JPA já funciona como "salvar ou atualizar" (merge)
    // se a entidade já tiver um ID e existir no banco.
    private Customer findOrCreateCustomer(BookingMessage.Customer customerDto) {
        return customerRepository.findById(customerDto.id)
                .map(customer -> { // Se encontrou, atualiza os dados
                    customer.setName(customerDto.name);
                    customer.setEmail(customerDto.email);
                    customer.setDocument(customerDto.document);
                    return customerRepository.save(customer);
                })
                .orElseGet(() -> { // Se não encontrou, cria um novo
                    Customer newCustomer = new Customer();
                    newCustomer.setId(customerDto.id);
                    newCustomer.setName(customerDto.name);
                    newCustomer.setEmail(customerDto.email);
                    newCustomer.setDocument(customerDto.document);
                    return customerRepository.save(newCustomer);
                });
    }

    private Hotel findOrCreateHotel(BookingMessage.Hotel hotelDto) {

        return hotelRepository.findById(hotelDto.id)
                .map(hotel -> { // Se encontrou, atualiza os dados
                    hotel.setName(hotelDto.name);
                    hotel.setCity(hotelDto.city);
                    hotel.setState(hotelDto.state);
                    return hotelRepository.save(hotel);
                })
                .orElseGet(() -> {
                    Hotel newHotel = new Hotel();
                    newHotel.setId(hotelDto.id);
                    newHotel.setName(hotelDto.name);
                    newHotel.setCity(hotelDto.city);
                    newHotel.setState(hotelDto.state);
                    return hotelRepository.save(newHotel);
                });
    }

    private List<BookedRoom> createBookedRooms(List<BookingMessage.BookedRoom> roomDtos, Booking booking) {
        if (roomDtos == null || roomDtos.isEmpty()) {
            return new ArrayList<>(); // Retorna lista vazia para evitar NullPointerException
        }

        // Usando Streams para um código mais funcional e limpo
        return roomDtos.stream().map(roomDto -> {
            RoomSubCategory subCategory = findOrCreateRoomSubCategory(roomDto.category.subCategory);
            RoomCategory category = findOrCreateRoomCategory(roomDto.category, subCategory);

            BookedRoom bookedRoom = new BookedRoom();
            bookedRoom.setBooking(booking);
            bookedRoom.setRoomCategory(category);
            bookedRoom.setRoomNumber(roomDto.roomNumber);
            bookedRoom.setDailyRate(roomDto.dailyRate);
            bookedRoom.setNumberOfDays(roomDto.numberOfDays);
            bookedRoom.setCheckinDate(LocalDate.parse(roomDto.checkinDate));
            bookedRoom.setCheckoutDate(LocalDate.parse(roomDto.checkoutDate));
            bookedRoom.setGuests(roomDto.guests);
            bookedRoom.setBreakfastIncluded(roomDto.breakfastIncluded);
            bookedRoom.setStatus(roomDto.status);
            bookedRoom.setTotalAmount(roomDto.dailyRate.multiply(new BigDecimal(roomDto.numberOfDays)));

            return bookedRoom;
        }).collect(Collectors.toList());
    }
    private BigDecimal calculateTotalAmount(List<BookingMessage.BookedRoom> roomDtos) {
        if (roomDtos == null || roomDtos.isEmpty()) {
            return BigDecimal.ZERO;
        }
        return roomDtos.stream()
                // Mapeia cada quarto para seu valor total (diária * dias)
                .map(room -> room.dailyRate.multiply(new BigDecimal(room.numberOfDays)))
                // Soma todos os valores
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    private Payment createPayment(BookingMessage.Payment paymentDto, Booking booking, BigDecimal totalAmount) {
        if (paymentDto == null) return null;

        Payment payment = new Payment();
        payment.setBooking(booking);
        payment.setTransactionId(paymentDto.transactionId);
        payment.setMethod(paymentDto.method);
        payment.setStatus(paymentDto.status);
        payment.setAmount(totalAmount);
        return payment;
    }

    private RoomSubCategory findOrCreateRoomSubCategory(BookingMessage.RoomSubCategory dto) {
        return roomSubCategoryRepository.findById(dto.id).orElseGet(() -> {
            try {
                RoomSubCategory newSubCategory = new RoomSubCategory();
                newSubCategory.setId(dto.id);
                newSubCategory.setName(dto.name);
                return roomSubCategoryRepository.save(newSubCategory);
            } catch (DataIntegrityViolationException e) {
                return roomSubCategoryRepository.findById(dto.id).orElseThrow();
            }
        });
    }
    private RoomCategory findOrCreateRoomCategory(BookingMessage.RoomCategory dto, RoomSubCategory subCategory) {
        return roomCategoryRepository.findById(dto.id).orElseGet(() -> {
            try {
                RoomCategory newCategory = new RoomCategory();
                newCategory.setId(dto.id);
                newCategory.setName(dto.name);
                newCategory.setSubCategory(subCategory);
                return roomCategoryRepository.save(newCategory);
            } catch (DataIntegrityViolationException e) {
                return roomCategoryRepository.findById(dto.id).orElseThrow();
            }
        });
    }
}
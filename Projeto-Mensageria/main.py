# Seu código de importação permanece o mesmo
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import Optional, List, Dict, Any
from uuid import UUID

# Importa os componentes corretos: engine, Base, get_db e AsyncSession
from db.database import engine, Base, get_db, AsyncSession
# Importa os modelos de dados
from db import models

app = FastAPI(title="API de Reservas de Hotel")


@app.get("/reserves", response_model=List[Dict[str, Any]])
async def get_reserves(
    uuid: Optional[UUID] = Query(None, description="Filtrar por UUID da reserva"),
    client_id: Optional[int] = Query(None, description="Filtrar por ID do cliente"),
    room_id: Optional[int] = Query(None, description="Filtrar por ID do quarto"),
    hotel_id: Optional[int] = Query(None, description="Filtrar por ID do hotel"),
    db: AsyncSession = Depends(get_db)
):
    """
    Consulta reservas de hotel com filtros opcionais.
    """
    query = select(models.Booking).options(
        joinedload(models.Booking.customer),
        joinedload(models.Booking.hotel),
        joinedload(models.Booking.booked_rooms).joinedload(models.BookedRoom.room_category).joinedload(models.RoomCategory.sub_category),
        joinedload(models.Booking.payments)
    )

    # Aplica os filtros
    if uuid:
        query = query.filter(models.Booking.uuid == uuid)
    if client_id:
        query = query.filter(models.Booking.customer_id == client_id)
    if hotel_id:
        query = query.filter(models.Booking.hotel_id == hotel_id)

    # Para buscar por room_id, usamos um JOIN com a tabela BookedRoom
    if room_id:
        query = query.join(models.Booking.booked_rooms).filter(models.BookedRoom.id == room_id)

    # Executa a query de forma assíncrona
    result = await db.execute(query)
    reserves = result.unique().scalars().all()

    if not reserves:
        raise HTTPException(status_code=404, detail="Nenhuma reserva encontrada com os critérios fornecidos.")

    response_data = []
    for reserve in reserves:
        # Pega os dados do cliente e hotel
        customer_data = {
            "id": reserve.customer.id,
            "name": reserve.customer.name,
            "email": reserve.customer.email,
            "document": reserve.customer.document,
        }

        hotel_data = {
            "id": reserve.hotel.id,
            "name": reserve.hotel.name,
            "city": reserve.hotel.city,
            "state": reserve.hotel.state,
        }

        # Computa o valor total de cada quarto e da reserva
        total_reserve_value = 0
        booked_rooms_list = []
        for room in reserve.booked_rooms:
            total_room_value = room.daily_rate * room.number_of_days
            total_reserve_value += total_room_value
            
            booked_rooms_list.append({
                "id": room.id,
                "room number": room.room_number,
                "daily rate": float(room.daily_rate),
                "number of days": room.number_of_days,
                "checkin date": room.checkin_date.isoformat(),
                "checkout date": room.checkout_date.isoformat(),
                "category": {
                    "id": room.room_category.id,
                    "name": room.room_category.name,
                    "sub category": {
                        "id": room.room_category.sub_category.id,
                        "name": room.room_category.sub_category.name
                    } if room.room_category.sub_category else None
                },
                "status": room.status,
                "guests": room.guests,
                "breakfast_included": room.breakfast_included,
                "total_room_value": float(total_room_value)
            })

        # Prepara os dados de pagamento
        payment_data = {
            "method": reserve.payments[0].method,
            "status": reserve.payments[0].status,
            "transaction_id": reserve.payments[0].transaction_id,
        } if reserve.payments else None

        # Monta a resposta final
        response_data.append({
            "uuid": str(reserve.uuid),
            "created at": reserve.created_at.isoformat(),
            "indexed_at": reserve.indexed_at.isoformat(),
            "type": reserve.type,
            "customer": customer_data,
            "hotel": hotel_data,
            "rooms": booked_rooms_list,
            "payment": payment_data,
            "metadata": {
                "source": reserve.source,
                "user agent": reserve.user_agent,
                "ip address": str(reserve.ip_address), # Linha corrigida
            },
            "total_reserve_value": float(total_reserve_value)
        })

    return response_data


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

# Importe os modelos de dados e a função de sessão do seu db/
# Ajuste o caminho se necessário, mas .db.database parece ser o correto
from db.database import engine, Base, SessionLocal
from db import models

# Crie a aplicação FastAPI
app = FastAPI()

# Crie as tabelas no banco de dados se elas não existirem
def create_tables():
    Base.metadata.create_all(bind=engine)

# Função para gerenciar a sessão do banco de dados (injeção de dependência)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota para o seu projeto
@app.on_event("startup")
def startup_event():
    create_tables()

@app.get("/reserves", response_model=List[Dict[str, Any]])
def get_reserves(
    uuid: Optional[str] = Query(None, description="Filtrar por UUID da reserva"),
    client_id: Optional[int] = Query(None, description="Filtrar por ID do cliente"),
    room_id: Optional[int] = Query(None, description="Filtrar por ID do quarto"),
    hotel_id: Optional[int] = Query(None, description="Filtrar por ID do hotel"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Reserva)

    if uuid:
        query = query.filter(models.Reserva.uuid == uuid)
    if client_id:
        query = query.filter(models.Reserva.client_id == client_id)
    if hotel_id:
        query = query.filter(models.Reserva.hotel_id == hotel_id)

    # Para buscar por room_id, precisamos de um JOIN com a tabela quarto_reservado
    if room_id:
        query = query.join(models.Reserva.quartos_reservados).filter(models.QuartoReservado.id == room_id)

    reserves = query.all()

    if not reserves:
        raise HTTPException(status_code=404, detail="Nenhuma reserva encontrada.")

    # Converte os objetos do banco de dados para o formato de resposta
    response_data = []
    for reserve in reserves:
        total_reserve_value = 0
        reserved_rooms = []
        
        for room in reserve.quartos_reservados:
            room_value = room.valor * (room.data_saida - room.data_entrada).days # Exemplo de calculo do valor total de um quarto
            total_reserve_value += room_value
            reserved_rooms.append({
                "id_quarto": room.id,
                "valor_quarto": room.valor,
                "valor_total_quarto": room_value
            })

        response_data.append({
            "uuid": reserve.uuid,
            "client_id": reserve.client_id,
            "hotel_id": reserve.hotel_id,
            "data_criacao": reserve.data_criacao.isoformat(),
            "valor_total_reserva": total_reserve_value,
            "quartos_reservados": reserved_rooms,
        })
        
    return response_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
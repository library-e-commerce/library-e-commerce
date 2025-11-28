from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.pedido_service import PedidoService
from app.domain.pedido_model import PedidoCreate, PedidoResponse

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

# [API-PEDIDO-001] Endpoints para crear pedido
@router.post("/", response_model=PedidoResponse, status_code=201)
def create_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    """Crear nuevo pedido"""
    service = PedidoService(db)
    return service.create_pedido(pedido)

@router.post("/from-carrito/{carrito_id}", response_model=PedidoResponse, status_code=201)
def create_from_carrito(carrito_id: int, db: Session = Depends(get_db)):
    """Crear pedido desde carrito"""
    service = PedidoService(db)
    pedido = service.create_from_carrito(carrito_id)
    if not pedido:
        raise HTTPException(status_code=400, detail="No se pudo crear el pedido")
    return pedido

@router.get("/{pedido_id}", response_model=PedidoResponse)
def get_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Obtener pedido por ID"""
    service = PedidoService(db)
    pedido = service.get_pedido(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido

@router.get("/usuario/{usuario_id}", response_model=list[PedidoResponse])
def get_pedidos_by_user(usuario_id: int, db: Session = Depends(get_db)):
    """Listar pedidos de un usuario"""
    service = PedidoService(db)
    return service.get_pedidos_by_user(usuario_id)


# [API-PEDIDO-002] Endpoint para cancelar pedido
@router.put("/{pedido_id}/cancelar", response_model=PedidoResponse)
def cancel_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Cancelar un pedido"""
    service = PedidoService(db)
    pedido = service.cancel_pedido(pedido_id)
    if not pedido:
        raise HTTPException(status_code=400, detail="No se pudo cancelar el pedido")
    return pedido
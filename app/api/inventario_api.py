from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.inventario_service import InventarioService
from app.domain.inventario_model import InventarioUpdate, InventarioResponse

router = APIRouter(prefix="/inventario", tags=["Inventario"])

# [API-INVENTARIO-001] Endpoint para actualizar stock (Admin)
@router.put("/{libro_id}/stock", response_model=InventarioResponse)
def update_stock(libro_id: int, inventario: InventarioUpdate, db: Session = Depends(get_db)):
    """Actualizar stock de un libro (Admin)"""
    service = InventarioService(db)
    updated = service.update_stock(libro_id, inventario)
    if not updated:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")
    return updated
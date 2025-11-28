from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.facturacion_service import FacturacionService
from app.domain.facturacion_model import FacturacionResponse

router = APIRouter(prefix="/facturacion", tags=["Facturación"])

# [API-FACTURA-001] Endpoints para consultar factura
@router.get("/{factura_id}", response_model=FacturacionResponse)
def get_facturacion(factura_id: int, db: Session = Depends(get_db)):
    """Consultar factura por ID"""
    service = FacturacionService(db)
    factura = service.get_facturacion(factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura

@router.get("/usuario/{usuario_id}", response_model=list[FacturacionResponse])
def get_facturaciones_by_user(usuario_id: int, db: Session = Depends(get_db)):
    """Consultar facturas por usuario"""
    service = FacturacionService(db)
    return service.get_facturaciones_by_user(usuario_id)

@router.get("/pedido/{pedido_id}", response_model=FacturacionResponse)
def get_facturacion_by_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Consultar factura por pedido"""
    service = FacturacionService(db)
    factura = service.get_facturacion_by_pedido(pedido_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura

# [API-FACTURA-002] Endpoint para anular factura (Admin)
@router.delete("/{factura_id}", status_code=204)
def anular_factura(factura_id: int, db: Session = Depends(get_db)):
    """Anular factura (Admin)"""
    service = FacturacionService(db)
    service.anular_factura(factura_id)
    return None
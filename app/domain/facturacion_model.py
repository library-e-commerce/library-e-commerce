from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from enum import Enum


class EstadoFacturaEnum(str, Enum):
	EMITIDA = "EMITIDA"
	PAGADA = "PAGADA"
	ANULADA = "ANULADA"


class MonedaEnum(str, Enum):
	COP = "COP"
	USD = "USD"
	EUR = "EUR"


class FacturaItem(BaseModel):
	idlibro: int
	cantidad: int
	precio_unitario: Decimal
	subtotal_item: Decimal
	impuesto_item: Decimal


class FacturacionCreate(BaseModel):
	idpedido: int
	idusuario: int
	metodo_pago: str
	datos_fiscales: str
	moneda: MonedaEnum = MonedaEnum.COP
	notas: str | None = None


class FacturacionUpdate(BaseModel):
	estado: EstadoFacturaEnum | None = None
	notas: str | None = None


class FacturacionResponse(BaseModel):
	idfactura: int
	idpedido: int
	metodo_pago: str
	fecha: datetime
	total: Decimal
	impuesto: Decimal
	idusuario: int
	subtotal: Decimal
	descuentos: Decimal
	items: list[FacturaItem]
	estado: EstadoFacturaEnum
	fecha_actualizacion: datetime
	ultimo_usuario_modifico: int | None
	datos_fiscales: str
	moneda: MonedaEnum
	notas: str | None

	model_config = {"from_attributes": True}

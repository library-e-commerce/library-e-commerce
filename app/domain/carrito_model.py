from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from enum import Enum


class EstadoCarritoEnum(str, Enum):
	ACTIVO = "ACTIVO"
	ABANDONADO = "ABANDONADO"
	CONVERTIDO = "CONVERTIDO"


class CarritoItem(BaseModel):
	idlibro: int
	cantidad: int
	precio_unitario: Decimal
	subtotal_item: Decimal


class CarritoCreate(BaseModel):
	idusuario: int
	sesion_id: str | None = None


class CarritoAddItem(BaseModel):
	idlibro: int
	cantidad: int


class CarritoUpdate(BaseModel):
	estado: EstadoCarritoEnum | None = None


class CarritoResponse(BaseModel):
	idcarrito: int
	idusuario: int
	items: list[CarritoItem]
	fecha_creacion: datetime
	fecha_actualizacion: datetime
	subtotal: Decimal
	descuentos: Decimal
	impuestos: Decimal
	total: Decimal
	estado: EstadoCarritoEnum
	sesion_id: str | None
	ultimo_usuario_modifico: int | None

	model_config = {"from_attributes": True}

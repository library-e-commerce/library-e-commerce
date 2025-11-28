from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from enum import Enum


class EstadoPedidoEnum(str, Enum):
	PENDIENTE = "PENDIENTE"
	PAGADO = "PAGADO"
	ENVIADO = "ENVIADO"
	ENTREGADO = "ENTREGADO"
	CANCELADO = "CANCELADO"


class MetodoPagoEnum(str, Enum):
	TARJETA = "TARJETA"
	PAYPAL = "PAYPAL"
	TRANSFERENCIA = "TRANSFERENCIA"


class PedidoItem(BaseModel):
	idlibro: int
	cantidad: int
	precio_unitario: Decimal
	subtotal_item: Decimal


class PedidoCreate(BaseModel):
	idusuario: int
	items: list[PedidoItem]
	direccion_envio: str
	metodo_pago: MetodoPagoEnum
	idcarrito: int | None = None
	notas: str | None = None


class PedidoUpdate(BaseModel):
	estado: EstadoPedidoEnum | None = None
	notas: str | None = None


class PedidoResponse(BaseModel):
	idpedido: int
	idusuario: int
	fecha: datetime
	estado: EstadoPedidoEnum
	items: list[PedidoItem]
	total: Decimal
	direccion_envio: str
	metodo_pago: MetodoPagoEnum
	subtotal: Decimal
	descuentos: Decimal
	impuestos: Decimal
	fecha_actualizacion: datetime
	ultimo_usuario_modifico: int | None
	idcarrito: int | None
	numero_factura: str | None
	notas: str | None

	model_config = {"from_attributes": True}

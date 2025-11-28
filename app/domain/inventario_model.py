from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class EstadoInventarioEnum(str, Enum):
	ACTIVO = "ACTIVO"
	BAJO_STOCK = "BAJO_STOCK"
	AGOTADO = "AGOTADO"


class InventarioCreate(BaseModel):
	idlibro: int
	umbral_minimo: int = 5
	stock_disponible: int
	ubicacion_almacen: str | None = None
	notas: str | None = None


class InventarioUpdate(BaseModel):
	umbral_minimo: int | None = None
	stock_disponible: int | None = None
	stock_reservado: int | None = None
	estado: EstadoInventarioEnum | None = None
	ubicacion_almacen: str | None = None
	notas: str | None = None
	lote_reabastecimiento: str | None = None


class InventarioReabastecer(BaseModel):
	cantidad: int
	lote_reabastecimiento: str | None = None
	notas: str | None = None


class InventarioResponse(BaseModel):
	idinventario: int
	idlibro: int
	umbral_minimo: int
	stock_disponible: int
	stock_reservado: int
	fecha_ultima_actualizacion: datetime
	ultimo_usuario_modifico: int | None
	estado: EstadoInventarioEnum
	fecha_ultimo_reabastecimiento: datetime | None
	notas: str | None
	ubicacion_almacen: str | None
	lote_reabastecimiento: str | None

	model_config = {"from_attributes": True}

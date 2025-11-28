from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from enum import Enum


class FormatoEnum(str, Enum):
	TAPA_DURA = "Tapa Dura"
	TAPA_BLANDA = "Tapa Blanda"
	EBOOK = "E-book"


class IdiomaEnum(str, Enum):
	ESPANOL = "Español"
	INGLES = "Inglés"
	FRANCES = "Francés"
	ALEMAN = "Alemán"


class BookCreate(BaseModel):
	titulo: str
	autor: str | list[str]
	categoria: str | list[str]
	precio: Decimal
	stock: int
	editorial: str | None = None
	año_publicacion: int
	idioma: IdiomaEnum
	formato: FormatoEnum
	descripcion: str | None = None
	imagen_portada: str | None = None
	descuento: Decimal = Decimal("0")


class BookUpdate(BaseModel):
	titulo: str | None = None
	autor: str | list[str] | None = None
	categoria: str | list[str] | None = None
	precio: Decimal | None = None
	stock: int | None = None
	editorial: str | None = None
	año_publicacion: int | None = None
	idioma: IdiomaEnum | None = None
	formato: FormatoEnum | None = None
	descripcion: str | None = None
	imagen_portada: str | None = None
	activo: bool | None = None
	descuento: Decimal | None = None


class BookResponse(BaseModel):
	idlibro: int
	titulo: str
	autor: str | list[str]
	categoria: str | list[str]
	precio: Decimal
	stock: int
	editorial: str | None
	año_publicacion: int
	idioma: IdiomaEnum
	formato: FormatoEnum
	descripcion: str | None
	imagen_portada: str | None
	activo: bool
	fecha_creacion: datetime
	fecha_ultima_actualizacion: datetime
	descuento: Decimal

	model_config = {"from_attributes": True}
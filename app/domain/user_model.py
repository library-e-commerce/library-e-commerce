from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from enum import Enum


class RolEnum(str, Enum):
	CLIENTE = "CLIENTE"
	ADMIN = "ADMIN"
	VENDEDOR = "VENDEDOR"


class UserCreate(BaseModel):
	nombre: str
	apellido: str
	correo: EmailStr
	contraseña: str
	rol: RolEnum = RolEnum.CLIENTE
	fecha_nacimiento: date
	direccion: str
	telefono: str
	preferencias: list[str] | None = None
	acepta_terminos: bool


class UserUpdate(BaseModel):
	nombre: str | None = None
	apellido: str | None = None
	correo: EmailStr | None = None
	contraseña: str | None = None
	rol: RolEnum | None = None
	fecha_nacimiento: date | None = None
	direccion: str | None = None
	telefono: str | None = None
	preferencias: list[str] | None = None
	activo: bool | None = None


class UserResponse(BaseModel):
	idusuario: int
	nombre: str
	apellido: str
	correo: EmailStr
	rol: RolEnum
	fecha_nacimiento: date
	direccion: str
	telefono: str
	fecha_creacion: datetime
	activo: bool
	email_verificado: bool
	preferencias: list[str] | None
	acepta_terminos: bool

	model_config = {"from_attributes": True}
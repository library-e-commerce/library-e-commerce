from sqlalchemy.orm import Session
from app.repository.carrito_repository import CarritoRepository
from app.repository.book_repository import BookRepository
from app.repository.user_repository import UserRepository
from app.domain.carrito_model import CarritoCreate, CarritoAddItem, CarritoUpdate, CarritoResponse, CarritoItem
from fastapi import HTTPException
from decimal import Decimal


class CarritoService:
	def __init__(self, db: Session):
		self.carrito_repo = CarritoRepository(db)
		self.book_repo = BookRepository(db)
		self.user_repo = UserRepository(db)

	def create_carrito(self, carrito_data: CarritoCreate) -> CarritoResponse:
		# Verificar que el usuario existe
		user = self.user_repo.get_user_by_id(carrito_data.idusuario)
		if not user:
			raise HTTPException(status_code=404, detail="Usuario no encontrado")

		# Verificar si ya tiene un carrito activo
		existing = self.carrito_repo.get_carrito_by_user(carrito_data.idusuario)
		if existing:
			return CarritoResponse.model_validate(existing)

		carrito = self.carrito_repo.create_carrito(
			idusuario=carrito_data.idusuario,
			sesion_id=carrito_data.sesion_id
		)
		return CarritoResponse.model_validate(carrito)

	def get_carrito(self, carrito_id: int) -> CarritoResponse:
		carrito = self.carrito_repo.get_carrito_by_id(carrito_id)
		if not carrito:
			raise HTTPException(status_code=404, detail="Carrito no encontrado")
		return CarritoResponse.model_validate(carrito)

	def get_carrito_by_user(self, idusuario: int) -> CarritoResponse:
		carrito = self.carrito_repo.get_carrito_by_user(idusuario)
		if not carrito:
			raise HTTPException(status_code=404, detail="Carrito no encontrado")
		return CarritoResponse.model_validate(carrito)

	def add_item(self, carrito_id: int, item_data: CarritoAddItem) -> CarritoResponse:
		carrito = self.carrito_repo.get_carrito_by_id(carrito_id)
		if not carrito:
			raise HTTPException(status_code=404, detail="Carrito no encontrado")

		# Verificar que el libro existe
		book = self.book_repo.get_book_by_id(item_data.idlibro)
		if not book:
			raise HTTPException(status_code=404, detail="Libro no encontrado")

		# Verificar stock
		if book.stock < item_data.cantidad:
			raise HTTPException(status_code=400, detail="Stock insuficiente")

		# Crear item
		precio_unitario = Decimal(book.precio)
		subtotal_item = precio_unitario * item_data.cantidad

		item = {
			"idlibro": item_data.idlibro,
			"cantidad": item_data.cantidad,
			"precio_unitario": str(precio_unitario),
			"subtotal_item": str(subtotal_item)
		}

		# Añadir al carrito
		carrito = self.carrito_repo.add_item(carrito, item)
		carrito = self.carrito_repo.recalcular_totales(carrito)

		return CarritoResponse.model_validate(carrito)

	def remove_item(self, carrito_id: int, idlibro: int) -> CarritoResponse:
		carrito = self.carrito_repo.get_carrito_by_id(carrito_id)
		if not carrito:
			raise HTTPException(status_code=404, detail="Carrito no encontrado")

		carrito = self.carrito_repo.remove_item(carrito, idlibro)
		carrito = self.carrito_repo.recalcular_totales(carrito)

		return CarritoResponse.model_validate(carrito)

	def update_carrito(self, carrito_id: int, carrito_data: CarritoUpdate) -> CarritoResponse:
		carrito = self.carrito_repo.get_carrito_by_id(carrito_id)
		if not carrito:
			raise HTTPException(status_code=404, detail="Carrito no encontrado")

		if carrito_data.estado is not None:
			carrito.estado = carrito_data.estado

		updated_carrito = self.carrito_repo.update_carrito(carrito)
		return CarritoResponse.model_validate(updated_carrito)

	def delete_carrito(self, carrito_id: int) -> None:
		carrito = self.carrito_repo.get_carrito_by_id(carrito_id)
		if not carrito:
			raise HTTPException(status_code=404, detail="Carrito no encontrado")
		self.carrito_repo.delete_carrito(carrito)

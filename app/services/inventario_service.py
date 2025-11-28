from sqlalchemy.orm import Session
from app.repository.inventario_repository import InventarioRepository
from app.repository.book_repository import BookRepository
from app.domain.inventario_model import InventarioCreate, InventarioUpdate, InventarioReabastecer, InventarioResponse
from fastapi import HTTPException


class InventarioService:
	def __init__(self, db: Session):
		self.inventario_repo = InventarioRepository(db)
		self.book_repo = BookRepository(db)

	def create_inventario(self, inventario_data: InventarioCreate) -> InventarioResponse:
		# Verificar que el libro existe
		book = self.book_repo.get_book_by_id(inventario_data.idlibro)
		if not book:
			raise HTTPException(status_code=404, detail="Libro no encontrado")

		# Verificar si ya existe inventario para este libro
		existing = self.inventario_repo.get_inventario_by_libro(inventario_data.idlibro)
		if existing:
			raise HTTPException(status_code=400, detail="Ya existe inventario para este libro")

		inventario = self.inventario_repo.create_inventario(
			idlibro=inventario_data.idlibro,
			stock_disponible=inventario_data.stock_disponible,
			umbral_minimo=inventario_data.umbral_minimo,
			ubicacion_almacen=inventario_data.ubicacion_almacen,
			notas=inventario_data.notas
		)

		return InventarioResponse.model_validate(inventario)

	def get_inventario(self, inventario_id: int) -> InventarioResponse:
		inventario = self.inventario_repo.get_inventario_by_id(inventario_id)
		if not inventario:
			raise HTTPException(status_code=404, detail="Inventario no encontrado")
		return InventarioResponse.model_validate(inventario)

	def get_inventario_by_book(self, idlibro: int) -> InventarioResponse:
		inventario = self.inventario_repo.get_inventario_by_libro(idlibro)
		if not inventario:
			raise HTTPException(status_code=404, detail="Inventario no encontrado")
		return InventarioResponse.model_validate(inventario)

	def get_inventarios_bajo_stock(self) -> list[InventarioResponse]:
		inventarios = self.inventario_repo.get_bajo_stock()
		return [InventarioResponse.model_validate(i) for i in inventarios]

	def reabastecer(self, inventario_id: int, reabastecer_data: InventarioReabastecer) -> InventarioResponse:
		inventario = self.inventario_repo.get_inventario_by_id(inventario_id)
		if not inventario:
			raise HTTPException(status_code=404, detail="Inventario no encontrado")

		if reabastecer_data.cantidad <= 0:
			raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

		inventario = self.inventario_repo.reabastecer(inventario, reabastecer_data.cantidad)

		# Actualizar stock del libro
		book = self.book_repo.get_book_by_id(inventario.idlibro)
		if book:
			book.stock += reabastecer_data.cantidad
			self.book_repo.update_book(book)

		return InventarioResponse.model_validate(inventario)

	def reservar_stock(self, inventario_id: int, cantidad: int) -> InventarioResponse:
		inventario = self.inventario_repo.get_inventario_by_id(inventario_id)
		if not inventario:
			raise HTTPException(status_code=404, detail="Inventario no encontrado")

		if cantidad <= 0:
			raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

		if inventario.cantidad_disponible < cantidad:
			raise HTTPException(status_code=400, detail="Stock insuficiente")

		inventario = self.inventario_repo.reservar_stock(inventario, cantidad)
		return InventarioResponse.model_validate(inventario)

	def liberar_stock(self, inventario_id: int, cantidad: int) -> InventarioResponse:
		inventario = self.inventario_repo.get_inventario_by_id(inventario_id)
		if not inventario:
			raise HTTPException(status_code=404, detail="Inventario no encontrado")

		if cantidad <= 0:
			raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

		inventario = self.inventario_repo.liberar_stock(inventario, cantidad)
		return InventarioResponse.model_validate(inventario)

	def update_inventario(self, inventario_id: int, inventario_data: InventarioUpdate) -> InventarioResponse:
		inventario = self.inventario_repo.get_inventario_by_id(inventario_id)
		if not inventario:
			raise HTTPException(status_code=404, detail="Inventario no encontrado")

		if inventario_data.stock_minimo is not None:
			if inventario_data.stock_minimo < 0:
				raise HTTPException(status_code=400, detail="Stock mínimo no puede ser negativo")
			inventario.stock_minimo = inventario_data.stock_minimo

		if inventario_data.ubicacion is not None:
			inventario.ubicacion = inventario_data.ubicacion

		if inventario_data.estado is not None:
			inventario.estado = inventario_data.estado

		updated_inventario = self.inventario_repo.update_inventario(inventario)
		return InventarioResponse.model_validate(updated_inventario)

	def delete_inventario(self, inventario_id: int) -> None:
		inventario = self.inventario_repo.get_inventario_by_id(inventario_id)
		if not inventario:
			raise HTTPException(status_code=404, detail="Inventario no encontrado")

		# No permitir eliminar si hay stock reservado
		if inventario.cantidad_reservada > 0:
			raise HTTPException(status_code=400, detail="No se puede eliminar inventario con stock reservado")

		self.inventario_repo.delete_inventario(inventario)

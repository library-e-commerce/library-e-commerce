from sqlalchemy.orm import Session
from app.repository.book_repository import BookRepository
from app.domain.book_model import BookCreate, BookUpdate, BookResponse
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime


class BookService:
	def __init__(self, db: Session):
		self.repository = BookRepository(db)

	def create_book(self, book_data: BookCreate) -> BookResponse:
		# Validar año
		current_year = datetime.now().year
		if book_data.año_publicacion < 1700 or book_data.año_publicacion > current_year:
			raise HTTPException(
				status_code=400,
				detail=f"Año de publicación inválido (debe estar entre 1700 y {current_year})"
			)

		# Validar precio y stock
		if book_data.precio < 0:
			raise HTTPException(status_code=400, detail="El precio debe ser mayor o igual a 0")
		
		if book_data.stock < 0:
			raise HTTPException(status_code=400, detail="El stock debe ser mayor o igual a 0")

		# Validar descuento
		if book_data.descuento < 0:
			raise HTTPException(status_code=400, detail="El descuento debe ser mayor o igual a 0")

		book = self.repository.create_book(
			titulo=book_data.titulo,
			autor=book_data.autor,
			categoria=book_data.categoria,
			precio=book_data.precio,
			stock=book_data.stock,
			editorial=book_data.editorial,
			año_publicacion=book_data.año_publicacion,
			idioma=book_data.idioma,
			formato=book_data.formato,
			descripcion=book_data.descripcion,
			imagen_portada=book_data.imagen_portada,
			descuento=book_data.descuento
		)
		return BookResponse.model_validate(book)

	def get_book(self, book_id: int) -> BookResponse:
		book = self.repository.get_book_by_id(book_id)
		if not book:
			raise HTTPException(status_code=404, detail="Libro no encontrado")
		return BookResponse.model_validate(book)

	def get_all_books(self) -> list[BookResponse]:
		books = self.repository.get_all_books()
		return [BookResponse.model_validate(book) for book in books]

	def update_book(self, book_id: int, book_data: BookUpdate) -> BookResponse:
		book = self.repository.get_book_by_id(book_id)
		if not book:
			raise HTTPException(status_code=404, detail="Libro no encontrado")

		# Actualizar solo campos proporcionados
		if book_data.titulo is not None:
			book.titulo = book_data.titulo
		if book_data.autor is not None:
			book.autor = book_data.autor if isinstance(book_data.autor, list) else [book_data.autor]
		if book_data.categoria is not None:
			book.categoria = book_data.categoria if isinstance(book_data.categoria, list) else [book_data.categoria]
		if book_data.precio is not None:
			if book_data.precio < 0:
				raise HTTPException(status_code=400, detail="El precio debe ser mayor o igual a 0")
			book.precio = str(book_data.precio)
		if book_data.stock is not None:
			if book_data.stock < 0:
				raise HTTPException(status_code=400, detail="El stock debe ser mayor o igual a 0")
			book.stock = book_data.stock
		if book_data.editorial is not None:
			book.editorial = book_data.editorial
		if book_data.año_publicacion is not None:
			current_year = datetime.now().year
			if book_data.año_publicacion < 1700 or book_data.año_publicacion > current_year:
				raise HTTPException(status_code=400, detail="Año de publicación inválido")
			book.año_publicacion = book_data.año_publicacion
		if book_data.idioma is not None:
			book.idioma = book_data.idioma
		if book_data.formato is not None:
			book.formato = book_data.formato
		if book_data.descripcion is not None:
			book.descripcion = book_data.descripcion
		if book_data.imagen_portada is not None:
			book.imagen_portada = book_data.imagen_portada
		if book_data.activo is not None:
			book.activo = book_data.activo
		if book_data.descuento is not None:
			if book_data.descuento < 0:
				raise HTTPException(status_code=400, detail="El descuento debe ser mayor o igual a 0")
			book.descuento = str(book_data.descuento)

		updated_book = self.repository.update_book(book)
		return BookResponse.model_validate(updated_book)

	def delete_book(self, book_id: int) -> None:
		book = self.repository.get_book_by_id(book_id)
		if not book:
			raise HTTPException(status_code=404, detail="Libro no encontrado")
		self.repository.delete_book(book)

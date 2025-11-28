from sqlalchemy.orm import Session
from app.database import BookDB
from decimal import Decimal
from datetime import datetime


class BookRepository:
	"""Repository handling DB operations for BookDB."""

	def __init__(self, db: Session):
		self.db = db

	def create_book(
		self,
		titulo: str,
		autor: str | list[str],
		categoria: str | list[str],
		precio: Decimal,
		stock: int,
		año_publicacion: int,
		idioma: str,
		formato: str,
		editorial: str | None = None,
		descripcion: str | None = None,
		imagen_portada: str | None = None,
		descuento: Decimal = Decimal("0")
	) -> BookDB:
		book = BookDB(
			titulo=titulo,
			autor=autor if isinstance(autor, list) else [autor],
			categoria=categoria if isinstance(categoria, list) else [categoria],
			precio=str(precio),
			stock=stock,
			editorial=editorial,
			año_publicacion=año_publicacion,
			idioma=idioma,
			formato=formato,
			descripcion=descripcion,
			imagen_portada=imagen_portada,
			activo=True,
			fecha_creacion=datetime.utcnow(),
			fecha_ultima_actualizacion=datetime.utcnow(),
			descuento=str(descuento)
		)
		self.db.add(book)
		self.db.commit()
		self.db.refresh(book)
		return book

	def get_book_by_id(self, book_id: int) -> BookDB | None:
		return self.db.query(BookDB).filter(BookDB.idlibro == book_id).first()

	def get_all_books(self) -> list[BookDB]:
		return self.db.query(BookDB).all()

	def update_book(self, book: BookDB) -> BookDB:
		book.fecha_ultima_actualizacion = datetime.utcnow()
		self.db.commit()
		self.db.refresh(book)
		return book

	def delete_book(self, book: BookDB) -> None:
		self.db.delete(book)
		self.db.commit()

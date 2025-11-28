from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.book_service import BookService
from app.domain.book_model import BookResponse
from app.domain.book_model import BookCreate, BookUpdate

router = APIRouter(prefix="/libros", tags=["Libros"])

# [API-LIBRO-001] Endpoints para consultar el catálogo de libros
@router.get("/", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db)):
    """Listar todos los libros"""
    service = BookService(db)
    return service.get_all_books()

@router.get("/{libro_id}", response_model=BookResponse)
def get_book(libro_id: int, db: Session = Depends(get_db)):
    """Obtener libro por ID"""
    service = BookService(db)
    book = service.get_book(libro_id)
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return book

@router.get("/buscar/", response_model=list[BookResponse])
def search_books(
    titulo: str | None = Query(None),
    autor: str | None = Query(None),
    db: Session = Depends(get_db)
):
    """Buscar libros por título o autor"""
    service = BookService(db)
    return service.search_books(titulo, autor)


# [API-LIBRO-002] Endpoints para crear nuevos libros (Admin)
@router.post("/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Crear nuevo libro (Admin)"""
    service = BookService(db)
    return service.create_book(book)

@router.put("/{libro_id}", response_model=BookResponse)
def update_book(libro_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    """Actualizar libro (Admin)"""
    service = BookService(db)
    updated_book = service.update_book(libro_id, book)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return updated_book

@router.delete("/{libro_id}", status_code=204)
def delete_book(libro_id: int, db: Session = Depends(get_db)):
    """Eliminar libro (Admin)"""
    service = BookService(db)
    service.delete_book(libro_id)
    return None
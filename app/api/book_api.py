from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.book_service import BookService
from app.domain.book_model import BookResponse

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
from sqlalchemy.orm import Session
from app.database import CarritoDB
from datetime import datetime
from decimal import Decimal
import json


class CarritoRepository:
	"""Repository handling DB operations for CarritoDB."""

	def __init__(self, db: Session):
		self.db = db

	def create_carrito(self, idusuario: int, sesion_id: str | None = None) -> CarritoDB:
		carrito = CarritoDB(
			idusuario=idusuario,
			items=[],
			fecha_creacion=datetime.utcnow(),
			fecha_actualizacion=datetime.utcnow(),
			subtotal="0",
			descuentos="0",
			impuestos="0",
			total="0",
			estado="ACTIVO",
			sesion_id=sesion_id
		)
		self.db.add(carrito)
		self.db.commit()
		self.db.refresh(carrito)
		return carrito

	def get_carrito_by_id(self, carrito_id: int) -> CarritoDB | None:
		return self.db.query(CarritoDB).filter(CarritoDB.idcarrito == carrito_id).first()

	def get_carrito_by_user(self, idusuario: int) -> CarritoDB | None:
		return self.db.query(CarritoDB).filter(
			CarritoDB.idusuario == idusuario,
			CarritoDB.estado == "ACTIVO"
		).first()

	def update_carrito(self, carrito: CarritoDB) -> CarritoDB:
		carrito.fecha_actualizacion = datetime.utcnow()
		self.db.commit()
		self.db.refresh(carrito)
		return carrito

	def delete_carrito(self, carrito: CarritoDB) -> None:
		self.db.delete(carrito)
		self.db.commit()

	def add_item(self, carrito: CarritoDB, item: dict) -> CarritoDB:
		items = carrito.items or []
		# Verificar si el libro ya está en el carrito
		existing_item = next((i for i in items if i["idlibro"] == item["idlibro"]), None)
		if existing_item:
			existing_item["cantidad"] += item["cantidad"]
			existing_item["subtotal_item"] = str(Decimal(existing_item["precio_unitario"]) * existing_item["cantidad"])
		else:
			items.append(item)
		# Forzar actualización del campo JSON
		carrito.items = None
		self.db.flush()
		carrito.items = items
		return self.update_carrito(carrito)

	def remove_item(self, carrito: CarritoDB, idlibro: int) -> CarritoDB:
		items = carrito.items or []
		new_items = [i for i in items if i["idlibro"] != idlibro]
		# Forzar actualización del campo JSON
		carrito.items = None
		self.db.flush()
		carrito.items = new_items
		return self.update_carrito(carrito)

	def recalcular_totales(self, carrito: CarritoDB) -> CarritoDB:
		items = carrito.items or []
		subtotal = sum(Decimal(item["subtotal_item"]) for item in items)
		descuentos = Decimal(carrito.descuentos)
		impuestos = subtotal * Decimal("0.19")  # IVA 19%
		total = subtotal - descuentos + impuestos
		
		carrito.subtotal = str(subtotal)
		carrito.impuestos = str(impuestos)
		carrito.total = str(total)
		return self.update_carrito(carrito)

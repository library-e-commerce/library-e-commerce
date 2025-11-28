from sqlalchemy.orm import Session
from app.database import InventarioDB
from datetime import datetime


class InventarioRepository:
	"""Repository handling DB operations for InventarioDB."""

	def __init__(self, db: Session):
		self.db = db

	def create_inventario(
		self,
		idlibro: int,
		umbral_minimo: int,
		stock_disponible: int,
		ubicacion_almacen: str | None = None,
		notas: str | None = None
	) -> InventarioDB:
		# Determinar estado según stock
		if stock_disponible == 0:
			estado = "AGOTADO"
		elif stock_disponible <= umbral_minimo:
			estado = "BAJO_STOCK"
		else:
			estado = "ACTIVO"

		inventario = InventarioDB(
			idlibro=idlibro,
			umbral_minimo=umbral_minimo,
			stock_disponible=stock_disponible,
			stock_reservado=0,
			fecha_ultima_actualizacion=datetime.utcnow(),
			estado=estado,
			ubicacion_almacen=ubicacion_almacen,
			notas=notas
		)
		self.db.add(inventario)
		self.db.commit()
		self.db.refresh(inventario)
		return inventario

	def get_inventario_by_id(self, inventario_id: int) -> InventarioDB | None:
		return self.db.query(InventarioDB).filter(InventarioDB.idinventario == inventario_id).first()

	def get_inventario_by_libro(self, idlibro: int) -> InventarioDB | None:
		return self.db.query(InventarioDB).filter(InventarioDB.idlibro == idlibro).first()

	def get_all_inventarios(self) -> list[InventarioDB]:
		return self.db.query(InventarioDB).all()

	def get_bajo_stock(self) -> list[InventarioDB]:
		return self.db.query(InventarioDB).filter(
			InventarioDB.estado.in_(["BAJO_STOCK", "AGOTADO"])
		).all()

	def update_inventario(self, inventario: InventarioDB) -> InventarioDB:
		# Actualizar estado según stock
		if inventario.stock_disponible == 0:
			inventario.estado = "AGOTADO"
		elif inventario.stock_disponible <= inventario.umbral_minimo:
			inventario.estado = "BAJO_STOCK"
		else:
			inventario.estado = "ACTIVO"

		inventario.fecha_ultima_actualizacion = datetime.utcnow()
		self.db.commit()
		self.db.refresh(inventario)
		return inventario

	def reabastecer(
		self,
		inventario: InventarioDB,
		cantidad: int,
		lote_reabastecimiento: str | None = None
	) -> InventarioDB:
		inventario.stock_disponible += cantidad
		inventario.fecha_ultimo_reabastecimiento = datetime.utcnow()
		if lote_reabastecimiento:
			inventario.lote_reabastecimiento = lote_reabastecimiento
		return self.update_inventario(inventario)

	def reservar_stock(self, inventario: InventarioDB, cantidad: int) -> InventarioDB:
		if inventario.stock_disponible >= cantidad:
			inventario.stock_disponible -= cantidad
			inventario.stock_reservado += cantidad
			return self.update_inventario(inventario)
		return inventario

	def liberar_stock(self, inventario: InventarioDB, cantidad: int) -> InventarioDB:
		inventario.stock_reservado -= cantidad
		inventario.stock_disponible += cantidad
		return self.update_inventario(inventario)

	def confirmar_venta(self, inventario: InventarioDB, cantidad: int) -> InventarioDB:
		# Si hay stock reservado, reducirlo primero
		if inventario.stock_reservado >= cantidad:
			inventario.stock_reservado -= cantidad
		else:
			# Si no hay suficiente reservado, reducir del disponible
			inventario.stock_disponible -= cantidad
		return self.update_inventario(inventario)

	def delete_inventario(self, inventario: InventarioDB) -> None:
		self.db.delete(inventario)
		self.db.commit()

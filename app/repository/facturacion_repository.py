from sqlalchemy.orm import Session
from app.database import FacturacionDB
from datetime import datetime
from decimal import Decimal


class FacturacionRepository:
	"""Repository handling DB operations for FacturacionDB."""

	def __init__(self, db: Session):
		self.db = db

	def create_factura(
		self,
		idpedido: int,
		idusuario: int,
		metodo_pago: str,
		items: list,
		datos_fiscales: str,
		moneda: str = "COP",
		notas: str | None = None
	) -> FacturacionDB:
		# Calcular totales
		subtotal = sum(Decimal(item["subtotal_item"]) for item in items)
		descuentos = Decimal("0")
		impuesto = subtotal * Decimal("0.19")
		total = subtotal - descuentos + impuesto

		# Añadir impuesto por item
		for item in items:
			item["impuesto_item"] = str(Decimal(item["subtotal_item"]) * Decimal("0.19"))

		factura = FacturacionDB(
			idpedido=idpedido,
			metodo_pago=metodo_pago,
			fecha=datetime.utcnow(),
			total=str(total),
			impuesto=str(impuesto),
			idusuario=idusuario,
			subtotal=str(subtotal),
			descuentos=str(descuentos),
			items=items,
			estado="EMITIDA",
			fecha_actualizacion=datetime.utcnow(),
			datos_fiscales=datos_fiscales,
			moneda=moneda,
			notas=notas
		)
		self.db.add(factura)
		self.db.commit()
		self.db.refresh(factura)
		return factura

	def get_factura_by_id(self, factura_id: int) -> FacturacionDB | None:
		return self.db.query(FacturacionDB).filter(FacturacionDB.idfactura == factura_id).first()

	def get_factura_by_pedido(self, idpedido: int) -> FacturacionDB | None:
		return self.db.query(FacturacionDB).filter(FacturacionDB.idpedido == idpedido).first()

	def get_facturas_by_user(self, idusuario: int) -> list[FacturacionDB]:
		return self.db.query(FacturacionDB).filter(FacturacionDB.idusuario == idusuario).all()

	def get_all_facturas(self) -> list[FacturacionDB]:
		return self.db.query(FacturacionDB).all()

	def update_factura(self, factura: FacturacionDB) -> FacturacionDB:
		factura.fecha_actualizacion = datetime.utcnow()
		self.db.commit()
		self.db.refresh(factura)
		return factura

	def delete_factura(self, factura: FacturacionDB) -> None:
		self.db.delete(factura)
		self.db.commit()

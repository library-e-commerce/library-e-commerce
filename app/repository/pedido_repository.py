from sqlalchemy.orm import Session
from app.database import PedidoDB
from datetime import datetime
from decimal import Decimal


class PedidoRepository:
	"""Repository handling DB operations for PedidoDB."""

	def __init__(self, db: Session):
		self.db = db

	def create_pedido(
		self,
		idusuario: int,
		items: list,
		direccion_envio: str,
		metodo_pago: str,
		idcarrito: int | None = None,
		notas: str | None = None
	) -> PedidoDB:
		# Convertir items a diccionarios si son objetos Pydantic
		items_dict = []
		for item in items:
			if hasattr(item, 'model_dump'):
				# Usar mode='json' para convertir Decimals a strings
				items_dict.append(item.model_dump(mode='json'))
			else:
				items_dict.append(item)
		
		# Calcular totales
		subtotal = sum(Decimal(item["subtotal_item"]) for item in items_dict)
		descuentos = Decimal("0")
		impuestos = subtotal * Decimal("0.19")
		total = subtotal - descuentos + impuestos

		pedido = PedidoDB(
			idusuario=idusuario,
			fecha=datetime.utcnow(),
			estado="PENDIENTE",
			items=items_dict,
			total=str(total),
			direccion_envio=direccion_envio,
			metodo_pago=metodo_pago,
			subtotal=str(subtotal),
			descuentos=str(descuentos),
			impuestos=str(impuestos),
			fecha_actualizacion=datetime.utcnow(),
			idcarrito=idcarrito,
			notas=notas
		)
		self.db.add(pedido)
		self.db.commit()
		self.db.refresh(pedido)
		return pedido

	def get_pedido_by_id(self, pedido_id: int) -> PedidoDB | None:
		return self.db.query(PedidoDB).filter(PedidoDB.idpedido == pedido_id).first()

	def get_pedidos_by_user(self, idusuario: int) -> list[PedidoDB]:
		return self.db.query(PedidoDB).filter(PedidoDB.idusuario == idusuario).all()

	def get_all_pedidos(self) -> list[PedidoDB]:
		return self.db.query(PedidoDB).all()

	def update_pedido(self, pedido: PedidoDB) -> PedidoDB:
		pedido.fecha_actualizacion = datetime.utcnow()
		self.db.commit()
		self.db.refresh(pedido)
		return pedido

	def delete_pedido(self, pedido: PedidoDB) -> None:
		self.db.delete(pedido)
		self.db.commit()

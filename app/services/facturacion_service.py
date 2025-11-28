from sqlalchemy.orm import Session
from app.repository.facturacion_repository import FacturacionRepository
from app.repository.pedido_repository import PedidoRepository
from app.repository.user_repository import UserRepository
from app.domain.facturacion_model import FacturacionCreate, FacturacionUpdate, FacturacionResponse
from fastapi import HTTPException


class FacturacionService:
	def __init__(self, db: Session):
		self.facturacion_repo = FacturacionRepository(db)
		self.pedido_repo = PedidoRepository(db)
		self.user_repo = UserRepository(db)

	def create_facturacion_from_pedido(self, pedido_id: int) -> FacturacionResponse:
		# Verificar que el pedido existe
		pedido = self.pedido_repo.get_pedido_by_id(pedido_id)
		if not pedido:
			raise HTTPException(status_code=404, detail="Pedido no encontrado")

		# Verificar si ya existe factura para este pedido
		existing = self.facturacion_repo.get_factura_by_pedido(pedido_id)
		if existing:
			return FacturacionResponse.model_validate(existing)

		# Crear factura con los items del pedido
		facturacion = self.facturacion_repo.create_factura(
			idusuario=pedido.idusuario,
			idpedido=pedido.idpedido,
			items=pedido.items,
			datos_fiscales="",
			metodo_pago=pedido.metodo_pago
		)

		return FacturacionResponse.model_validate(facturacion)

	def create_facturacion(self, facturacion_data: FacturacionCreate) -> FacturacionResponse:
		# Verificar que el usuario existe
		user = self.user_repo.get_user_by_id(facturacion_data.idusuario)
		if not user:
			raise HTTPException(status_code=404, detail="Usuario no encontrado")

		# Verificar que el pedido existe si se proporciona
		if facturacion_data.idpedido:
			pedido = self.pedido_repo.get_pedido_by_id(facturacion_data.idpedido)
			if not pedido:
				raise HTTPException(status_code=404, detail="Pedido no encontrado")

		facturacion = self.facturacion_repo.create_factura(
			idusuario=facturacion_data.idusuario,
			idpedido=facturacion_data.idpedido,
			items=facturacion_data.items,
			datos_fiscales=facturacion_data.datos_fiscales or "",
			metodo_pago=facturacion_data.metodo_pago
		)

		return FacturacionResponse.model_validate(facturacion)

	def get_facturacion(self, factura_id: int) -> FacturacionResponse:
		facturacion = self.facturacion_repo.get_factura_by_id(factura_id)
		if not facturacion:
			raise HTTPException(status_code=404, detail="Factura no encontrada")
		return FacturacionResponse.model_validate(facturacion)

	def get_facturaciones_by_user(self, idusuario: int) -> list[FacturacionResponse]:
		facturaciones = self.facturacion_repo.get_facturas_by_user(idusuario)
		return [FacturacionResponse.model_validate(f) for f in facturaciones]

	def get_facturacion_by_pedido(self, pedido_id: int) -> FacturacionResponse:
		facturacion = self.facturacion_repo.get_factura_by_pedido(pedido_id)
		if not facturacion:
			raise HTTPException(status_code=404, detail="Factura no encontrada")
		return FacturacionResponse.model_validate(facturacion)

	def update_facturacion(self, factura_id: int, facturacion_data: FacturacionUpdate) -> FacturacionResponse:
		facturacion = self.facturacion_repo.get_factura_by_id(factura_id)
		if not facturacion:
			raise HTTPException(status_code=404, detail="Factura no encontrada")

		if facturacion_data.estado is not None:
			facturacion.estado = facturacion_data.estado

		if facturacion_data.direccion_facturacion is not None:
			facturacion.direccion_facturacion = facturacion_data.direccion_facturacion

		if facturacion_data.notas is not None:
			facturacion.notas = facturacion_data.notas

		updated_facturacion = self.facturacion_repo.update_factura(facturacion)
		return FacturacionResponse.model_validate(updated_facturacion)

	def delete_facturacion(self, factura_id: int) -> None:
		facturacion = self.facturacion_repo.get_factura_by_id(factura_id)
		if not facturacion:
			raise HTTPException(status_code=404, detail="Factura no encontrada")
		self.facturacion_repo.delete_factura(facturacion)

from sqlalchemy.orm import Session
from app.repository.pedido_repository import PedidoRepository
from app.repository.carrito_repository import CarritoRepository
from app.repository.book_repository import BookRepository
from app.repository.user_repository import UserRepository
from app.repository.inventario_repository import InventarioRepository
from app.domain.pedido_model import PedidoCreate, PedidoUpdate, PedidoResponse
from app.domain.carrito_model import EstadoCarritoEnum
from app.domain.pedido_model import EstadoPedidoEnum
from fastapi import HTTPException
from decimal import Decimal


class PedidoService:
	def __init__(self, db: Session):
		self.pedido_repo = PedidoRepository(db)
		self.carrito_repo = CarritoRepository(db)
		self.book_repo = BookRepository(db)
		self.user_repo = UserRepository(db)
		self.inventario_repo = InventarioRepository(db)

	def create_pedido_from_carrito(self, carrito_id: int, metodo_pago: str, direccion_envio: str) -> PedidoResponse:
		# Obtener carrito
		carrito = self.carrito_repo.get_carrito_by_id(carrito_id)
		if not carrito:
			raise HTTPException(status_code=404, detail="Carrito no encontrado")

		if not carrito.items or len(carrito.items) == 0:
			raise HTTPException(status_code=400, detail="El carrito está vacío")

		if carrito.estado != EstadoCarritoEnum.ACTIVO.value:
			raise HTTPException(status_code=400, detail="El carrito no está activo")

		# Verificar stock para todos los items
		for item in carrito.items:
			book = self.book_repo.get_book_by_id(item["idlibro"])
			if not book:
				raise HTTPException(status_code=404, detail=f"Libro {item['idlibro']} no encontrado")
			if book.stock < item["cantidad"]:
				raise HTTPException(status_code=400, detail=f"Stock insuficiente para libro {item['idlibro']}")

		# Crear pedido con items del carrito
		pedido_data = PedidoCreate(
			idusuario=carrito.idusuario,
			items=carrito.items,
			metodo_pago=metodo_pago,
			direccion_envio=direccion_envio,
			notas=""
		)

		pedido = self.pedido_repo.create_pedido(
			idusuario=pedido_data.idusuario,
			items=pedido_data.items,
			metodo_pago=pedido_data.metodo_pago,
			direccion_envio=pedido_data.direccion_envio,
			notas=pedido_data.notas
		)

		# Actualizar stock y crear registros de inventario
		for item in pedido.items:
			book = self.book_repo.get_book_by_id(item["idlibro"])
			book.stock -= item["cantidad"]
			self.book_repo.update_book(book)

			# Confirmar venta en inventario
			inventario = self.inventario_repo.get_inventario_by_libro(item["idlibro"])
			if inventario:
				self.inventario_repo.confirmar_venta(inventario, item["cantidad"])

		# Actualizar estado del carrito
		carrito.estado = EstadoCarritoEnum.CONVERTIDO.value
		self.carrito_repo.update_carrito(carrito)

		return PedidoResponse.model_validate(pedido)

	def create_pedido(self, pedido_data: PedidoCreate) -> PedidoResponse:
		# Verificar que el usuario existe
		user = self.user_repo.get_user_by_id(pedido_data.idusuario)
		if not user:
			raise HTTPException(status_code=404, detail="Usuario no encontrado")

		# Verificar stock para todos los items
		for item in pedido_data.items:
			book = self.book_repo.get_book_by_id(item["idlibro"])
			if not book:
				raise HTTPException(status_code=404, detail=f"Libro {item['idlibro']} no encontrado")
			if book.stock < item["cantidad"]:
				raise HTTPException(status_code=400, detail=f"Stock insuficiente para libro {item['idlibro']}")

		pedido = self.pedido_repo.create_pedido(
			idusuario=pedido_data.idusuario,
			items=pedido_data.items,
			metodo_pago=pedido_data.metodo_pago,
			direccion_envio=pedido_data.direccion_envio,
			notas=pedido_data.notas
		)

		# Actualizar stock
		for item in pedido.items:
			book = self.book_repo.get_book_by_id(item["idlibro"])
			book.stock -= item["cantidad"]
			self.book_repo.update_book(book)

			# Confirmar venta en inventario
			inventario = self.inventario_repo.get_inventario_by_libro(item["idlibro"])
			if inventario:
				self.inventario_repo.confirmar_venta(inventario, item["cantidad"])

		return PedidoResponse.model_validate(pedido)

	def get_pedido(self, pedido_id: int) -> PedidoResponse:
		pedido = self.pedido_repo.get_pedido_by_id(pedido_id)
		if not pedido:
			raise HTTPException(status_code=404, detail="Pedido no encontrado")
		return PedidoResponse.model_validate(pedido)

	def get_pedidos_by_user(self, idusuario: int) -> list[PedidoResponse]:
		pedidos = self.pedido_repo.get_pedidos_by_user(idusuario)
		return [PedidoResponse.model_validate(p) for p in pedidos]

	def update_pedido(self, pedido_id: int, pedido_data: PedidoUpdate) -> PedidoResponse:
		pedido = self.pedido_repo.get_pedido_by_id(pedido_id)
		if not pedido:
			raise HTTPException(status_code=404, detail="Pedido no encontrado")

		# Validar transiciones de estado válidas
		if pedido_data.estado is not None:
			current_state = pedido.estado
			new_state = pedido_data.estado

			# No permitir cancelar pedidos ya enviados o entregados
			if new_state == EstadoPedidoEnum.CANCELADO.value:
				if current_state in [EstadoPedidoEnum.ENVIADO.value, EstadoPedidoEnum.ENTREGADO.value]:
					raise HTTPException(status_code=400, detail="No se puede cancelar un pedido enviado o entregado")

			pedido.estado = new_state

		if pedido_data.metodo_pago is not None:
			pedido.metodo_pago = pedido_data.metodo_pago

		if pedido_data.direccion_envio is not None:
			pedido.direccion_envio = pedido_data.direccion_envio

		if pedido_data.notas is not None:
			pedido.notas = pedido_data.notas

		if pedido_data.numero_seguimiento is not None:
			pedido.numero_seguimiento = pedido_data.numero_seguimiento

		updated_pedido = self.pedido_repo.update_pedido(pedido)
		return PedidoResponse.model_validate(updated_pedido)

	def delete_pedido(self, pedido_id: int) -> None:
		pedido = self.pedido_repo.get_pedido_by_id(pedido_id)
		if not pedido:
			raise HTTPException(status_code=404, detail="Pedido no encontrado")

		# No permitir eliminar pedidos enviados o entregados
		if pedido.estado in [EstadoPedidoEnum.ENVIADO.value, EstadoPedidoEnum.ENTREGADO.value]:
			raise HTTPException(status_code=400, detail="No se puede eliminar un pedido enviado o entregado")

		self.pedido_repo.delete_pedido(pedido)

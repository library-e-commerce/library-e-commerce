from app.api import auth_api, user_api, book_api, carrito_api, pedido_api, facturacion_api, inventario_api


ROUTERS = [
	auth_api.router,
	user_api.router,
	book_api.router,
	carrito_api.router,
	pedido_api.router,
	facturacion_api.router,
	inventario_api.router,
]


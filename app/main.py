from fastapi import FastAPI
from app.config.routers import ROUTERS


app = FastAPI(
	title="Library API",
	description="API de gestión de biblioteca con arquitectura en capas",
	version="1.0.0",
)


for router in ROUTERS:
	app.include_router(router)


@app.get("/")
def root():
	return {"message": "API funcionando correctamente"}
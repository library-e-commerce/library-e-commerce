from fastapi import FastAPI

app = FastAPI(
    title="Librería API",
    description="Sistema de gestión de librería e-commerce",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Bienvenido a Librería API"}

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Text, JSON
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime

DATABASE_URL = "sqlite:///./library.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserDB(Base):
    """SQLAlchemy model for the users table."""
    __tablename__ = "users"

    idusuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False, index=True)
    contraseña = Column(String, nullable=False)
    rol = Column(String, nullable=False, default="CLIENTE")
    fecha_nacimiento = Column(Date, nullable=False)
    direccion = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    activo = Column(Boolean, default=False, nullable=False)
    preferencias = Column(JSON, nullable=True)
    acepta_terminos = Column(Boolean, nullable=False)
    token_verificacion = Column(String, nullable=True)
    email_verificado = Column(Boolean, default=False, nullable=False)

    carritos = relationship("CarritoDB", back_populates="user")
    pedidos = relationship("PedidoDB", back_populates="user")
    facturas = relationship("FacturacionDB", back_populates="user")


class BookDB(Base):
    """SQLAlchemy model for the books table."""
    __tablename__ = "books"

    idlibro = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    autor = Column(JSON, nullable=False)
    categoria = Column(JSON, nullable=False)
    precio = Column(String, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    editorial = Column(String(100), nullable=True)
    año_publicacion = Column(Integer, nullable=False)
    idioma = Column(String, nullable=False)
    formato = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    imagen_portada = Column(String, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    descuento = Column(String, nullable=False, default="0")

    inventarios = relationship("InventarioDB", back_populates="book")


class CarritoDB(Base):
    """SQLAlchemy model for the shopping carts table."""
    __tablename__ = "carritos"

    idcarrito = Column(Integer, primary_key=True, index=True)
    idusuario = Column(Integer, ForeignKey("users.idusuario"), nullable=False)
    items = Column(JSON, nullable=False, default=list)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    subtotal = Column(String, nullable=False, default="0")
    descuentos = Column(String, nullable=False, default="0")
    impuestos = Column(String, nullable=False, default="0")
    total = Column(String, nullable=False, default="0")
    estado = Column(String, nullable=False, default="ACTIVO")
    sesion_id = Column(String, nullable=True)
    ultimo_usuario_modifico = Column(Integer, nullable=True)

    user = relationship("UserDB", back_populates="carritos")


class PedidoDB(Base):
    """SQLAlchemy model for the orders table."""
    __tablename__ = "pedidos"

    idpedido = Column(Integer, primary_key=True, index=True)
    idusuario = Column(Integer, ForeignKey("users.idusuario"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    estado = Column(String, nullable=False, default="PENDIENTE")
    items = Column(JSON, nullable=False)
    total = Column(String, nullable=False)
    direccion_envio = Column(String, nullable=False)
    metodo_pago = Column(String, nullable=False)
    subtotal = Column(String, nullable=False, default="0")
    descuentos = Column(String, nullable=False, default="0")
    impuestos = Column(String, nullable=False, default="0")
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_usuario_modifico = Column(Integer, nullable=True)
    idcarrito = Column(Integer, nullable=True)
    numero_factura = Column(String, nullable=True)
    notas = Column(String(500), nullable=True)

    user = relationship("UserDB", back_populates="pedidos")


class FacturacionDB(Base):
    """SQLAlchemy model for the invoices table."""
    __tablename__ = "facturacion"

    idfactura = Column(Integer, primary_key=True, index=True)
    idpedido = Column(Integer, ForeignKey("pedidos.idpedido"), nullable=False)
    metodo_pago = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    total = Column(String, nullable=False)
    impuesto = Column(String, nullable=False, default="0")
    idusuario = Column(Integer, ForeignKey("users.idusuario"), nullable=False)
    subtotal = Column(String, nullable=False, default="0")
    descuentos = Column(String, nullable=False, default="0")
    items = Column(JSON, nullable=False)
    estado = Column(String, nullable=False, default="EMITIDA")
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_usuario_modifico = Column(Integer, nullable=True)
    datos_fiscales = Column(String, nullable=False)
    moneda = Column(String, nullable=False, default="COP")
    notas = Column(String(500), nullable=True)

    user = relationship("UserDB", back_populates="facturas")


class InventarioDB(Base):
    """SQLAlchemy model for the inventory table."""
    __tablename__ = "inventario"

    idinventario = Column(Integer, primary_key=True, index=True)
    idlibro = Column(Integer, ForeignKey("books.idlibro"), nullable=False, unique=True)
    umbral_minimo = Column(Integer, nullable=False, default=5)
    stock_disponible = Column(Integer, nullable=False, default=0)
    stock_reservado = Column(Integer, nullable=False, default=0)
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_usuario_modifico = Column(Integer, nullable=True)
    estado = Column(String, nullable=False, default="ACTIVO")
    fecha_ultimo_reabastecimiento = Column(DateTime, nullable=True)
    notas = Column(String(500), nullable=True)
    ubicacion_almacen = Column(String, nullable=True)
    lote_reabastecimiento = Column(String, nullable=True)

    book = relationship("BookDB", back_populates="inventarios")


Base.metadata.create_all(bind=engine)

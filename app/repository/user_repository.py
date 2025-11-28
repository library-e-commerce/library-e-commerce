from sqlalchemy.orm import Session
from app.database import UserDB
from datetime import date, datetime
import bcrypt
import uuid


class UserRepository:
	"""Repository handling DB operations for UserDB."""

	def __init__(self, db: Session):
		self.db = db

	def create_user(
		self,
		nombre: str,
		apellido: str,
		correo: str,
		contraseña: str,
		rol: str,
		fecha_nacimiento: date,
		direccion: str,
		telefono: str,
		preferencias: list[str] | None,
		acepta_terminos: bool
	) -> UserDB:
		# Hash de contraseña con bcrypt (límite de 72 bytes)
		password_bytes = contraseña.encode('utf-8')[:72]
		hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
		
		# Generar token de verificación
		token_verificacion = str(uuid.uuid4())
		
		user = UserDB(
			nombre=nombre,
			apellido=apellido,
			correo=correo,
			contraseña=hashed_password,
			rol=rol,
			fecha_nacimiento=fecha_nacimiento,
			direccion=direccion,
			telefono=telefono,
			preferencias=preferencias or [],
			acepta_terminos=acepta_terminos,
			fecha_creacion=datetime.utcnow(),
			activo=False,  # Inactivo hasta verificar email
			email_verificado=False,
			token_verificacion=token_verificacion
		)
		self.db.add(user)
		self.db.commit()
		self.db.refresh(user)
		return user

	def get_user_by_id(self, user_id: int) -> UserDB | None:
		return self.db.query(UserDB).filter(UserDB.idusuario == user_id).first()

	def get_user_by_email(self, correo: str) -> UserDB | None:
		return self.db.query(UserDB).filter(UserDB.correo == correo).first()

	def get_all_users(self) -> list[UserDB]:
		return self.db.query(UserDB).all()

	def update_user(self, user: UserDB) -> UserDB:
		self.db.commit()
		self.db.refresh(user)
		return user

	def delete_user(self, user: UserDB) -> None:
		self.db.delete(user)
		self.db.commit()

	def verify_password(self, plain_password: str, hashed_password: str) -> bool:
		password_bytes = plain_password.encode('utf-8')[:72]
		return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))

	def get_user_by_token(self, token: str) -> UserDB | None:
		return self.db.query(UserDB).filter(UserDB.token_verificacion == token).first()

	def verify_email(self, user: UserDB) -> UserDB:
		user.email_verificado = True
		user.activo = True
		user.token_verificacion = None
		self.db.commit()
		self.db.refresh(user)
		return user

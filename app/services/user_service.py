from sqlalchemy.orm import Session
from app.repository.user_repository import UserRepository
from app.domain.user_model import UserCreate, UserUpdate, UserResponse
from fastapi import HTTPException
from datetime import date


class UserService:
	def __init__(self, db: Session):
		self.repository = UserRepository(db)

	def create_user(self, user_data: UserCreate) -> UserResponse:
		existing_user = self.repository.get_user_by_email(user_data.correo)
		if existing_user:
			raise HTTPException(status_code=400, detail="El correo ya existe")

		# Validar edad mínima (18 años)
		today = date.today()
		age = today.year - user_data.fecha_nacimiento.year - (
			(today.month, today.day) < (user_data.fecha_nacimiento.month, user_data.fecha_nacimiento.day)
		)
		if age < 18:
			raise HTTPException(status_code=400, detail="Debe ser mayor de 18 años")

		if not user_data.acepta_terminos:
			raise HTTPException(status_code=400, detail="Debe aceptar los términos y condiciones")

		user = self.repository.create_user(
			nombre=user_data.nombre,
			apellido=user_data.apellido,
			correo=user_data.correo,
			contraseña=user_data.contraseña,
			rol=user_data.rol,
			fecha_nacimiento=user_data.fecha_nacimiento,
			direccion=user_data.direccion,
			telefono=user_data.telefono,
			preferencias=user_data.preferencias,
			acepta_terminos=user_data.acepta_terminos
		)

		return UserResponse.model_validate(user)

	def get_user(self, user_id: int) -> UserResponse:
		user = self.repository.get_user_by_id(user_id)
		if not user:
			raise HTTPException(status_code=404, detail="Usuario no encontrado")
		return UserResponse.model_validate(user)

	def get_all_users(self) -> list[UserResponse]:
		users = self.repository.get_all_users()
		return [UserResponse.model_validate(user) for user in users]

	def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
		user = self.repository.get_user_by_id(user_id)
		if not user:
			raise HTTPException(status_code=404, detail="Usuario no encontrado")

		# Verificar email único si se está cambiando
		if user_data.correo and user_data.correo != user.correo:
			existing = self.repository.get_user_by_email(user_data.correo)
			if existing:
				raise HTTPException(status_code=400, detail="Email ya registrado")
			user.correo = user_data.correo

		# Actualizar campos proporcionados
		if user_data.nombre is not None:
			user.nombre = user_data.nombre
		if user_data.apellido is not None:
			user.apellido = user_data.apellido
		if user_data.contraseña is not None:
			import bcrypt
			password_bytes = user_data.contraseña.encode('utf-8')[:72]
			user.contraseña = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
		if user_data.rol is not None:
			user.rol = user_data.rol
		if user_data.fecha_nacimiento is not None:
			user.fecha_nacimiento = user_data.fecha_nacimiento
		if user_data.direccion is not None:
			user.direccion = user_data.direccion
		if user_data.telefono is not None:
			user.telefono = user_data.telefono
		if user_data.preferencias is not None:
			user.preferencias = user_data.preferencias
		if user_data.activo is not None:
			user.activo = user_data.activo

		updated_user = self.repository.update_user(user)
		return UserResponse.model_validate(updated_user)

	def delete_user(self, user_id: int) -> None:
		user = self.repository.get_user_by_id(user_id)
		if not user:
			raise HTTPException(status_code=404, detail="Usuario no encontrado")
		self.repository.delete_user(user)
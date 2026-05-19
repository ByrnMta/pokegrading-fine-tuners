from passlib.context import CryptContext
from Modelos.Usuario import Usuario
from sqlalchemy.orm import Session


class UsuarioServicio:

    # Hashing de contraseña
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    #============================= Lógica endpoints =============================

    # Registro de usuario
    @staticmethod
    def registrar_usuario_servicio(db: Session, nombre_usuario: str, correo: str, contrasena: str):

        errores = {}
        try:
            # Validar que el correo sea único
            UsuarioServicio.validar_correo_unico(db, correo, errores)

            #validación de unicidad de nombre de usuario
            UsuarioServicio.validar_nombre_usuario_unico(db, nombre_usuario, errores)
            
            # si hay errores de validación, se retornan
            if errores:
                return {"errores": errores}
            
            # Se encripta la contraseña antes de guardarla
            contrasena_hashed = UsuarioServicio.pwd_context.hash(contrasena)
            rol_id = 2  # Asignar rol de submitter por defecto

            # Se crea un nuevo usuario
            nuevo_usuario = Usuario(
                rol_id=rol_id,
                nombre_usuario=nombre_usuario,
                correo=correo,
                contrasena=contrasena_hashed
            )
            db.add(nuevo_usuario)
            db.commit()
            db.refresh(nuevo_usuario)

            return {"mensaje": "Usuario registrado exitosamente"}
            
        except Exception as e:
            db.rollback()
            return {"errores": {"internal": f"Error interno: {str(e)}"}}
        finally:
            db.close()

    #============================= Validaciones =============================

    # validar unicidad de correo
    @staticmethod
    def validar_correo_unico(db: Session, correo: str, errores: dict):
        # se valida que el correo no esté vacío
        if not correo:
            errores['correo'] = "El correo es obligatorio."
            return None

        # Validar que el correo no esté registrado
        if  db.query(Usuario).filter(Usuario.correo == correo).first():
            errores['correo'] = "El correo ya está registrado."
            return None
    
    # validar unicidad de nombre de usuario
    @staticmethod
    def validar_nombre_usuario_unico(db: Session, nombre_usuario: str, errores: dict):
        # se valida que el nombre de usuario no esté vacío
        if not nombre_usuario:
            errores['nombre_usuario'] = "El nombre de usuario es obligatorio."
            return None

        # Validar que el nombre de usuario no esté registrado
        if db.query(Usuario).filter(Usuario.nombre_usuario == nombre_usuario).first():
            errores['nombre_usuario'] = "El nombre de usuario ya está registrado, por favor intente con otro."
            return None


    
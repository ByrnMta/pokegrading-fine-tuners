from passlib.context import CryptContext
from Modelos.Usuario import Usuario
from sqlalchemy.orm import Session
from Esquemas.UsuarioEsquema import UsuarioCreate
from AccesoDatos.UsuarioRepositorio import UsuarioRepositorio
from Servicios.validaciones.UsuarioValidacion import UsuarioValidacion

class UsuarioServicio:

    # Hashing de contraseña
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    #============================= Lógica endpoints =============================

    # Registro de usuario
    @staticmethod
    def registrar_usuario_servicio(db: Session, nuevo_usuario: UsuarioCreate):
        """Servicio de registro de usuario nuevo, que valida los datos recibidos."""

        errores = {}
        try:
            # Validar que el correo sea único
            UsuarioValidacion.unicidad_correo(db, nuevo_usuario.correo, errores)

            # Validar formato del correo
            UsuarioValidacion.formato_correo_valido(db, nuevo_usuario.correo, errores)

            # Validar dominio del correo
            UsuarioValidacion.validar_dominio_bloqueado(db, nuevo_usuario.correo, errores)
            
            # Validar formato de la contraseña
            UsuarioValidacion.validar_contrasena(db, nuevo_usuario.contrasena, errores)
            
            # Validar país de mercado
            UsuarioValidacion.validar_pais_mercado(db, nuevo_usuario.pais, errores)
            
            # Validar idioma
            UsuarioValidacion.validar_idioma(db, nuevo_usuario.idioma, errores)

            # si hay errores de validación, se retornan
            if errores:
                return {"errores": errores}
            
            # Se registra el nuevo usuario
            UsuarioRepositorio.registrar_usuario(db, nuevo_usuario)

            return {"mensaje": "Usuario registrado exitosamente"}
            
        except Exception as e:
            db.rollback()
            return {"errores": {"internal": f"Error interno: {str(e)}"}}
        finally:
            db.close()
    
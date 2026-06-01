from passlib.context import CryptContext
from sqlalchemy.orm import Session
from Modelos.Usuario import Usuario
from Esquemas.UsuarioEsquema import UsuarioBase
from Esquemas.UsuarioEsquema import UsuarioCreate
from AccesoDatos.PaisRepositorio import PaisRepositorio
from AccesoDatos.IdiomaRepositorio import IdiomaRepositorio

class UsuarioRepositorio:

    @staticmethod
    def obtener_usuario_por_correo(db: Session, correo: str) -> UsuarioBase | None:
        """Busca un usuario por su correo electrónico. Retorna un objeto UsuarioBase si se encuentra, o None si no se encuentra."""

        usuario_encontrado = db.query(Usuario).filter(Usuario.correo == correo).first()
        if usuario_encontrado:
            # Se regresa un objeto UsuarioBase si se encontró un usuario con el correo dado
            return UsuarioRepositorio.orm_a_usuario(usuario_encontrado)
        return None

    @staticmethod
    def registrar_usuario(db: Session, nuevo_usuario: UsuarioCreate) -> UsuarioBase:
        """Registra un nuevo usuario en la base de datos. Retorna el usuario registrado como un objeto UsuarioBase."""
        
        rol_id = 2  # Asignar rol de submitter por defecto

        # Se encripta la contraseña
        contrasena_hashed = UsuarioRepositorio.encriptar_contrasena(nuevo_usuario.contrasena)

        # Se obtiene el id del país a partir del nombre del país
        pais = PaisRepositorio.buscar_pais_por_nombre(db, nuevo_usuario.pais)
        pais_id = pais.id

        # Se obtiene el id del idioma a partir del nombre del idioma
        idioma = IdiomaRepositorio.buscar_idioma_por_nombre(db, nuevo_usuario.idioma)
        idioma_id = idioma.id

        nuevo_usuario = Usuario(
            rol_id=rol_id,
            pais_id=pais_id,  # Se asignará el país_id después de validar el país
            idioma_id=idioma_id,  # Se asignará el idioma_id después de validar el idioma
            nombre_usuario=nuevo_usuario.nombre_usuario,
            correo=nuevo_usuario.correo,
            contrasena=contrasena_hashed,
            ultimo_acceso=None
        )
        db.add(nuevo_usuario)
        db.commit()
        return UsuarioRepositorio.orm_a_usuario(nuevo_usuario)

    @staticmethod
    def encriptar_contrasena(contrasena: str) -> str:
        """Encripta la contraseña utilizando bcrypt y retorna la contraseña encriptada."""

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(contrasena)

    @staticmethod 
    def orm_a_usuario(usuario: Usuario)->UsuarioBase:
        """Convierte un objeto ORM Usuario (usado por la DB) a un esquema UsuarioBase(modelo interno en el backend)."""
        
        return UsuarioBase(
            id=usuario.id,
            rol_id=usuario.rol_id,
            pais_id=usuario.pais_id,
            idioma_id=usuario.idioma_id,
            nombre_usuario=usuario.nombre_usuario,
            correo=usuario.correo,
            contrasena=usuario.contrasena,
            ultimo_acceso=usuario.ultimo_acceso
        )
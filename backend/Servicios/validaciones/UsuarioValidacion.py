from sqlalchemy.orm import Session
from AccesoDatos.UsuarioRepositorio import UsuarioRepositorio
from AccesoDatos.CorreoBloqueadoRepositorio import CorreosBloqueadosRepositorio
from AccesoDatos.PaisRepositorio import PaisRepositorio
from AccesoDatos.IdiomaRepositorio import IdiomaRepositorio

class UsuarioValidacion:

    @staticmethod
    def unicidad_correo(db: Session, correo: str, errores: dict):
        """Valida que el correo sea único, que no haya duplicidad"""

        # se valida que el correo no esté vacío
        if not correo:
            errores['correo'] = "El correo es obligatorio."
            return None

        # Se valida que el correo no esté ya registrado en la base de datos
        if UsuarioRepositorio.obtener_usuario_por_correo(db, correo):
            errores['correo existente'] = "El correo ya está registrado."
            return None
    
    @staticmethod
    def formato_correo_valido(db: Session, correo: str, errores: dict):
        """Valida que el formato del correo sea válido"""

        if not correo:
            errores['correo'] = "El correo es obligatorio."
            return None
        
        # Se comprueba si el formato del correo es válido (al menos una @)
        if correo.count("@") != 1:
            errores['correo formato'] = "El formato del correo no es válido."
            return None
                
    @staticmethod
    def validar_dominio_bloqueado(db: Session, correo: str, errores: dict):
        """Valida que el dominio del correo no esté bloqueado"""
        
        if not correo:
            errores['correo'] = "El correo es obligatorio."
            return None

        # Se valida primero si el formato del correo es válido para poder extraer el dominio
        if "@" not in correo:
            errores['correo formato'] = "El formato del correo no es válido."
            return None
        
        # Se extrae el dominio del correo para validar si es permitido
        _, dominio = correo.split("@")
        
        if not dominio:
            errores['correo formato'] = "El formato del correo no es válido."
            return None
        
        if CorreosBloqueadosRepositorio.buscar_dominio_bloqueado(db, dominio):
            errores['correo dominio'] = "El dominio del correo no es válido."
            return None
    
    @staticmethod
    def validar_contrasena(db: Session, contrasena: str, errores: dict):
        """Valida que la contraseña cumpla con el formato requerido (mínimo 8 caracteres),
        al menos una letra mayúscula, una letra minúscula y digito"""

        if not contrasena:
            errores['contraseña'] = "La contraseña es obligatoria."
            return None
        
        if len(contrasena) < 8:
            errores['contraseña longitud'] = "La contraseña debe tener al menos 8 caracteres."
            return None
        
        if not any(c.isupper() for c in contrasena):
            errores['contraseña mayúscula'] = "La contraseña debe contener al menos una letra mayúscula."
            return None
        
        if not any(c.islower() for c in contrasena):
            errores['contraseña minúscula'] = "La contraseña debe contener al menos una letra minúscula."
            return None
        
        if not any(c.isdigit() for c in contrasena):
            errores['contraseña dígito'] = "La contraseña debe contener al menos un dígito."
            return None
    
    @staticmethod
    def validar_pais_mercado(db: Session, pais: str, errores: dict):
        """Valida que el país seleccionado sea un país válido en la base de datos"""

        if not pais:
            errores['pais'] = "El país es obligatorio."
            return None
        
        if not PaisRepositorio.buscar_pais_por_nombre(db, pais):
            errores['pais inválido'] = "El país seleccionado no es válido."
            return None
        
    @staticmethod
    def validar_idioma(db: Session, idioma: str, errores: dict):
        """Valida si el idioma seleccionado sea un idioma válido en la base de datos"""

        if not idioma:
            errores['idioma'] = "El idioma es obligatorio."
            return None

        if not IdiomaRepositorio.buscar_idioma_por_nombre(db, idioma):
            errores['idioma inválido'] = "El idioma seleccionado no es válido."
            return None
        
        # Aquí se podría agregar una validación similar a la de país si se tuviera una tabla de idiomas en la base de datos
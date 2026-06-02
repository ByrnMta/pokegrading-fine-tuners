
# Backend FastAPI - Instrucciones de Entorno y Migraciones

## Configuración del entorno virtual

**Nota:** Si ya se da el archivo requirements.txt, omitir pasos 3,4. Ejecutar solo 1,2 y 5.

1. **Crear entorno virtual:**
	```
	python -m venv .venv
	```
2. **Activar entorno virtual:**
	(Haz esto cada vez que abras el proyecto)
	```
	.\.venv\Scripts\Activate
	```
3. **Instalar paquetes (esto solo es si se necesita instalar alguna dependencia más):**
	(Con el entorno activado)
	```
	pip install nombre_paquete
	```
4. **Generar/actualizar requirements.txt:**
	(Después de instalar o actualizar paquetes)
	```
	pip freeze > requirements.txt
	```
5. **Instalar dependencias desde requirements.txt:**
	(Para nuevos miembros o al clonar el proyecto)
	```
	pip install -r requirements.txt
	```

### Instalación de paquetes iniciales

Con el entorno activado, instala los paquetes principales (estos es al iniciar el proyecto de cero, no se hace más):
```bash
pip install fastapi
pip install uvicorn
pip install sqlalchemy
```

### Dependencias para embeddings e imagenes

La busqueda por imagen usa dependencias adicionales. Si instalas manualmente el entorno, asegúrate de incluir:
```bash
pip install numpy Pillow torch transformers
```

Si usas PyTorch en CPU sobre Windows, puedes instalarlo con:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Si quieres evitar el warning del Hub de Hugging Face, define `HF_TOKEN` antes de arrancar el servidor.

### Iniciar el servidor del backend

```
uvicorn main:app --reload
```

---

## Migraciones de Base de Datos (Alembic)

1. **Inicializar Alembic (solo la primera vez):**
	```
	alembic init migraciones
	```
2. **Crear una nueva migración (detecta cambios en los modelos, nuevas tablas, columnas nuevas) y genera una nueva migración en la carpeta migraciones/versions lista para ser aplicada a la base de datos:**
	```
	alembic revision --autogenerate -m "Descripción de la migración"
	```
3. **Aplicar la migración a la base de datos (después de esto debería ver los cambios en la base de datos):**
	```
	alembic upgrade head
	```
**Nota:** si da problemas haciendo la migración, elimine la carpeta de versions, ejecute el comando 2 de esta sección y luego el 3.

---

**Notas:**
- Asegúrate de tener el entorno virtual activado antes de ejecutar cualquier comando.
- Edita la ruta de la base de datos en los archivos de configuración según tu entorno. En en alembic.ini (la variable "sqlalchemy.url") y en la carpeta Base_de_Datos en db.py (la variable DATABASE_URL).
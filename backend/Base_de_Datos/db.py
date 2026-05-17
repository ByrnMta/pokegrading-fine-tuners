from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de la base de datos SQLite (se coloca la obsoluta dado que la relativa no sirve, editar la ruta de acuerdo al path suyo)
DATABASE_URL = r"sqlite:///D:\TEC_I-2026\Diseno_calidad_productos\Asignaciones\Proyecto\pokegrading-fine-tuners\backend\Base_de_Datos\pokegrading.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base para los modelos
Base = declarative_base()

# database.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# ---------------------------------------------------
# Configuración de conexión
# ---------------------------------------------------
db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(
    db_connection_string,
    pool_pre_ping=True,
    pool_recycle=280,
    pool_size=1,
    max_overflow=0,
    connect_args={
        "connect_timeout": 10,
        "ssl": { "ssl_ca": "/etc/ssl/certs/ca-certificates.crt" }
    }
)

SessionLocal = sessionmaker(bind=engine)

def get_db_session():
    return SessionLocal()

# ---------------------------------------------------
# Funciones de base de datos
# ---------------------------------------------------

def is_preregistered(numero_control: str) -> bool:
    """Verifica si el número de control está preregistrado"""
    session = get_db_session()
    try:
        result = session.execute(
            text("""
                SELECT 1 FROM alumnos_preregistrados
                WHERE UPPER(TRIM(numero_control)) = :nc
                LIMIT 1
            """),
            {"nc": numero_control.strip().upper()}
        ).first()
        return result is not None
    finally:
        session.close()

def get_user_by_username(username: str):
    """Obtiene los datos de un usuario por su username"""
    session = get_db_session()
    try:
        result = session.execute(
            text("SELECT * FROM users2 WHERE username = :username"),
            {"username": username}
        ).mappings().first()
        return dict(result) if result else None
    finally:
        session.close()

def register_user(session, numero_control, plantel, apellido_paterno,
                  apellido_materno, nombres, username, password_raw) -> bool:
    """Registra un nuevo usuario en users2"""
    try:
        password_hash = bcrypt.generate_password_hash(password_raw).decode('utf-8')
        session.execute(
            text("""
                INSERT INTO users2 (
                    numero_control, plantel, apellido_paterno, apellido_materno,
                    nombres, username, password, created_at
                )
                VALUES (
                    :numero_control, :plantel, :apellido_paterno, :apellido_materno,
                    :nombres, :username, :password, :created_at
                )
            """),
            {
                "numero_control": numero_control,
                "plantel": plantel,
                "apellido_paterno": apellido_paterno,
                "apellido_materno": apellido_materno,
                "nombres": nombres,
                "username": username,
                "password": password_hash,
                "created_at": datetime.now(pytz.timez_

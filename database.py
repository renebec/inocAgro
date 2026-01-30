import os
from datetime import datetime
import pytz
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from flask import request, render_template

# ---------------------------
# Database connection
# ---------------------------
db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(
    db_connection_string,
    connect_args={
        "ssl": {"ssl_ca": "/etc/ssl/certs/ca-certificates.crt"}
    }
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db_session():
    """Create a new SQLAlchemy session"""
    return SessionLocal()

# ---------------------------
# Login: Get user by username
# ---------------------------
def get_user_from_database(username):
    try:
        session = get_db_session()
        result = session.execute(
            text("SELECT * FROM users2 WHERE username = :username"),
            {"username": username}
        )
        row = result.mappings().first()
        return dict(row) if row else None
    except SQLAlchemyError as e:
        print(f"DB ERROR (login): {e}")
        return None
    finally:
        session.close()

# ---------------------------
# Registration
# ---------------------------
def register_user(
    numero_control, plantel, apellido_paterno, apellido_materno,
    nombres, username, password
):
    session = get_db_session()
    created_at = datetime.now(pytz.timezone("America/Mexico_City"))

    # Check if username already exists
    existing_user = get_user_from_database(username)
    if existing_user:
        print("⚠️ Username already exists")
        session.close()
        return False

    # TODO: Hash password before storing
    try:
        sql = text("""
            INSERT INTO users2 (
                numero_control, plantel, apellido_paterno,
                apellido_materno, nombres, username, password, created_at
            ) VALUES (
                :numero_control, :plantel, :apellido_paterno,
                :apellido_materno, :nombres, :username, :password, :created_at
            )
        """)
        session.execute(sql, {
            "numero_control": numero_control,
            "plantel": plantel,
            "apellido_paterno": apellido_paterno,
            "apellido_materno": apellido_materno,
            "nombres": nombres,
            "username": username,
            "password": password,  # store hashed password in production!
            "created_at": created_at
        })
        session.commit()
        print("✅ User registered successfully")
        return True
    except SQLAlchemyError as e:
        print(f"DB ERROR (registration): {e}")
        session.rollback()
        return False
    finally:
        session.close()

# ---------------------------
# Optional: Handle Flask form for choice (register type)
# ---------------------------
def handle_choice():
    choice = None
    if request.method == 'POST':
        choice = request.form.get('choice')
    return render_template('register.html', choice=choice)

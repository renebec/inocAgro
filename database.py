import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz
import pymysql



db_connection_string = os.environ['DB_CONNECTION_STRING']
engine = create_engine(db_connection_string,
                       pool_pre_ping=True,
                       pool_recycle=280,
                       pool_size=1,
                       max_overflow=0,
      connect_args={
            "connect_timeout": 10,
            "ssl": { 
              "ssl_ca": "/etc/ssl/certs/ca-certificates.crt"
                   }
                  }
            )

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SessionLocal = sessionmaker(bind=engine)

def get_db_session():
    return SessionLocal()

"""
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
"""

def handle_choice():
    choice = None
    if request.method == 'POST':
        choice = request.form.get('choice')  # 'value1' or 'value2' or None
    return render_template('register.html', choice=choice)


""" ESTO ES UN COMENTARIO
def is_preregistered(numero_control):
    session = get_db_session()
    try:
        print("🔎 Buscando NC:", repr(numero_control))

        rows = session.execute(
            text("SELECT numero_control FROM alumnos_preregistrados")
        ).fetchall()

        print("📋 NCs en DB:", [repr(r[0]) for r in rows])

        return any(r[0].strip().upper() == numero_control for r in rows)

    finally:
        session.close()
"""

def is_preregistered(numero_control):
    session = get_db_session()
    try:
        return session.execute(
            text("""
                SELECT 1
                FROM alumnos_preregistrados
                WHERE UPPER(TRIM(numero_control)) = :nc
                LIMIT 1
            """),
            {"nc": numero_control.strip().upper()}
        ).first() is not None
    finally:
        session.close()




def load_pg_from_db():
    try:
      with engine.connect() as conn:
          result = conn.execute(text("SELECT * FROM users2"))
          pg = result.mappings().all()
          return pg
    except Exception as e:
      print(f"DB ERROR: {e}")
      return None

      #result_all = result.all()
      #tipo = type(result_all)
      #tipo_2 = type(result_all[0])
      #print(tipo)
      #print(tipo_2)
      #print(result_all)
    #otro comentario



# Insert a new actividad record
def insert_actividad(session, numero_control, plantel, apellido_paterno, apellido_materno, nombres, info, pdf_url, created_at):
    created_at = datetime.now(pytz.timezone("America/Mexico_City"))
    try:
            query = text("""
                INSERT INTO actividades (
                    numero_control,
                    plantel,
                    apellido_paterno,
                    apellido_materno,
                    nombres,
                    info,
                    pdf_url,
                    created_at
                )
                VALUES (
                    :numero_control,
                    :plantel,
                    :apellido_paterno,
                    :apellido_materno,
                    :nombres,
                    :info,
                    :pdf_url,
                    :created_at
                )
            """)
            session.execute(query, {
                "numero_control": numero_control,
                "plantel": plantel,
                "apellido_paterno": apellido_paterno,
                "apellido_materno": apellido_materno,
                "nombres": nombres,
                "info": info,
                "pdf_url": pdf_url,
                "created_at": created_at
            })
            session.commit()  # Make sure to commit the transaction
            print("✅ Registro insertado correctamente")
            session.close()
    except Exception as e:
        print(f"DB ERROR Error al cargar el registro, intente más tarde: {e}")
        session.rollback()  # Rollback in case of error
        return False
    return True



def load_all_pdfs(session_db):
    query = text("""
        SELECT pdf_url, created_at, numero_control
        FROM actividades
        ORDER BY created_at DESC, numero_control DESC
    """)
    result = session_db.execute(query).mappings().all()  # <-- mapeo
    pdfs = result  # Cada dict tiene keys: 'pdf_url', 'created_at', 'numero_control'
    return pdfs



def load_user_pdfs(session_db, numero_control):
    query = text("""
        SELECT pdf_url, created_at, numero_control
        FROM actividades
        WHERE numero_control = :numero_control
        ORDER BY created_at DESC, numero_control DESC
    """)
    result = session_db.execute(query, {"numero_control": numero_control}).mappings().all()
    pdfs = result
    return pdfs


def load_user_info(session_db, numero_control):
    query = text("""
        SELECT info
        FROM users2
        WHERE numero_control = :numero_control
        LIMIT 1
    """)
    row = session_db.execute(query, {"numero_control": numero_control}).mappings().first()
    return row["info"] if row else None


def insert_plan(
    session, plan, docenteID, cve,
    created_at=None, pdf_url=None, parPond=None
):
    # Si no se proporciona created_at, se asigna la hora actual de México
    if created_at is None:
        created_at = datetime.now(pytz.timezone("America/Mexico_City"))


    # Preparación de parámetros para INSERT y UPDATE
    params = {
        "plan": plan,"plantel": plantel, 
        "docenteID": docenteID, "cve": cve,
        "created_at": created_at, "pdf_url": pdf_url
    }

    try:
        # Definición de la sentencia INSERT
        insert_query = text("""
            INSERT INTO mat1 (
                plan, docenteID, cve, created_at, pdf_url
            ) VALUES (
                :plan, :docenteID, :cve, :created_at, :pdf_url
            )
        """)
        result = session.execute(insert_query, params)
        session.commit()
        print("✅ Registro insertado correctamente")
        return result.lastrowid

    except pymysql.err.IntegrityError as e:
        if "1062" in str(e):  # Detección de clave duplicada
            print("⚠️ Plan duplicado detectado. Actualizando...")

            update_query = text("""
                UPDATE mat1 SET
                    plan = :plan,
                    docenteID = :docenteID, 
                    created_at = :created_at, pdf_url = :pdf_url, parPond = : parPond
                WHERE plan = :plan
            """)

            session.execute(update_query, params)
            session.commit()
            print("✅ Plan actualizado correctamente")
            return params.get("plan")  # Puedes retornar el identificador si corresponde

        # Si no es por duplicado, propaga el error
        raise

    except Exception as e:
        print(f"❌ DB ERROR al cargar la planeación: {e}")
        session.rollback()
        return False

    finally:
        session.close()






# Get user data by username (login verification)
def get_user_from_database(username):
    try:
        session = get_db_session()
        result = session.execute(
            text("SELECT * FROM users2 WHERE username = :val"),
            {"val": username}
        )
        row = result.mappings().first()
        session.close()
        return dict(row) if row else None
    except Exception as e:
        print(f"DB ERROR: {e}")
        return None




# Register a new user in the database
def register_user(session, numero_control, plantel, apellido_paterno,
      apellido_materno, nombres, username, password, created_at):
    try:
        session.execute(
        text("""
            INSERT INTO users2 (
                numero_control, plantel,
                apellido_paterno, apellido_materno,
                nombres, username, password, created_at
            )
            VALUES (
                :numero_control, :plantel,
                :apellido_paterno, :apellido_materno,
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
            "password": password,
            "created_at": created_at
        }
        )
        session.commit()
        return True
    except Exception as e:
        print("❌ DB ERROR register_user:", e)
        session.rollback()
        return False

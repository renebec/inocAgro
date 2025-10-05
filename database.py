import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz
import pymysql

db_connection_string = os.environ['DB_CONNECTION_STRING']
engine = create_engine(db_connection_string,
      connect_args={
            "ssl": { 
              "ca": "/etc/ssl/certs/ca-certificates.crt"
                   }
                  }
            )

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SessionLocal = sessionmaker(bind=engine)

def get_db_session():
    return SessionLocal()


def handle_choice():
    choice = None
    if request.method == 'POST':
        choice = request.form.get('choice')  # 'value1' or 'value2' or None
    return render_template('register.html', choice=choice)


def is_preregistered(numero_control):
    """
    Return True if numero_control is present in alumnos_preregistrados table.
    """
    try:
        session = get_db_session()
        result = session.execute(
            text("SELECT 1 FROM prereg WHERE controlnum = :nc"),
            {"nc": controlnum}
        )
        row = result.first()
        session.close()
        return row is not None
    except Exception as e:
        print(f"DB ERROR in is_preregistered: {e}")
        # maybe safe to reject if DB error
        return False


def load_pg_from_db():
    try:
      with engine.connect() as conn:
          result = conn.execute(text("SELECT * FROM matSat"))
          pg = result.mappings().all()
          return pg
    except Exception as e:
      print(f"DB ERROR: {e}")
      return None

def load_pg_from_db2():
    try:
      with engine.connect() as conn:
          #result = conn.execute(text("SELECT * FROM planInocAgro ORDER BY created_at DESC"))
          result = conn.execute(text("SELECT * FROM matSat"))
          pg2 = result.mappings().all()
          return pg2
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

def load_pg_from_db3():
    try:
      with engine.connect() as conn:
          #result = conn.execute(text("SELECT * FROM planInocAgro ORDER BY created_at DESC"))
          result = conn.execute(text("SELECT * FROM webContent"))
          pg3 = result.mappings().all()
          return pg3
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


def load_plan_from_db(id):
    try:
      with engine.connect() as conn:
          result = conn.execute(text("SELECT * FROM matSat WHERE id = :val"),
              {"val":id}
            )
          row = result.mappings().first()
          return dict(row) if row else None
    except Exception as e:
      print(f"DB ERROR: {e}")
      return None


def load_pgn_from_db(id):
  try:
    with engine.connect() as conn:
      result = conn.execute(
        text("SELECT * FROM matSat WHERE id = :val"),
        {"val": id}
      )
      row = result.mappings().first()
      return dict(row) if row else None
  except Exception as e:
    print(f"DB ERROR: {e}")
    return None



# Insert a new actividad record
def insert_actividad(session, actividad_num, apellido_paterno, apellido_materno, nombres, carrera, semestre, grupo, pdf_url, created_at):
    created_at = datetime.now(pytz.timezone("America/Mexico_City"))
    try:
            query = text("""
                INSERT INTO actividades (
                    actividad_num,
                    apellido_paterno,
                    apellido_materno,
                    nombres,
                    carrera,
                    semestre,
                    grupo,
                    pdf_url,
                    created_at
                )
                VALUES (
                    :actividad_num,
                    :apellido_paterno,
                    :apellido_materno,
                    :nombres,
                    :carrera,
                    :semestre,
                    :grupo,
                    :pdf_url,
                    :created_at
                )
            """)
            session.execute(query, {
                "actividad_num": actividad_num,
                "apellido_paterno": apellido_paterno,
                "apellido_materno": apellido_materno,
                "nombres": nombres,
                "carrera": carrera,
                "semestre": semestre,
                "grupo": grupo,
                "pdf_url": pdf_url,
                "created_at": created_at
            })
            session.commit()  # Make sure to commit the transaction
            session.close()
    except Exception as e:
        print(f"DB ERROR Error al cargar la actividad, intente más tarde: {e}")
        session.rollback()  # Rollback in case of error
        return False
    return True




def insert_plan(
    session, plan, asig, meta, prop, temas, plantel, ciclo, periodo,
    carrera, semestre, grupos, horas_sem, docenteID, imparte, parcial,
    trAsigP1, trtemaP1, trAsigP2, trtemaP2, trAsigP3, trtemaP3,
    trAsigP4, trtemaP4, trAsigM1, trtemaM1, trAsigM2, trtemaM2,
    trAsigM3, trtemaM3, trAsigM4, trtemaM4,
    apDur, apEv, apIns, apPond, apAct,
    deDur, deEv, deIns, dePond, deAct,
    ciDur, ciEv, ciIns, ciPond, ciAct,
    materiales, equipo, fuentes,
    elabora, revisa, avala, cve,
    created_at=None, pdf_url=None, parPond=None
):
    # Si no se proporciona created_at, se asigna la hora actual de México
    if created_at is None:
        created_at = datetime.now(pytz.timezone("America/Mexico_City"))


    # Preparación de parámetros para INSERT y UPDATE
    params = {
        "plan": plan, "asig": asig, "meta": meta, "prop": prop, "temas": temas,
        "plantel": plantel, "ciclo": ciclo, "periodo": periodo, "carrera": carrera,
        "semestre": semestre, "grupos": grupos, "horas_sem": horas_sem,
        "docenteID": docenteID, "imparte": imparte, "parcial": parcial,
        "trAsigP1": trAsigP1, "trtemaP1": trtemaP1, "trAsigP2": trAsigP2,
        "trtemaP2": trtemaP2, "trAsigP3": trAsigP3, "trtemaP3": trtemaP3,
        "trAsigP4": trAsigP4, "trtemaP4": trtemaP4,
        "trAsigM1": trAsigM1, "trtemaM1": trtemaM1, "trAsigM2": trAsigM2,
        "trtemaM2": trtemaM2, "trAsigM3": trAsigM3,
        "trtemaM3": trtemaM3, "trAsigM4": trAsigM4, "trtemaM4": trtemaM4,
        "apDur": apDur, "apEv": apEv, "apIns": apIns, "apPond": apPond,
        "apAct": apAct,
        "deDur": deDur, "deEv": deEv, "deIns": deIns, "dePond": dePond,
        "deAct": deAct,
        "ciDur": ciDur, "ciEv": ciEv, "ciIns": ciIns, "ciPond": ciPond,
        "ciAct": ciAct,
        "materiales": materiales, "equipo": equipo, "fuentes": fuentes,
        "elabora": elabora, "revisa": revisa, "avala": avala, "cve": cve,
        "created_at": created_at, "pdf_url": pdf_url, "parPond": parPond
    }

    try:
        # Definición de la sentencia INSERT
        insert_query = text("""
            INSERT INTO matSat (
                plan, asig, prop, temas, plantel, ciclo, meta, periodo, carrera,
                semestre, grupos, horas_sem, docenteID, imparte, parcial,
                trAsigP1, trtemaP1, trAsigP2, trtemaP2, trAsigP3, trtemaP3,
                trAsigP4, trtemaP4, trAsigM1, trtemaM1, trAsigM2, trtemaM2,
                trAsigM3, trtemaM3, trAsigM4, trtemaM4,
                apDur, apEv, apIns, apPond, apAct, deDur, deEv, deIns, dePond,
                deAct, ciDur, ciEv, ciIns, ciPond, ciAct,
                materiales, equipo, fuentes,
                elabora, revisa, avala, cve, created_at, pdf_url, parPond
            ) VALUES (
                :plan, :asig, :prop, :temas, :plantel, :ciclo, :meta, :periodo, :carrera,
                :semestre, :grupos, :horas_sem, :docenteID, :imparte, :parcial,
                :trAsigP1, :trtemaP1, :trAsigP2, :trtemaP2, :trAsigP3, :trtemaP3,
                :trAsigP4, :trtemaP4, :trAsigM1, :trtemaM1, :trAsigM2, :trtemaM2,
                :trAsigM3, :trtemaM3, :trAsigM4, :trtemaM4, :apDur, :apEv, :apIns,
                :apPond, :apAct, :deDur, :deEv, :deIns, :dePond, :deAct,
                :ciDur, :ciEv, :ciIns, :ciPond, :ciAct, :materiales, :equipo,
                :fuentes, :elabora, :revisa, :avala, :cve, :created_at, :pdf_url, :parPond
            )
        """)
        result = session.execute(insert_query, params)
        session.commit()
        print("✅ Plan insertado correctamente")
        return result.lastrowid

    except pymysql.err.IntegrityError as e:
        if "1062" in str(e):  # Detección de clave duplicada
            print("⚠️ Plan duplicado detectado. Actualizando...")

            update_query = text("""
                UPDATE matSat SET
                    plan = :plan, asig = :asig, meta = :meta, prop = :prop, temas = :temas,
                    plantel = :plantel, ciclo = :ciclo, periodo = :periodo, carrera = :carrera,
                    semestre = :semestre, grupos = :grupos, horas_sem = :horas_sem,
                    docenteID = :docenteID, imparte = :imparte, parcial = :parcial,
                    trAsigP1 = :trAsigP1, trtemaP1 = :trtemaP1, trAsigP2 = :trAsigP2,
                    trtemaP2 = :trtemaP2, trAsigP3 = :trAsigP3, trtemaP3 = :trtemaP3,
                    trAsigP4 = :trAsigP4, trtemaP4 = :trtemaP4,
                    trAsigM1 = :trAsigM1, trtemaM1 = :trtemaM1,
                    trAsigM2 = :trAsigM2, trtemaM2 = :trtemaM2,
                    trAsigM3 = :trAsigM3, trtemaM3 = :trtemaM3,
                    trAsigM4 = :trAsigM4, trtemaM4 = :trtemaM4,
                    apDur = :apDur, apEv = :apEv, apIns = :apIns, apPond = :apPond,
                    apAct = :apAct,
                    deDur = :deDur, deEv = :deEv, deIns = :deIns, dePond = :dePond,
                    deAct = :deAct,
                    ciDur = :ciDur, ciEv = :ciEv, ciIns = :ciIns, ciPond = :ciPond,
                    ciAct = :ciAct,
                    materiales = :materiales, equipo = :equipo, fuentes = :fuentes,
                    elabora = :elabora, revisa = :revisa, avala = :avala,
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
            text("SELECT * FROM users WHERE username = :val"),
            {"val": username}
        )
        row = result.mappings().first()
        session.close()
        return dict(row) if row else None
    except Exception as e:
        print(f"DB ERROR: {e}")
        return None



# Register a new user in the database
def register_user(session, numero_control, apellido_paterno, apellido_materno, nombres, username, password, carrera, semestre, grupo, created_at):
    # Check if username already exists
    existing_user = get_user_from_database(username)
    if existing_user:
        # If the user already exists, return False or an error message
        return False

    password = password  # You might want to hash this password
    try:
        sql = text("""
            INSERT INTO users ( numero_control, apellido_paterno, apellido_materno, nombres, username, password, carrera, semestre, grupo, created_at)
            VALUES (:numero_control, :apellido_paterno, :apellido_materno, :nombres, :username, :password, :carrera, :semestre, :grupo, :created_at)
        """)
        session.execute(sql, {
            "numero_control": numero_control,
            "apellido_paterno": apellido_paterno,
            "apellido_materno": apellido_materno,
            "nombres": nombres,
            "username": username,
            "password": password,
            "carrera": carrera,
            "semestre": semestre,
            "grupo": grupo,
            "created_at": created_at
        })
        session.commit()  # Commit the transaction
    except Exception as e:
        print(f"DB ERROR during user registration: {e}")
        session.rollback()  # Rollback in case of error
        return False
    return True
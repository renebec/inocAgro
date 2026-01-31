import time
from datetime import datetime, timedelta
import pytz
from flask import Flask, render_template, request, redirect, url_for, flash, session as flask_session
from flask_bcrypt import Bcrypt
from database import register_user, get_db_session, is_preregistered, get_user_from_database

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "dev-secret"  # Replace with os.environ.get("SECRET_KEY") in production
app.permanent_session_lifetime = timedelta(minutes=60)

# -----------------------------
# Session timeout check
# -----------------------------
def check_session_timeout():
    last = flask_session.get('last_activity')
    if not last:
        return False
    now = time.time()
    timeout_seconds = 60 * 60  # 60 minutes
    try:
        last = float(last)
    except:
        flask_session.clear()
        return False
    if now - last > timeout_seconds:
        flask_session.clear()
        return False
    flask_session['last_activity'] = time.time()
    return True

# -----------------------------
# Home page
# -----------------------------
@app.route("/")
def home():
    if not check_session_timeout():
        flash("Su sesión ha expirado. Por favor, inicie sesión nuevamente.", "danger")
        return redirect(url_for("login"))
    username = flask_session.get("username")
    numero_control = flask_session.get("numero_control")
    is_master = flask_session.get("is_master", False)
    if not username or not numero_control:
        flash("Debe iniciar sesión.", "danger")
        return redirect(url_for("login"))
    return render_template(
        "home.html",
        username=username,
        numero_control=numero_control,
        is_master=is_master
    )

# -----------------------------
# Login
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        try:
            user = get_user_from_database(username)
            if user and bcrypt.check_password_hash(user['password'], password):
                flask_session.permanent = True
                flask_session['username'] = username
                flask_session['numero_control'] = user['numero_control']
                flask_session['last_activity'] = time.time()

                # Detect teacher
                school_id = user.get('numero_control', '')
                flask_session['es_profesor'] = len(school_id) >= 4 and school_id[3].isalpha()

                # Detect master
                flask_session['is_master'] = user.get('is_master', 0) == 1

                flash(f'{username} inició sesión correctamente', 'success')
                return redirect(url_for('home'))
            else:
                flash('Usuario o contraseña incorrectos.', 'danger')
        except Exception as e:
            print("❌ Error en login:", e)
            flash('Error interno. Intenta más tarde.', 'danger')

    return render_template('login.html')

# -----------------------------
# Register selection
# -----------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        if user_type == 'A':
            return redirect(url_for('register_alumno'))
        elif user_type == 'D':
            return redirect(url_for('register_docente'))
        else:
            flash("Seleccione un tipo de usuario válido.")
    return render_template('select_register_type.html')

# -----------------------------
# Handle registration (shared)
# -----------------------------
def handle_register_user(choice):
    template_map = {
        "A": "register_alumno.html",
        "D": "register_docente.html"
    }
    template = template_map.get(choice)
    if not template:
        flash("Tipo de usuario no válido.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        db_session = None
        try:
            numero_control = request.form.get('numero_control', '').strip()
            plantel = request.form.get('plantel', '').strip()
            apellido_paterno = request.form.get('apellido_paterno', '').strip()
            apellido_materno = request.form.get('apellido_materno', '').strip()
            nombres = request.form.get('nombres', '').strip()
            username = request.form.get('username', '').strip()
            password_raw = request.form.get('password', '')

            if len(password_raw) < 8:
                flash("La contraseña debe tener al menos 8 caracteres.", "danger")
                return render_template(template)

            password = bcrypt.generate_password_hash(password_raw).decode('utf-8')

            # Validate user type vs numero_control
            is_teacher_form = (choice == "D")
            fourth_char = numero_control[3] if len(numero_control) >= 4 else None

            if is_teacher_form and (not fourth_char or not fourth_char.isalpha()):
                flash("El número de control No corresponde a un docente.", "danger")
                return render_template(template)
            if not is_teacher_form and fourth_char and fourth_char.isalpha():
                flash("El número de control corresponde a un docente. Selecciona 'Docente' para registrarte.", "danger")
                return render_template(template)

            if not is_preregistered(numero_control):
                flash("No se reconoce ese número de control; imposible registrar.", "danger")
                return render_template(template)

            db_session = get_db_session()
            created_at = datetime.now(pytz.timezone("America/Mexico_City"))

            # Check if username exists
            existing = db_session.execute(
                text("SELECT * FROM users2 WHERE username = :username"),
                {"username": username}
            ).fetchone()
            if existing:
                flash("Ese nombre de usuario ya está registrado. Por favor, elige otro.", "danger")
                return render_template(template)

            success = register_user(
                db_session,
                numero_control,
                plantel,
                apellido_paterno,
                apellido_materno,
                nombres,
                username,
                password,
                created_at
            )
            if success:
                flash(f"Registro exitoso para {nombres}!", "success")
                return redirect(url_for('login'))
            else:
                flash("Error al registrar usuario.", "danger")

        except Exception as e:
            print("❌ Error en registro:", e)
            flash("Hubo un problema al registrarte. Inténtelo más tarde.", "danger")
        finally:
            if db_session:
                db_session.close()

    return render_template(template)

@app.route("/register/alumno", methods=["GET", "POST"])
def register_alumno():
    return handle_register_user("A")

@app.route("/register/docente", methods=["GET", "POST"])
def register_docente():
    return handle_register_user("D")

# -----------------------------
# Logout
# -----------------------------
@app.route('/logout')
def logout():
    flask_session.clear()
    flash("Has cerrado sesión correctamente.", "success")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)

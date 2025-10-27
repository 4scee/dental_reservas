from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecreto123")  # Mejor usar variable de entorno

# Base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///reservas.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de reservas
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    hora = db.Column(db.String(50), nullable=False)
    servicio = db.Column(db.String(50), nullable=False)

# Modelo de usuario (para login)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Crear tablas
with app.app_context():
    db.create_all()
    # Crear usuario admin si no existe
    if not Usuario.query.filter_by(usuario='admin').first():
        admin = Usuario(usuario='admin', password_hash=generate_password_hash('1234'))
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

# ---- RUTA RESERVAS ----
@app.route('/reservas', methods=['GET', 'POST'])
def reservas():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        servicio = request.form.get('servicio')  # nuevo campo

        if not nombre or not fecha or not hora or not servicio:
            flash("Por favor completa todos los campos", "error")
            return redirect(url_for('reservas'))

        try:
            nueva = Reserva(nombre=nombre, fecha=fecha, hora=hora, servicio=servicio)
            db.session.add(nueva)
            db.session.commit()
            flash('Reserva creada con éxito.', 'success')
            return redirect(url_for('reservas'))
        except Exception as e:
            db.session.rollback()
            flash(f"Ocurrió un error al guardar la reserva: {e}", "error")
            return redirect(url_for('reservas'))

    reservas_lista = Reserva.query.order_by(Reserva.fecha, Reserva.hora).all()
    return render_template('reservas.html', reservas=reservas_lista)

# ---- LOGIN ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        user = Usuario.query.filter_by(usuario=usuario).first()
        if user and check_password_hash(user.password_hash, password):
            session['usuario'] = usuario
            flash('Bienvenido al panel administrativo.', 'info')
            return redirect(url_for('admin'))
        else:
            flash('Credenciales incorrectas.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('index'))

# ---- PANEL ADMIN ----
@app.route('/admin')
def admin():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder al panel.', 'warning')
        return redirect(url_for('login'))
    reservas = Reserva.query.order_by(Reserva.fecha, Reserva.hora).all()
    return render_template('admin.html', reservas=reservas)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    reserva = Reserva.query.get(id)
    if reserva:
        db.session.delete(reserva)
        db.session.commit()
        flash('Reserva eliminada.', 'info')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)

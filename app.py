from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Conexión a PostgreSQL usando variable de entorno DATABASE_URL (Railway)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de reservas
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(10), nullable=False)
    servicio = db.Column(db.String(100), nullable=False)

# Crear tablas automáticamente si no existen
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reservas', methods=['GET', 'POST'])
def reservas():
    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha = request.form['fecha']
        hora = request.form['hora']
        servicio = request.form['servicio']
        nueva = Reserva(nombre=nombre, fecha=fecha, hora=hora, servicio=servicio)
        db.session.add(nueva)
        db.session.commit()
        return redirect('/reservas')
    
    reservas = Reserva.query.order_by(Reserva.fecha, Reserva.hora).all()
    return render_template('reservas.html', reservas=reservas)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    reserva = Reserva.query.get_or_404(id)
    db.session.delete(reserva)
    db.session.commit()
    return redirect('/reservas')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    reserva = Reserva.query.get_or_404(id)
    if request.method == 'POST':
        reserva.nombre = request.form['nombre']
        reserva.fecha = request.form['fecha']
        reserva.hora = request.form['hora']
        reserva.servicio = request.form['servicio']
        db.session.commit()
        return redirect('/reservas')
    return render_template('editar.html', reserva=reserva)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

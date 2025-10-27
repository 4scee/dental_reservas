from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB = "reservas.db"

# Crear DB si no existe
if not os.path.exists(DB):
    conn = sqlite3.connect(DB)
    conn.execute('''CREATE TABLE reservas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        fecha TEXT NOT NULL,
                        hora TEXT NOT NULL,
                        servicio TEXT NOT NULL
                    )''')
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reservas', methods=['GET', 'POST'])
def reservas():
    conn = get_db_connection()
    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha = request.form['fecha']
        hora = request.form['hora']
        servicio = request.form['servicio']
        conn.execute("INSERT INTO reservas (nombre, fecha, hora, servicio) VALUES (?, ?, ?, ?)",
                     (nombre, fecha, hora, servicio))
        conn.commit()
        return redirect('/reservas')
    
    reservas = conn.execute('SELECT * FROM reservas ORDER BY fecha, hora').fetchall()
    conn.close()
    return render_template('reservas.html', reservas=reservas)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM reservas WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/reservas')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    reserva = conn.execute("SELECT * FROM reservas WHERE id=?", (id,)).fetchone()
    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha = request.form['fecha']
        hora = request.form['hora']
        servicio = request.form['servicio']
        conn.execute("UPDATE reservas SET nombre=?, fecha=?, hora=?, servicio=? WHERE id=?",
                     (nombre, fecha, hora, servicio, id))
        conn.commit()
        conn.close()
        return redirect('/reservas')
    conn.close()
    return render_template('editar.html', reserva=reserva)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

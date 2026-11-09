

from flask import Flask, render_template, request, redirect, url_for, session
import secrets
from datetime import date
from math import isfinite
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Base de datos SQLite
BASE_DATOS = Path(__file__).with_name("gastos.db")


# Crear la tabla de gastos
def crear_base_datos():
    conexion = sqlite3.connect(BASE_DATOS)

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL CHECK(monto > 0)
        )
    """)

    conexion.commit()
    conexion.close()


crear_base_datos()


# Inicio de sesion
@app.route("/", methods=["GET", "POST"])
def inicio():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        clave = request.form.get("clave")

        if usuario == "admin" and clave == "123":
            session["usuario"] = usuario
            return redirect(url_for("panel"))
        else:
            return render_template(
                "login.html",
                error="Usuario o contraseña incorrectos"
            )

    return render_template("login.html")



# Panel principal y registro de gastos
@app.route("/panel", methods=["GET", "POST"])
def panel():

    if "usuario" not in session:
        return redirect(url_for("inicio"))

    if request.method == "POST":

        fecha = request.form.get("fecha", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        monto_texto = request.form.get("monto", "")

        try:
            date.fromisoformat(fecha)
            monto = float(monto_texto)

            if not descripcion or not isfinite(monto) or monto <= 0:
                raise ValueError

        except ValueError:
            return render_template(
                "panel.html",
                error="Verifica la fecha, descripcion y monto."
            )

        # Guardar el gasto en SQLite
        with sqlite3.connect(BASE_DATOS) as conexion:
            conexion.execute(
                """
                INSERT INTO gastos (fecha, descripcion, monto)
                VALUES (?, ?, ?)
                """,
                (fecha, descripcion, monto)
            )

        return redirect(url_for("panel", guardado=1))

    
    guardado = request.args.get("guardado") == "1"

    # Consultar los gastos guardados
    with sqlite3.connect(BASE_DATOS) as conexion:
        gastos = conexion.execute(
            """SELECT id, fecha, descripcion, monto
            FROM gastos
            ORDER BY fecha DESC, id DESC
            """
        ).fetchall()

    # Calcular el total de gastos
    total = sum(gasto[3] for gasto in gastos)

    return render_template(
        "panel.html",
        guardado=guardado,
        gastos=gastos,
        total=total
    )


# Reporte de gastos
@app.route("/reporte")
def reporte():

    if "usuario" not in session:
        return redirect(url_for("inicio"))

    # Obtener gastos desde SQLite
    conexion = sqlite3.connect(BASE_DATOS)

    gastos = conexion.execute("""
        SELECT fecha, descripcion, monto
        FROM gastos
        ORDER BY fecha DESC, id DESC
    """).fetchall()

    conexion.close()

    # Calcular el total
    total = sum(gasto[2] for gasto in gastos)

    return render_template(
        "reporte.html",
        gastos=gastos,
        total=total
    )


# Eliminar un gasto
@app.route("/eliminar/<int:gasto_id>", methods=["POST"])
def eliminar_gasto(gasto_id):

    if "usuario" not in session:
        return redirect(url_for("inicio"))

    with sqlite3.connect(BASE_DATOS) as conexion:
        conexion.execute(
            "DELETE FROM gastos WHERE id = ?",
            (gasto_id,)
        )

    return redirect(url_for("panel"))


# Cerrar sesion
@app.route("/salir")
def salir():
    session.clear()
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(debug=True)

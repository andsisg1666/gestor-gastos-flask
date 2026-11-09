
from app import app


# Prueba 1: comprobar inicio de sesion
def test_pagina_inicio():
    app.config["TESTING"] = True

    with app.test_client() as cliente:
        respuesta = cliente.get("/")

        assert respuesta.status_code == 200
        assert b"Control de Gastos" in respuesta.data


# Prueba 2: proteger el panel
def test_panel_sin_sesion():
    app.config["TESTING"] = True

    with app.test_client() as cliente:
        respuesta = cliente.get("/panel")

        assert respuesta.status_code == 302
        assert respuesta.headers["Location"].endswith("/")



# Prueba 3: inicio de sesion correcto
def test_login_correcto():
    app.config["TESTING"] = True

    with app.test_client() as cliente:
        respuesta = cliente.post("/", data={
            "usuario": "admin",
            "clave": "123"
        })

        assert respuesta.status_code == 302
        assert respuesta.headers["Location"].endswith("/panel")


# Prueba 4: inicio de sesion incorrecto
def test_login_incorrecto():
    app.config["TESTING"] = True

    with app.test_client() as cliente:
        respuesta = cliente.post("/", data={
            "usuario": "admin",
            "clave": "incorrecta"
        })

        assert respuesta.status_code == 200
        assert b"incorrectos" in respuesta.data


import sqlite3
import pytest
import app as modulo


@pytest.fixture
def cliente(monkeypatch, tmp_path):
    # Base de datos temporal para las pruebas
    base_prueba = tmp_path / "pruebas.db"

    monkeypatch.setattr(modulo, "BASE_DATOS", base_prueba)
    modulo.crear_base_datos()

    modulo.app.config["TESTING"] = True

    with modulo.app.test_client() as cliente:
        yield cliente, base_prueba


# Prueba 5: registrar un gasto en SQLite
def test_registrar_gasto(cliente):
    navegador, base_prueba = cliente

    # Iniciar sesion
    navegador.post("/", data={
        "usuario": "admin",
        "clave": "123"
    })

    # Registrar gasto de prueba
    respuesta = navegador.post("/panel", data={
        "fecha": "2026-11-08",
        "descripcion": "Cuadernos de prueba",
        "monto": "25.50"
    }, follow_redirects=True)

    assert respuesta.status_code == 200

    # Comprobar el registro en SQLite
    with sqlite3.connect(base_prueba) as conexion:
        gasto = conexion.execute(
            "SELECT descripcion, monto FROM gastos"
        ).fetchone()

    assert gasto == ("Cuadernos de prueba", 25.50)


# Prueba 6: eliminar un gasto
def test_eliminar_gasto(cliente):
    navegador, base_prueba = cliente

    # Iniciar sesion
    navegador.post("/", data={
        "usuario": "admin",
        "clave": "123"
    })

    # Registrar un gasto de prueba
    navegador.post("/panel", data={
        "fecha": "2026-11-08",
        "descripcion": "Gasto para eliminar",
        "monto": "15.00"
    })

    # Obtener el ID del gasto registrado
    with sqlite3.connect(base_prueba) as conexion:
        gasto = conexion.execute(
            "SELECT id FROM gastos"
        ).fetchone()

    assert gasto is not None

    # Eliminar el gasto
    respuesta = navegador.post(
        f"/eliminar/{gasto[0]}",
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    # Comprobar que ya no existe
    with sqlite3.connect(base_prueba) as conexion:
        cantidad = conexion.execute(
            "SELECT COUNT(*) FROM gastos"
        ).fetchone()[0]

    assert cantidad == 0


# Prueba 7: comprobar el reporte de gastos
def test_reporte_gastos(cliente):
    navegador, base_prueba = cliente

    # Iniciar sesion
    navegador.post("/", data={
        "usuario": "admin",
        "clave": "123"
    })

    # Registrar el primer gasto
    navegador.post("/panel", data={
        "fecha": "2026-11-08",
        "descripcion": "Papeleria",
        "monto": "10.00"
    })

    # Registrar el segundo gasto
    navegador.post("/panel", data={
        "fecha": "2026-11-08",
        "descripcion": "Transporte",
        "monto": "12.50"
    })

    # Consultar el reporte
    respuesta = navegador.get("/reporte")

    # Comprobar los resultados
    assert respuesta.status_code == 200
    assert b"Reporte de Gastos" in respuesta.data
    assert b"Papeleria" in respuesta.data
    assert b"Transporte" in respuesta.data
    assert b"S/ 22.50" in respuesta.data

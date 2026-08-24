"""
Prueba rapida de la base de datos: confirma que farmacos.db existe y que
una consulta basica funciona. Corre esto DESPUES de haber corrido
setup_db.py al menos una vez (eso crea farmacos.db en esta misma carpeta).
"""
import sqlite3
import os

if not os.path.exists("../farmacos.db"):
    raise SystemExit(
        "No encontre farmacos.db en la carpeta superior. Corre primero: "
        "python3 ../setup_db.py"
    )

conn = sqlite3.connect("../farmacos.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT COUNT(*) as total FROM farmacos")
total = cur.fetchone()["total"]
print(f"Farmacos en la base de datos: {total}")

cur.execute(
    "SELECT * FROM farmacos WHERE nombre LIKE ? AND especie = ?",
    ("%Amoxicilina%", "perro"),
)
fila = cur.fetchone()
conn.close()

if fila:
    print("\nConsulta de prueba (Amoxicilina, perro):")
    print(dict(fila))
    print("\nLa base de datos esta OK.")
else:
    print("\nLa consulta no devolvio resultados. Revisa el contenido de la tabla.")

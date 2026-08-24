"""
Crea y llena la base de datos local de farmacos veterinarios (SQLite).
Los valores de dosis son ILUSTRATIVOS para el prototipo: antes de usarlos
en la app final, verificalos contra Plumb's Veterinary Drug Handbook,
el Manual Merck o el material de tu catedra.

Este script es IDEMPOTENTE: lo puedes correr las veces que quieras y
siempre vas a terminar con exactamente 18 registros (borra los datos
viejos antes de insertar los nuevos), asi que no genera duplicados.
"""
import sqlite3

conn = sqlite3.connect("farmacos.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS farmacos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    especie TEXT NOT NULL,
    dosis_min REAL NOT NULL,
    dosis_max REAL NOT NULL,
    unidad TEXT NOT NULL DEFAULT 'mg/kg',
    via TEXT NOT NULL,
    frecuencia TEXT NOT NULL,
    contraindicaciones TEXT
)
""")

farmacos = [
    ("Amoxicilina", "Antibiotico", "perro", 10, 20, "mg/kg", "Oral", "Cada 12 h", "Alergia conocida a penicilinas"),
    ("Amoxicilina", "Antibiotico", "gato", 10, 20, "mg/kg", "Oral", "Cada 12 h", "Alergia conocida a penicilinas"),
    ("Amoxicilina + acido clavulanico", "Antibiotico", "perro", 12.5, 25, "mg/kg", "Oral", "Cada 12 h", "Alergia a penicilinas"),
    ("Enrofloxacina", "Antibiotico", "perro", 5, 10, "mg/kg", "Oral/IM", "Cada 24 h", "Evitar en cachorros en crecimiento"),
    ("Enrofloxacina", "Antibiotico", "gato", 5, 5, "mg/kg", "Oral/IM", "Cada 24 h", "Riesgo de dano ocular a dosis altas en gatos"),
    ("Cefalexina", "Antibiotico", "perro", 15, 30, "mg/kg", "Oral", "Cada 12 h", "Alergia a cefalosporinas"),
    ("Ivermectina", "Antiparasitario", "perro", 0.2, 0.2, "mg/kg", "Oral/SC", "Dosis unica o mensual", "Contraindicado en razas sensibles (Collie y similares)"),
    ("Fenbendazol", "Antiparasitario", "perro", 50, 50, "mg/kg", "Oral", "Cada 24 h por 3 dias", "Ninguna relevante"),
    ("Praziquantel", "Antiparasitario", "gato", 5, 5, "mg/kg", "Oral", "Dosis unica", "Ninguna relevante"),
    ("Milbemicina oxima", "Antiparasitario", "perro", 0.5, 0.5, "mg/kg", "Oral", "Mensual", "Contraindicado en cachorros muy jovenes"),
    ("Meloxicam", "AINE / analgesico", "perro", 0.1, 0.2, "mg/kg", "Oral/SC", "Cada 24 h", "Evitar en insuficiencia renal"),
    ("Meloxicam", "AINE / analgesico", "gato", 0.05, 0.1, "mg/kg", "Oral/SC", "Cada 24 h", "Uso muy cauteloso, riesgo renal"),
    ("Carprofeno", "AINE / analgesico", "perro", 2, 4, "mg/kg", "Oral", "Cada 12-24 h", "Evitar en enfermedad hepatica o renal"),
    ("Tramadol", "Analgesico", "perro", 2, 5, "mg/kg", "Oral", "Cada 8-12 h", "Precaucion con otros depresores del SNC"),
    ("Acepromazina", "Sedante", "perro", 0.5, 1, "mg/kg", "Oral/IM/IV", "Segun necesidad", "Contraindicado en epilepticos"),
    ("Ketamina", "Anestesico", "gato", 5, 10, "mg/kg", "IM", "Dosis unica, segun procedimiento", "Precaucion en cardiopatias"),
    ("Propofol", "Anestesico", "perro", 4, 6, "mg/kg", "IV", "Induccion, dosis unica", "Ajustar en pacientes debilitados"),
    ("Dexmedetomidina", "Sedante", "perro", 0.005, 0.01, "mg/kg", "IM/IV", "Segun necesidad", "Contraindicado en cardiopatias"),
]

cur.execute("DELETE FROM farmacos")

cur.executemany("""
INSERT INTO farmacos (nombre, categoria, especie, dosis_min, dosis_max, unidad, via, frecuencia, contraindicaciones)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", farmacos)

conn.commit()
conn.close()
print(f"Base de datos creada con {len(farmacos)} registros.")
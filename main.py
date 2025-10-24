from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import pusher

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos (ajusta aquí o mediante variables de entorno)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql-ybec.alwaysdata.net"),
    "user": os.getenv("DB_USER", "ybec"),
    "password": os.getenv("DB_PASS", "8B5EED1D"),
    "database": os.getenv("DB_NAME", "ybec_inventario"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

def serialize_row(row):
    if not row:
        return None
    # Convertir datetime a string ISO para JSON
    ts = row.get("fecha_publicacion")
    if isinstance(ts, (datetime.date, datetime.datetime)):
        row["fecha_publicacion"] = ts.isoformat(sep=' ')
    return row

def insert_message_to_db(texto):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Cambia el nombre de la tabla/columna si es distinto
        cur.execute("INSERT INTO mensajes (mensaje) VALUES (%s)", (texto,))
        conn.commit()
        last_id = cur.lastrowid
        cur.execute("SELECT id, mensaje, fecha_publicacion FROM mensajes WHERE id = %s", (last_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return serialize_row(row)
    except Exception as e:
        print("DB insert error:", e)
        return None

@app.route("/", methods=[ "POST"])
def hola_mundo():
    
    data = request.get_json()
   
    pusher_client = pusher.Pusher(
        app_id = '2062322',
        key = "c87165fe436b0a5d5ba0",
        secret = "76dc3c495d2f2c5eaf43",
        cluster = "mt1",
        ssl=True
    )

    if data and "message" in data:
        message = data["message"]
    else:
        message = request.form.get("message") or request.get_data(as_text=True) or ""

    pusher_client.trigger('my-channel', 'my-event', message)

    #guardar en base de datos

    success = insert_message_to_db(message)

    if success:
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"status": "db_error"}), 500

    return ".."

@app.route("/messages", methods=["GET"])
def get_messages():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, mensaje, fecha_publicacion FROM mensajes ORDER BY fecha_publicacion DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # Serializar timestamps
        rows = [serialize_row(r) for r in rows]
        return jsonify(rows), 200
    except Exception as e:
        print("DB fetch error:", e)
        return jsonify({"error": "db_error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
# ...existing code...
#  mysql-ybec.alwaysdata.net

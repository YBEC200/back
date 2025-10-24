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

def insert_message_to_db(texto):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Cambia el nombre de la tabla/columna si es distinto
        cur.execute("INSERT INTO mensajes (mensaje) VALUES (%s)", (texto,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        # Log sencillo; en producción usar logger
        print("DB insert error:", e)
        return False

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

# ...existing code...

@app.route("/messages", methods=["GET"])
def get_messages():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor(dictionary=True)  # Usar dictionary=True para obtener resultados como diccionarios
        
        # Consulta SQL para obtener mensajes ordenados por fecha descendente
        cur.execute("SELECT mensaje, fecha_publicacion FROM mensajes ORDER BY fecha_publicacion DESC")
        
        messages = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify(messages), 200
        
    except Exception as e:
        print("Error fetching messages:", e)
        return jsonify({"error": "Database error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
#  mysql-ybec.alwaysdata.net

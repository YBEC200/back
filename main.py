from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import pusher

app = Flask(__name__)
CORS(app)

# Configuración de Pusher (movida fuera de la ruta para mejor rendimiento)
pusher_client = pusher.Pusher(
    app_id = '2062322',
    key = "c87165fe436b0a5d5ba0",
    secret = "76dc3c495d2f2c5eaf43",
    cluster = "mt1",
    ssl=True
)

# Corrección de la configuración de la base de datos
DB_CONFIG = {
    "host": "mysql-ybec.alwaysdata.net",
    "user": "ybec",
    "password": "8B5EED1D",
    "database": "ybec_inventario"
}

def insert_message_to_db(texto):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Asegúrate que la tabla 'mensajes' existe con la columna 'mensaje'
        cur.execute("INSERT INTO mensajes (mensaje) VALUES (%s)", (texto,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("DB insert error:", str(e))
        return False

@app.route("/", methods=["POST"])
def hola_mundo():
    try:
        data = request.get_json()
        
        if data and "message" in data:
            message = data["message"]
        else:
            return jsonify({"status": "error", "message": "No message provided"}), 400

        # Emitir mensaje a Pusher
        pusher_client.trigger('my-channel', 'my-event', message)

        # Guardar en base de datos
        success = insert_message_to_db(message)

        if success:
            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"status": "db_error"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
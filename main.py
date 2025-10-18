from flask import Flask, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


@app.route("/", methods=[ "POST"])
def hola_mundo():
    import pusher
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
    return ".."

if __name__ == "__main__":
    app.run(debug=True)

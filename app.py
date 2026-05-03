from flask import Flask, request
from services.stream_service import publicar_evento
from datetime import datetime
import uuid

app = Flask(__name__)

@app.route('/consumo', methods=['POST'])
def registrar_consumo():

    data = request.json

    evento = {
        "event_id": str(uuid.uuid4()),
        "dispositivo_id": data["dispositivo_id"],
        "zona": data["zona"],
        "consumo": str(data["consumo"]),
        "timestamp": datetime.now().isoformat()
    }

    publicar_evento(evento)

    return {
        "mensaje": "Evento enviado al stream",
        "evento": evento
    }

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request

app = Flask(__name__)

@app.route('/consumo', methods=['POST'])
def registrar_consumo():

    data = request.json

    print(data)

    return {
        "mensaje": "dato recibido"
    }

app.run(debug=True)
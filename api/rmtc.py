from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
import subprocess, json

app = FlaskAPI(__name__)

@app.route("/ponto/<int:ponto>", methods=['GET'])
def ponto(ponto):
    return consultar(ponto, '', '')

@app.route("/linha/<int:linha>", methods=['GET'])
def linha(linha):
    return consultar('', linha, '')

@app.route("/pesquisar/<termo>", methods=['GET'])
def pesquisar(termo):
    return consultar('', '', termo)

def consultar(ponto, linha, termo):
    with open("horario.json", "r+") as file:
        file.truncate(0)
        commands = [
            "scrapy",
            "crawl",
            "rmtc",
            "-o", file.name,
            "-a", "termo_busca={termo}".format(termo=termo), 
            "-a", "numero_ponto={ponto}".format(ponto=ponto), 
            "-a", "numero_linha={linha}".format(linha=linha)
        ]
        result = subprocess.run(commands, stdout=subprocess.PIPE)
        horarios = json.loads( file.read() )
        return horarios

if __name__ == "__main__":
    app.run()
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask
from flask import render_template
from flask import request
from dataframes import usuariosCriticos
from dataframes import websCriticas
from dataframes import mas50Clickados
from dataframes import menos50Clickados
from sklearn import tree
import json
import plotly.graph_objects as go

app = Flask(__name__)


def decisionTreeClassifier():
    with open('static/users_IA_clases.json') as json_file:
        usersClasesDatos = json.load(json_file)
    usersClasesDatos = usersClasesDatos['usuarios']

    usersClasesTrain = []
    usersClasesTest = []
    vulnerableTrain = []
    vulnerableTest = []

    for i in range(int((len(usersClasesDatos) * 0.52))):
        vulnerableTrain.append(usersClasesDatos[i]['vulnerable'])

        usersClasesTrain.append(
            [usersClasesDatos[i]['emails_phishing_recibidos'], usersClasesDatos[i]['emails_phishing_clicados']])

    for i in range(int((len(usersClasesDatos) * 0.52)), len(usersClasesDatos)):
        vulnerableTest.append(usersClasesDatos[i]['vulnerable'])
        usersClasesTest.append(
            [usersClasesDatos[i]['emails_phishing_recibidos'], usersClasesDatos[i]['emails_phishing_clicados']])

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(usersClasesTrain, vulnerableTrain)
    return clf


def devolverJSONUsuariosCriticos(numeroU):
    import plotly
    a = plotly.utils.PlotlyJSONEncoder
    df = usuariosCriticos()
    traceU = go.Bar(x=df['nombreu'][0:numeroU], y=df['porcentaje'])
    layoutU = go.Layout(title="Usuarios más críticos", xaxis=dict(title="Usuarios con contraseña vulnerable"),
                        yaxis=dict(title="Porcentaje clicks emails"))
    dataU = [traceU]
    figU = go.Figure(data=dataU, layout=layoutU)
    graphJSONU = json.dumps(figU, cls=a)
    return graphJSONU


def devolverJSONWebsVulnerables(numeroW):
    import plotly
    a = plotly.utils.PlotlyJSONEncoder
    dfW = websCriticas()
    traceW = go.Bar(x=dfW['nombre'][0:numeroW], y=dfW['total'])
    layoutW = go.Layout(title="Webs más vulnerables", xaxis=dict(title="Webs"),
                        yaxis=dict(title="Total desactualizadas"))
    dataW = [traceW]
    figW = go.Figure(data=dataW, layout=layoutW)
    graphJSONW = json.dumps(figW, cls=a)
    return graphJSONW


def devolverJSONSeleccion(seleccion):
    import plotly
    a = plotly.utils.PlotlyJSONEncoder
    seleccionJSON = None
    if seleccion == "mas50":
        dfM50 = mas50Clickados()
        traceW = go.Bar(x=dfM50['nombre'], y=dfM50['porcentajeSpamClick'])
        layoutW = go.Layout(title="Usuarios que clickan más del 50% de spam", xaxis=dict(title="Usuarios"),
                            yaxis=dict(title="Porcentaje clicks"))
        dataW = [traceW]
        figW = go.Figure(data=dataW, layout=layoutW)
        seleccionJSON = json.dumps(figW, cls=a)
        return seleccionJSON
    elif seleccion == "menos50":
        dfM50 = menos50Clickados()
        traceW = go.Bar(x=dfM50['nombreu'], y=dfM50['porcentajeSpamClick'])
        layoutW = go.Layout(title="Usuarios que clickan 50% de spam o menos", xaxis=dict(title="Usuarios"),
                            yaxis=dict(title="Porcentaje clicks"))
        dataW = [traceW]
        figW = go.Figure(data=dataW, layout=layoutW)
        seleccionJSON = json.dumps(figW, cls=a)
        return seleccionJSON
    else:
        return seleccionJSON


def devolverLast10CVE():
    df = pd.read_json("https://cve.circl.lu/api/last")
    df = df.head(10)
    return df

def devolverTopMicrosoftVulnerabilidades():
    df = pd.read_json("https://cve.circl.lu/api/browse/microsoft")
    return df


@app.route('/')
def indice():
    return render_template("index.html")


@app.route("/formApartado2")
def tablas():
    return render_template("formApartado2.html")


@app.route("/graficosApartado2", methods=["GET", "POST"])
def criticalUsers():
    numeroU = int(request.form['numU'])
    numeroW = int(request.form['numW'])
    if numeroU != 0:
        graphJSONU = devolverJSONUsuariosCriticos(numeroU)
    if numeroW != 0:
        graphJSONW = devolverJSONWebsVulnerables(numeroW)
    if numeroU != 0 and numeroW != 0:
        return render_template("graficosApartado2.html", graphJSONU=graphJSONU, graphJSONW=graphJSONW)
    elif numeroU != 0:
        return render_template("graficosApartado2.html", graphJSONU=graphJSONU)
    elif numeroW != 0:
        return render_template("graficosApartado2.html", graphJSONW=graphJSONW)
    else:
        return render_template("index.html")


@app.route("/formApartado3")
def formApartado3():
    return render_template("formApartado3.html")


@app.route("/graficosApartado3", methods=["GET", "POST"])
def graficosApartado3():
    numeroU = int(request.form['numU'])
    seleccion = request.form['seleccion']
    if numeroU != 0:
        graphJSONU = devolverJSONUsuariosCriticos(numeroU)
    seleccionJSON = devolverJSONSeleccion(seleccion)
    if numeroU != 0 and seleccionJSON is not None:
        return render_template("graficosApartado3.html", graphJSONU=graphJSONU, seleccionJSON=seleccionJSON)
    elif numeroU != 0:
        return render_template("graficosApartado3.html", graphJSONU=graphJSONU)
    elif seleccionJSON is not None:
        return render_template("graficosApartado3.html", seleccionJSON=seleccionJSON)
    else:
        return render_template("index.html")


@app.route("/tenLastCVE")
def tenLastCVE():
    df = devolverLast10CVE()
    return render_template('tenLastCVE.html', tables=[df.to_html(classes='data', header="true")])


@app.route("/TopMicrosoftVulnerabilidades")
def TopMicrosoftVulnerabilidades():
    df = devolverTopMicrosoftVulnerabilidades()
    return render_template('TopMicrosoftVulnerabilidades.html', tables=[df.to_html(classes='data', header="true")])


@app.route("/predecir")
def predecir():
    return render_template("formUserVuln.html")


@app.route("/predecirUserVuln", methods=["GET", "POST"])
def predecirUserVuln():
    clf = decisionTreeClassifier()
    emailsRecibidos = int(request.form["emailsR"])
    emailsClickados = int(request.form["emailsC"])
    nombre = str(request.form["nombre"])
    prediccion = clf.predict([[emailsRecibidos, emailsClickados]])
    if prediccion[0] == 0:
        return render_template("vulnerable.html", nombre=nombre, novuln=1)
    else:
        return render_template("vulnerable.html", nombre=nombre, vuln=1)


if __name__ == '__main__':
    app.run(debug=True)

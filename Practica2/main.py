import pandas as pd
from flask import Flask
from flask import render_template
from flask import request
from dataframes import usuariosCriticos
from dataframes import websCriticas
from dataframes import mas50Clickados
from dataframes import menos50Clickados
import urllib
import json
import plotly.graph_objects as go
import matplotlib.pyplot as plt

app = Flask(__name__)


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
    return render_template('tenLastCVE.html', tables=[df.to_html(classes='data')], titles=df.columns.values)


@app.route('/plotly')
def plotly():
    fig = go.Figure(
        data=[go.Bar(y=[2, 1, 3])],
        layout_title_text="Figura"
    )
    # fig.show()
    import plotly
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('hello.html', graphJSON=graphJSON)


if __name__ == '__main__':
    app.run(debug=True)

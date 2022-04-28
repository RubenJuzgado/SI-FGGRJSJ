from flask import Flask
from flask import render_template
from flask import request
from dataframes import usuariosCriticos
from dataframes import websCriticas
import json
import plotly.graph_objects as go
import matplotlib.pyplot as plt

app = Flask(__name__)


@app.route('/')
def indice():
    return render_template("index.html")


@app.route("/formApartado2")
def tablas():
    return render_template("formApartado2.html")


@app.route("/graficosApartado2", methods=["GET", "POST"])
def criticalUsers():
    import plotly
    a = plotly.utils.PlotlyJSONEncoder
    graphJSONU = None
    graphJSONW = None
    if request.form['numU'] != "0":
        df = usuariosCriticos()
        numeroU = int(request.form['numU'])
        traceU = go.Bar(x=df['nombreu'][0:numeroU], y=df['porcentaje'])
        layoutU = go.Layout(title="Usuarios más críticos", xaxis=dict(title="Usuarios con contraseña vulnerable"),
                       yaxis=dict(title="Porcentaje clicks emails"))
        dataU = [traceU]
        figU = go.Figure(data=dataU, layout=layoutU)

        graphJSONU = json.dumps(figU, cls=a)
    if request.form['numW'] != 0:
        dfW = websCriticas()
        numeroW = int(request.form['numW'])
        traceW = go.Bar(x=dfW['nombre'][0:numeroW], y=dfW['total'])
        layoutW = go.Layout(title="Webs más vulnerables", xaxis=dict(title="Webs"),
                            yaxis=dict(title="Total desactualizadas"))
        dataW = [traceW]
        figW = go.Figure(data=dataW, layout=layoutW)

        graphJSONW = json.dumps(figW, cls=a)
    return render_template("graficosApartado2.html", graphJSONU=graphJSONU, graphJSONW=graphJSONW)


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

from flask import Flask
from flask import render_template
from flask import request
from dataframes import usuariosCriticos
import json
import plotly.graph_objects as go
import matplotlib.pyplot as plt
app = Flask(__name__)


@app.route('/')
def indice():
    return render_template("index.html")


@app.route('/tablas')
def tablas():
    df = usuariosCriticos()
    trace = go.Bar(x=df['nombreu'][0:10], y=df['porcentaje'])
    layout = go.Layout(title="Usuarios mas críticos", xaxis=dict(title="Usuarios con contraseña vulnerable"),
                       yaxis=dict(title="Porcentaje clicks emails"))
    data = [trace]
    fig = go.Figure(data=data, layout=layout)
    import plotly
    a = plotly.utils.PlotlyJSONEncoder

    graphJSON = json.dumps(fig, cls=a)
    return render_template("tablas.html", graphJSON=graphJSON)


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



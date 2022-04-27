from flask import Flask
from flask import render_template
from flask import request

import json
import plotly.graph_objects as go

app = Flask(__name__)


@app.route('/')
def indice():
    return render_template("index.html")


@app.route('/tablas')
def tablas():
    return render_template("tablas.html")


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

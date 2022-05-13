import pandas as pd
from flask import Flask, redirect, url_for
from flask import render_template
from flask import request
from flask_login import LoginManager, current_user, login_user, logout_user
from werkzeug.urls import url_parse

from dataframes import usuariosCriticos
from dataframes import websCriticas
from dataframes import mas50Clickados
from dataframes import menos50Clickados
from sklearn import tree
import json
import plotly.graph_objects as go

from forms import LoginForm, SignupForm
from models import users, get_user, User

app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298177da20fe'
login_manager = LoginManager(app)
login_manager.login_view = "login"


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
        traceW = go.Bar(x=dfM50['nombre'], y=dfM50['porcentajeSpamClick'])
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
    df = df.head(101)
    return df


@app.route('/')
def index():
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


@app.route("/registro", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        # Creamos el usuario y lo guardamos
        user = User(len(users) + 1, name, email, password)
        users.append(user)
        # Dejamos al usuario logueado
        login_user(user, remember=True)
        next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template("registro.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)




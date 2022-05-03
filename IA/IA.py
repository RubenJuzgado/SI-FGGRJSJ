import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
import json
import plotly.graph_objects as go


def regresionLineal():
    with open('static/users_IA_clases.json') as json_file:
        usersClasesDatos = json.load(json_file)
    usersClasesDatos = usersClasesDatos['usuarios']

    usersClasesTrain = []
    usersClasesTest = []
    vulnerableTrain = []
    vulnerableTest = []
    for i in range(int((len(usersClasesDatos) * 0.6))):
        vulnerableTrain.append(usersClasesDatos[i]['vulnerable'])

        usersClasesTrain.append(
            [usersClasesDatos[i]['emails_phishing_recibidos'], usersClasesDatos[i]['emails_phishing_clicados']])

    for i in range(int((len(usersClasesDatos) * 0.6)), len(usersClasesDatos)):
        vulnerableTest.append(usersClasesDatos[i]['vulnerable'])
        usersClasesTest.append(
            [usersClasesDatos[i]['emails_phishing_recibidos'], usersClasesDatos[i]['emails_phishing_clicados']])

    print("UsersClasesTrain:")
    print(usersClasesTrain)
    print("UsersClasesTest:")
    print(usersClasesTest)
    print("VulnerableTrain:")
    print(vulnerableTrain)
    print("VulnerableTest:")
    print(vulnerableTest)

    regr = linear_model.LinearRegression()
    regr.fit(usersClasesTrain, vulnerableTrain)
    print("Regr.coef_:")
    print(regr.coef_)
    usersPredecir_pred = regr.predict(usersClasesTest)
    porcentajeClickados = []
    coefDeter = r2_score(vulnerableTest, usersPredecir_pred)
    print(coefDeter)
    for i in range(len(usersClasesTest)):
        if usersClasesTest[i][0] != 0:
            data = usersClasesTest[i][1] / usersClasesTest[i][0]
            porcentajeClickados.append(data)
        else:
            porcentajeClickados.append(0)

    print("PorcentajeClickados")
    print(porcentajeClickados)

    print("regr.intercept")
    print(regr.intercept_)

    plt.scatter(porcentajeClickados, vulnerableTest)
    plt.plot(np.array(porcentajeClickados) * coefDeter + regr.intercept_, porcentajeClickados)
    plt.show()


if __name__ == '__main__':
    regresionLineal()
    exit(0)

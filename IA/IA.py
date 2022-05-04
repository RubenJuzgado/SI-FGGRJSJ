import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
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
    vulnerableTestPredecir = []
    usersPredecirTest = []
    for i in range(int((len(usersClasesDatos) * 0.69))):
        vulnerableTrain.append(usersClasesDatos[i]['vulnerable'])

        usersClasesTrain.append(
            [usersClasesDatos[i]['emails_phishing_recibidos'], usersClasesDatos[i]['emails_phishing_clicados']])

    for i in range(int((len(usersClasesDatos) * 0.69)), len(usersClasesDatos)):
        vulnerableTest.append(usersClasesDatos[i]['vulnerable'])
        usersClasesTest.append(
            [usersClasesDatos[i]['emails_phishing_recibidos'], usersClasesDatos[i]['emails_phishing_clicados']])

    regr = linear_model.LinearRegression()
    regr.fit(usersClasesTrain, vulnerableTrain)
    usersClases_pred = regr.predict(usersClasesTest)
    porcentajeClickados = []
    coefDeter = r2_score(vulnerableTest, usersClases_pred)
    for i in range(len(usersClasesTest)):
        if usersClasesTest[i][0] != 0:
            data = usersClasesTest[i][1] / usersClasesTest[i][0]
            porcentajeClickados.append(data)
        else:
            porcentajeClickados.append(0)
    plt.scatter(porcentajeClickados, vulnerableTest)
    plt.plot(np.array(porcentajeClickados) * coefDeter + regr.intercept_, porcentajeClickados)
    plt.show()

    for i in range(len(usersClases_pred)):
        if usersClases_pred[i] >= 0.65:
            usersClases_pred[i] = 1
        else:
            usersClases_pred[i] = 0
    accuracy = accuracy_score(vulnerableTest, usersClases_pred)
    # Predicciones
    with open('static/users_IA_clases.json') as json_file:
        usersPredecirDatos = json.load(json_file)
    usersPredecirDatos = usersPredecirDatos['usuarios']
    usersPredecirTest = []
    porcentajeClickadosPredecir = []
    for i in range(int(len(usersClasesDatos))):
        usersPredecirTest.append(
            [usersPredecirDatos[i]['emails_phishing_recibidos'], usersPredecirDatos[i]['emails_phishing_clicados']])

    for i in range(len(usersPredecirTest)):
        if usersPredecirTest[i][0] != 0:
            data = usersPredecirTest[i][1] / usersPredecirTest[i][0]
            porcentajeClickadosPredecir.append(data)
        else:
            porcentajeClickadosPredecir.append(0)
    for i in range(len(porcentajeClickadosPredecir)):
        if porcentajeClickadosPredecir[i] >= 0.65:
            porcentajeClickadosPredecir[i] = 1
        else:
            porcentajeClickadosPredecir[i] = 0
    usersPredecir_pred = regr.predict(usersPredecirTest)
    contVuln = 0
    contNoVuln= 0
    for i in range(len(usersPredecir_pred)):
        if usersPredecir_pred[i] >= 0.628:
            usersPredecir_pred[i] = 1
            contVuln = 1+contVuln

        else:
            usersPredecir_pred[i] = 0
            contNoVuln = 1+contNoVuln

    accuracy2 = accuracy_score(porcentajeClickadosPredecir, usersPredecir_pred)
    print("Usuarios vulnerables: "+str(contVuln))
    print("Usuarios NO vulnerables: " + str(contNoVuln))
    print("El accuracy es de:" + str(accuracy2))


if __name__ == '__main__':
    regresionLineal()
    exit(0)

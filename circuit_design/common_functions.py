import numpy as np
import matplotlib.pyplot as plt
import time
import pandas as pd
from scipy.interpolate import interp1d, CubicSpline
from sklearn.linear_model import LinearRegression

def numerical_derivative(x, y):
    dy = np.diff(y)  # Differences in y
    dx = np.diff(x)  # Differences in x
    return dy / dx  # Deriva


def extract_vth(vgs, gm):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    name = f"temp/output_{timestamp}"
    dgm = numerical_derivative(vgs, gm)

    n = 5
    ind = np.argsort(dgm)[::-1]
    model = LinearRegression()
    model.fit(vgs[ind[0]:ind[n]].reshape(-1, 1), gm[ind[0]:ind[n]].reshape(-1, 1))
    y_pred = model.predict(vgs[10:30].reshape(-1, 1))

    m = model.coef_[0]
    b = model.intercept_
    vth = -b / m

    plt.plot(vgs, gm, '*-')
    plt.plot(vgs[1::], dgm)
    plt.plot(vgs[10:30], y_pred)
    plt.plot(vth, 0, 'o')
    plt.savefig(name)

    return vth


def get_intersection(array1, array2, vgs):
    i = np.where(np.isclose(vgs, np.argmin(abs(array1 - array2))))
    return i, vgs[i]

def interpolate_array(x, y, y_value):
    f = CubicSpline(x, y)
    x_dense = np.linspace(0, 0.8, 1000)
    y_dense = f(x_dense)
    i = np.argmin(abs(y_dense - y_value))
    return x_dense[i]

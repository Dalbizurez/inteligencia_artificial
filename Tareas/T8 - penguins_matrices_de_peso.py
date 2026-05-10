import math
import numpy as np
import pandas as pd
from palmerpenguins import load_penguins

# Pega aquí los valores copiados del clipboard
W1 = np.array([[0.994504832479491,-1.54589432835614]
,[5.50395328730678,1.22031847485559]
,[-4.14907787942151,2.09765842247415]
,[-0.22236776729244,-2.38305672866946]
,[-1.002708990102,-3.9667346501893]
 ]) 
W2 = np.array([[ -3.07897850071029,2.21595888731438,-4.13454638775842],
[-5.66484379420109,-10.1912209666941,2.28427497075935],
[41.4589101828923,0.818649792054917,3.7415117247817]
 ]) 
W3 = np.array([[-7.82366579810457,13.7475579482544,-8.99483384055837]
,[5.68542701471266,-41.6457462557179,7.53173978445283]
,[37.3929029746157,-27.7679769734458,-33.8525985109122]
,[-19.4604907284182,-19.4082176309188,24.5023248252864]
 ]) 

def f_act(X):
    return np.array([1/(1 + np.exp(-x)) for x in X], dtype=np.float64)

# Cargar penguins y limpiar NA
penguins = load_penguins()
penguins = penguins.dropna(subset=['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g'])

especie = ['Adelie', 'Gentoo', 'Chinstrap']

xcols = ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']
X = penguins[xcols].copy()

# Normalizar igual que en R (escala z)
X = (X - X.mean()) / X.std()

X.insert(0, 'bias', 1)

# Prediccion
prediccion = []

for index, fila in X.iterrows():
    capa1 = f_act(fila.dot(W1))
    capa1 = np.insert(capa1, 0, 1)

    capa2 = f_act(capa1.dot(W2))
    capa2 = np.insert(capa2, 0, 1)

    salida = f_act(capa2.dot(W3))
    prediccion.append(especie[np.argmax(salida)])

penguins['Prediccion'] = prediccion

erroneas = penguins[penguins['species'] != penguins['Prediccion']]
print(erroneas)

eficiencia = (1 - len(erroneas) / len(penguins)) * 100
print(f"Eficiencia: {eficiencia:.2f}%")
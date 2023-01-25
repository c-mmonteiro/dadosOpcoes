import pandas as pd
import matplotlib.pyplot as plt

from keras.models import Sequential
from keras.layers import Dense
import numpy as np
from keras.models import load_model

dados = pd.read_csv('2023_01_20_10dias_CALL_EU_v2.csv')
dados.head()

dados.drop(["Idx"], axis=1, inplace=True)

print(dados)

#print(dados["Strike", "Premio", "Tempo de Vida"].values.tolist())

X = np.array(dados[["Strike", "Tempo de Vida", "Preco Acao"]].values.tolist())
y = np.array(dados["Premio"].values.tolist())



# Criação do modelo
model = Sequential()
model.add(Dense(64, input_dim=3, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(16, activation='relu'))
model.add(Dense(1, activation='linear'))

# Compilação do modelo
model.compile(loss='mean_squared_error', optimizer='adam')

# Função de treinamento
def train(X, y):
    model.fit(X, y, epochs=100, batch_size=32)
    model.save('model.h5')

# Função de uso
def predict(X):
    model = load_model('model.h5')
    return model.predict(X)

# exemplo de uso


#train(X, y)

strike_test = np.array(list(range(60, 160, 1)))/4

y_out = []

for s in strike_test:
    X_test = np.array([[s, 24, 26.6]])
    y_test = predict(X_test)
    y_out.append(y_test[0][0])


plt.plot(strike_test, y_out)
plt.grid()

plt.show()


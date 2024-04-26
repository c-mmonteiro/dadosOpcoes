import pandas as pd
import matplotlib.pyplot as plt

dados = pd.read_csv('2023_01_20_10dias_CALL_EU_v2.csv')


dados.head()


strike = dados['Preco Acao'].to_list()
strike = list(dict.fromkeys(strike))
strike.sort()

vida = dados['Tempo de Vida'].to_list()
vida = list(dict.fromkeys(vida))
vida.sort()

for s in strike:
    aux1 = dados[dados['Preco Acao'] == s]
    for v in vida:
        aux2 = aux1[aux1['Tempo de Vida'] == v]
        if len(aux2) > 0:
            plt.plot(aux2['Strike'], aux2['Premio'])

plt.show()



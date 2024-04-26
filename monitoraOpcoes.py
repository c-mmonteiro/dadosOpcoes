import pandas as pd

import plotly.express as px

import MetaTrader5 as mt5

import time
import pytz

import numpy as np
from keras.models import load_model

from blackScholes.bs import *

class monitoraOpcoes:
    def __init__(self, min_strike, max_strike):
        self.ativo = "PETR4"
        self.selic = (((1 + 0.1375) ** (1 / 12)) - 1)

        self.timezone = pytz.timezone('America/Sao_Paulo')
        self.validade = pd.datetime(2023, 3, 17)#, tzinfo=self.timezone)
        self.hoje = pd.datetime(2023, 2, 24) #pd.datetime.today()

        self.dias_restante = self.validade - self.hoje


        self.min_strike = min_strike
        self.max_strike = max_strike

        self.opcoes = pd.DataFrame(columns=['Codigo', 'Strike'])

        self.model = load_model('model.h5')

        mt5.initialize()

        if (not mt5.symbol_select(self.ativo, True)):
            print(f'ALERTA: O ativo {self.ativo} não pode ser adicionado!')
        else:
            lista_simbolos_completa = mt5.symbols_get(self.ativo[0:4])
        
        for symb in lista_simbolos_completa:
            papel = symb.name

            if (not mt5.symbol_select(papel, True)):
                print(f'ALERTA: O ativo {papel} não pode ser adicionado!')
            else:
                papel_info = mt5.symbol_info(papel)

                papel_validade = pd.to_datetime(papel_info.expiration_time, unit='s') - self.hoje



                if ((papel_info.basis == self.ativo) and 
                (papel_info.option_strike > self.min_strike) and 
                (papel_info.option_strike < self.max_strike) and
                (papel_validade.days == self.dias_restante.days) and
                (papel_info.option_right == 0) and (papel_info.option_mode == 0)):
                    self.opcoes = self.opcoes.append(
                                        {"Codigo": papel,
                                        "Strike": papel_info.option_strike}, ignore_index=True)
            mt5.symbol_select(papel, False)
        mt5.shutdown()

        self.opcoes = self.opcoes.sort_values(by="Strike")
        self.opcoes = self.opcoes.reset_index()
        self.opcoes.drop(['index'], axis=1, inplace=True)



    def atualiza(self):

        self.premio = pd.DataFrame(columns=['Codigo', 'Strike', 'Ultimo', 'Compra', 'Venda', 'IA', 'VolImp'])

        mt5.initialize()

        mt5.symbol_select(self.ativo, True)
        time.sleep(1)

        tick_base = mt5.symbol_info_tick(self.ativo)

        mt5.symbol_select(self.ativo, False)

        for idx, op in enumerate(self.opcoes['Codigo']):
            if (not mt5.symbol_select(op, True)):
                print(f'ALERTA: O ativo {self.ativo} não pode ser adicionado!')
            else:
                X_test = np.array([[self.opcoes['Strike'][idx], self.dias_restante.days, tick_base.last]])
                y_test = self.model.predict(X_test)

                vol = bs().call_implied_volatility(y_test, tick_base.last, self.opcoes['Strike'][idx], self.dias_restante.days/365, self.selic)

                tick_opcao = mt5.symbol_info_tick(op)

                self.premio = self.premio.append(
                                        {"Codigo": self.opcoes['Codigo'][idx],
                                        "Strike": self.opcoes['Strike'][idx],
                                        "Ultimo": tick_opcao.last,
                                        "Compra": tick_opcao.bid,
                                        "Venda": tick_opcao.ask,
                                        "IA": y_test[0][0],
                                        "VolImp": vol}, ignore_index=True)
            mt5.symbol_select(op, False) 

        #resultado = pd.merge(self.opcoes, self.premio, left_index = True, right_index = True, how = "inner")
        resultado = self.premio

        probabilidade = pd.DataFrame(columns=['Strike', 'Probabilidade'])

        for idx, aux in enumerate(resultado['Strike']):
            if not (idx == len(resultado) - 1):
                v2 = (resultado['VolImp'][idx] + resultado['VolImp'][idx + 1]) / 2

                s2 = (resultado['Strike'][idx] + resultado['Strike'][idx + 1]) / 2
                s = abs(resultado['Strike'][idx] - resultado['Strike'][idx + 1]) / 2
                c2 = round(bs().bs_call(tick_base.last, s2, self.dias_restante.days/365, self.selic, v2), 3)

                g = exp(self.selic * (self.dias_restante.days/365)) * (resultado['IA'][idx] + resultado['IA'][idx + 1] - 2 * c2) / (s ** 2)

                probabilidade = probabilidade.append(
                    {"Strike": s2, "Probabilidade": abs(g)}, ignore_index=True)
        print('Finalizou')

        return resultado, tick_base.last, probabilidade


        #plt.plot([tick_base.last, tick_base.last], [self.premio.min(), self.premio.max()])
        
        #plt.plot(self.opcoes['Strike'], self.premio['Ultimo'], label='Ultimo', color='blue')
        #plt.plot(self.opcoes['Strike'], self.premio['Compra'], label='Compra', color='green')
        #plt.plot(self.opcoes['Strike'], self.premio['Venda'], label='Venda', color='red')
        #plt.plot(self.opcoes['Strike'], self.premio['IA'], label='Calculado', color='black')
        #plt.grid()
        #plt.legend()
        #plt.show()






        


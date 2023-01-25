import pandas as pd

import plotly.express as px

import MetaTrader5 as mt5

import time
import pytz

import numpy as np
from keras.models import load_model

class monitoraOpcoes:
    def __init__(self, min_strike, max_strike):
        self.ativo = "PETR4"

        self.timezone = pytz.timezone('America/Sao_Paulo')
        self.validade = pd.datetime(2023, 2, 17)#, tzinfo=self.timezone)
        self.hoje = pd.datetime(2023, 1, 25) #pd.datetime.today()

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

        self.premio = pd.DataFrame(columns=['Ultimo', 'Compra', 'Venda', 'IA'])

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

                tick_opcao = mt5.symbol_info_tick(op)

                self.premio = self.premio.append(
                                        {"Ultimo": tick_opcao.last,
                                        "Compra": tick_opcao.bid,
                                        "Venda": tick_opcao.ask,
                                        "IA": y_test[0][0]}, ignore_index=True)
            mt5.symbol_select(op, False) 

        resultado = pd.merge(self.opcoes, self.premio, left_index = True, right_index = True, how = "inner")

        return resultado, tick_base.last


        #plt.plot([tick_base.last, tick_base.last], [self.premio.min(), self.premio.max()])
        
        #plt.plot(self.opcoes['Strike'], self.premio['Ultimo'], label='Ultimo', color='blue')
        #plt.plot(self.opcoes['Strike'], self.premio['Compra'], label='Compra', color='green')
        #plt.plot(self.opcoes['Strike'], self.premio['Venda'], label='Venda', color='red')
        #plt.plot(self.opcoes['Strike'], self.premio['IA'], label='Calculado', color='black')
        #plt.grid()
        #plt.legend()
        #plt.show()






        


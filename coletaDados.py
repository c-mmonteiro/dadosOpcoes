import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

import matplotlib.pyplot as plt

class dadosOpcoes:
    def __init__(self, ativo) -> None:

        self.ativo = ativo

        self.timezone = pytz.timezone('America/Sao_Paulo')
        self.hoje = datetime.today()


        utc_from = datetime(2023, 1, 11, tzinfo=self.timezone)
        utc_to = datetime(2023, 1, 21, tzinfo=self.timezone)

        #Pegar apenas CALL Européia
        self.opcoes = pd.DataFrame(columns=['Strike', 'Premio', 'Tempo de Vida', 'Preco Acao'])

        mt5.initialize()

        if (not mt5.market_book_add(self.ativo)):
            print(f'ALERTA: O ativo {self.ativo} não pode ser adicionado!')
        else:
            time.sleep(0.1)                            
            ticks_base = mt5.copy_ticks_range(self.ativo, utc_from, utc_to, mt5.COPY_TICKS_TRADE)

            ticks_base_frame = pd.DataFrame(ticks_base)

            mt5.market_book_release(self.ativo)

        self.listaSimbolos = mt5.symbols_get(self.ativo[0:4])

        num_symb = len(self.listaSimbolos)

        for idx_symb, symb in enumerate(self.listaSimbolos):

            papel = symb.name
            print(f'{papel}: {idx_symb} de {num_symb}')

            if (not mt5.market_book_add(papel)):
                print(f'ALERTA: O ativo {papel} não pode ser adicionado!')
            else:
                papel_info = mt5.symbol_info(papel)

                base = papel_info.basis

                if ((base == self.ativo) and (papel_info.option_strike > 0) and 
                (papel_info.option_right == 0) and (papel_info.option_mode == 0)):
                    
                    ticks = mt5.copy_ticks_range(papel, utc_from, utc_to, mt5.COPY_TICKS_TRADE)
                    # create DataFrame out of the obtained data
                    ticks_frame = pd.DataFrame(ticks)

                    ticks_frame = ticks_frame[ticks_frame['last'] > 0]  

                    for idx, tick_time in enumerate(ticks_frame['time']):

                        sub = 0
                        while True:
                            tick_base = ticks_base_frame[ticks_base_frame['time'] == tick_time - sub]

                            if len(tick_base) > 0:
                                break
                            elif (sub < 20):
                                sub = sub + 1
                            else:
                                break
                        if (sub != 20):

                            vencimento = pd.to_datetime(papel_info.expiration_time, unit='s') - pd.to_datetime(ticks_frame.loc[ticks_frame.iloc[idx].name]['time'], unit='s')

                            self.opcoes = self.opcoes.append(
                                        {"Strike": papel_info.option_strike, "Premio": ticks_frame.loc[ticks_frame.iloc[idx].name]['last'],
                                        "Tempo de Vida": vencimento.days, "Preco Acao": tick_base['last'].to_list()[0]}, ignore_index=True)
                        else:
                            print(f'ALERTA: Problema na cotação do ativo base.')
                   
            print(len(self.opcoes))
        mt5.shutdown()

        self.opcoes.to_csv('2023_01_20_10dias_CALL_EU_v2.csv')

            

dadosOpcoes('PETR4')
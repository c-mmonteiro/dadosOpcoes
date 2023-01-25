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

        self.listaSimbolos = mt5.symbols_get(self.ativo[0:4])

        num_symb = len(self.listaSimbolos)

        for idx_symb, symb in enumerate(self.listaSimbolos):

            papel = symb.name
            print(f'{papel}: {idx_symb} de {num_symb}')

            if (not mt5.market_book_add(papel)):
                print(f'ALERTA: O ativo {papel} não pode ser adicionado!')
            else:
                papel_info = mt5.symbol_info(papel)

                if ((papel_info.option_strike > 0) and (papel_info.option_right == 0) and (papel_info.option_mode == 0)):
                    
                    ticks = mt5.copy_ticks_range(papel, utc_from, utc_to, mt5.COPY_TICKS_ALL)
                    # create DataFrame out of the obtained data
                    ticks_frame = pd.DataFrame(ticks)
                    # convert time in seconds into the datetime format
                    ticks_frame['time']=pd.to_datetime(ticks_frame['time'], unit='s')

                    ticks_frame = ticks_frame[ticks_frame['last'] > 0]

                    

                    base = papel_info.basis

                    mt5.market_book_release(papel)

                    if (not mt5.market_book_add(base)):
                        print(f'ALERTA: O ativo {base} não pode ser adicionado!')
                    else:
                        time.sleep(0.1)
                        for idx, tick_time in enumerate(ticks_frame['time']):
                            
                            tick_base = mt5.copy_ticks_from(base, tick_time, 1, mt5.COPY_TICKS_ALL)

                            vencimento = pd.to_datetime(papel_info.expiration_time, unit='s') - ticks_frame.loc[ticks_frame.iloc[idx].name]['time'] 

                            self.opcoes = self.opcoes.append(
                                        {"Strike": papel_info.option_strike, "Premio": ticks_frame.loc[ticks_frame.iloc[idx].name]['last'],
                                        "Tempo de Vida": vencimento.days, "Preco Acao": tick_base[0]['last']}, ignore_index=True)


                            tick_base_frame = pd.DataFrame(tick_base)
                            if idx == 0:
                                ticks_base_frame = tick_base_frame
                            else:
                                ticks_base_frame = pd.concat([ticks_base_frame, tick_base_frame])

                        # convert time in seconds into the datetime format
                        ticks_base_frame['time']=pd.to_datetime(ticks_base_frame['time'], unit='s')

                        mt5.market_book_release(base)

                        self.opcoes = self.opcoes.drop_duplicates()
            print(len(self.opcoes))
        mt5.shutdown()

        self.opcoes.to_csv('2023_01_20_10dias_CALL_EU.csv')

            

dadosOpcoes('PETR4')
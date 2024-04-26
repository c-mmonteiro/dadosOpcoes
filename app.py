# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, State, ctx
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd

from datetime import datetime

from monitoraOpcoes import *


app = Dash(__name__)

monitor = monitoraOpcoes(24.5,28)
dados, base_last, prob = monitor.atualiza()

fig = make_subplots(rows=1, cols=1, subplot_titles=('Plot 1'))
fig.add_trace(go.Line(x=dados["Strike"], y=dados["IA"], name="IA", line=dict(color='black')))
fig.add_trace(go.Line(x=dados["Strike"], y=dados["Compra"], name="Compra", line=dict(color='red')))
fig.add_trace(go.Line(x=dados["Strike"], y=dados["Venda"], name="Venda", line=dict(color='green')))
fig.add_trace(go.Line(x=dados["Strike"], y=dados["Ultimo"], name="Ultimo", line=dict(color='blue')))
#Monta a string de data
now = datetime.now()
date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
#Monta o grafico de volatilidade
fig_vol = make_subplots(rows=1, cols=1, subplot_titles=('Volatilidade'))
fig_vol.add_trace(go.Line(x=dados["Strike"], y=dados["VolImp"]))
#Monta o grafico de probbilidade
fig_prob = make_subplots(rows=1, cols=1, subplot_titles=('Probabilidade'))
fig_prob.add_trace(go.Line(x=prob["Strike"], y=prob["Probabilidade"]))

app.layout = html.Div(children=[
    html.Div(children=[
        html.Div(children=['Valor minimo do Strike:']),
        dcc.Textarea(
            id='textarea-min-strike',
            value='24.5',
            style={'width': '100%', 'height': 20},
        ),
        html.Div(children=['Valor máximo do Strike:']),
        dcc.Textarea(
            id='textarea-max-strike',
            value='28',
            style={'width': '100%', 'height': 20},
        ),
        html.Button('Submit', id='button', n_clicks=0)
    ]),
    dcc.Graph(
        id='example-graph',
        figure=fig
    ),
    html.Div(
        id='div-hora',
        children=[date_time]
    ),
    dcc.Graph(
        id='prob-graph',
        figure = fig_prob
    ),
    dcc.Graph(
        id='vol-graph',
        figure = fig_vol
    ),
    dcc.Interval(
        id='interval-component',
        interval=30*1000, # in milliseconds
        n_intervals=0
    )
])


@app.callback(
    Output('example-graph', 'figure'),
    Output('div-hora', 'children'),
    Output('prob-graph', 'figure'),
    Output('vol-graph', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('button', 'n_clicks'),
    State('textarea-min-strike', 'value'),
    State('textarea-max-strike', 'value')
)
def interval_update(intervalo, n_click, min, max):

    global monitor

    trig = ctx.triggered_id

    if trig == 'button':
        monitor = monitoraOpcoes(float(min),float(max))
    #Atualiza os dados
    dados, base_last, prob = monitor.atualiza()
    #Monta a figura de preços
    fig = make_subplots(rows=1, cols=1, subplot_titles=('Preço'))
    fig.add_trace(go.Line(x=dados["Strike"], y=dados["Compra"], name="Compra", line=dict(color='red')))
    fig.add_trace(go.Line(x=dados["Strike"], y=dados["Ultimo"], name="Ultimo", line=dict(color='blue')))
    fig.add_trace(go.Line(x=[base_last, base_last], y=[dados["IA"].min(), dados["IA"].max()] , name="Ativo", line=dict(color='red')))
    fig.add_trace(go.Line(x=dados["Strike"], y=dados["IA"], name="IA", line=dict(color='black')))
    fig.add_trace(go.Line(x=dados["Strike"], y=dados["Venda"], name="Venda", line=dict(color='green')))
    #Monta a string de data
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
    #Monta o grafico de volatilidade
    fig_vol = make_subplots(rows=1, cols=1, subplot_titles=('Volatilidade'))
    fig_vol.add_trace(go.Line(x=dados["Strike"], y=dados["VolImp"]))
    #Monta o grafico de probbilidade
    fig_prob = make_subplots(rows=1, cols=1, subplot_titles=('Probabilidade'))
    fig_prob.add_trace(go.Line(x=prob["Strike"], y=prob["Probabilidade"]))
    
    return fig, date_time, fig_prob, fig_vol




if __name__ == '__main__':
    app.run_server(debug=True)
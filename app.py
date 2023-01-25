# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd

from monitoraOpcoes import *

app = Dash(__name__)

monitor = monitoraOpcoes(26,28)
dados, base_last = monitor.atualiza()

fig = make_subplots(rows=1, cols=1, subplot_titles=('Plot 1'))
fig.add_trace(go.Line(x=dados["Strike"], y=dados["IA"], name="IA", line=dict(color='black')))
fig.add_trace(go.Line(x=dados["Strike"], y=dados["Compra"], name="Compra", line=dict(color='red')))
fig.add_trace(go.Line(x=dados["Strike"], y=dados["Venda"], name="Venda", line=dict(color='green')))
fig.add_trace(go.Line(x=dados["Strike"], y=dados["Ultimo"], name="Ultimo", line=dict(color='blue')))

app.layout = html.Div(children=[
    dcc.Graph(
        id='example-graph',
        figure=fig
    ),
    dcc.Interval(
        id='interval-component',
        interval=20*1000, # in milliseconds
        n_intervals=0
    )
])


@app.callback(
    Output('example-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def interval_update(intervalo):
    dados, base_last = monitor.atualiza()
    fig = make_subplots(rows=1, cols=1, subplot_titles=('Plot 1'))
    fig.add_trace(go.Line(x=dados["Strike"], y=dados["IA"], name="IA", line=dict(color='black')))
    fig.add_trace(go.Line(x=dados["Strike"], y=dados["Compra"], name="Compra", line=dict(color='red')))
    fig.add_trace(go.Line(x=dados["Strike"], y=dados["Venda"], name="Venda", line=dict(color='green')))
    fig.add_trace(go.Line(x=dados["Strike"], y=dados["Ultimo"], name="Ultimo", line=dict(color='blue')))
    fig.add_trace(go.Line(x=[base_last, base_last], y=[dados["IA"].min(), dados["IA"].max()] , name="Ativo", line=dict(color='red')))
    return fig



if __name__ == '__main__':
    app.run_server(debug=True)
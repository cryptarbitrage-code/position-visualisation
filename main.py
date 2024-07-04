import plotly.graph_objs as go
from dash import Dash, dcc, html
import pandas as pd

app = Dash(__name__)

# Sample data
data = {
    'date': ['2021-07-01', '2021-07-02', '2021-07-03', '2021-07-04', '2021-07-05'],
    'open': [100, 105, 103, 108, 107],
    'high': [110, 115, 113, 118, 117],
    'low': [90, 95, 93, 98, 97],
    'close': [105, 103, 108, 107, 110]
}

# Create the candlestick chart
fig = go.Figure(data=[go.Candlestick(x=data['date'],
                                     open=data['open'],
                                     high=data['high'],
                                     low=data['low'],
                                     close=data['close'])])

# Example option positions with dates beyond the last candle date
positions = [
    {'date': '2021-07-06', 'type': 'call', 'action': 'long', 'price': 112},
    {'date': '2021-07-07', 'type': 'put', 'action': 'long', 'price': 105},
    {'date': '2021-07-08', 'type': 'call', 'action': 'sell', 'price': 115},
    {'date': '2021-07-09', 'type': 'put', 'action': 'sell', 'price': 108}
]

# Add arrows or triangles for each position
for pos in positions:
    arrow_color = 'green' if pos['action'] == 'long' else 'red'
    y_offset = 5 if pos['type'] == 'call' else -5
    symbol = 'triangle-up' if pos['type'] == 'call' else 'triangle-down'
    fig.add_trace(go.Scatter(
        x=[pos['date']],
        y=[pos['price']],
        mode='markers',  # markers+text to include text
        marker=dict(
            symbol=symbol,
            color=arrow_color,
            size=12
        ),
        # text=pos['type'].capitalize(),
        textposition="top center"
    ))

# Adjust layout settings
fig.update_layout(
    title='Candlestick Chart with Option Positions',
    xaxis_title='Date',
    yaxis_title='Price'
)

app.layout = html.Div(children=[
    dcc.Graph(id='candlestick-chart', figure=fig)
])

if __name__ == '__main__':
    app.run_server(debug=True)

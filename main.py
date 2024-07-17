import plotly.graph_objs as go
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
from api_functions import get_tradingview_chart_data, get_positions
from datetime import datetime, timedelta

pd.set_option('display.max_columns', None)  # useful for testing

# --- GET CANDLE DATA --- #
instrument = "BTC-PERPETUAL"
resolution = 1440  # resolution in minutes
end_time = datetime.now()
start_time = end_time - timedelta(minutes=60 * resolution)

# Convert start_timestamp and end_timestamp to unix time in milliseconds
start_timestamp = int(start_time.timestamp() * 1000)
end_timestamp = int(end_time.timestamp() * 1000)

candle_data = get_tradingview_chart_data(instrument, start_timestamp, end_timestamp, resolution)
df_candle = pd.DataFrame(candle_data)
df_candle = df_candle[['ticks', 'open', 'high', 'low', 'close']]
df_candle['date'] = pd.to_datetime(df_candle['ticks'], unit='ms')

# --- GET POSITION DATA --- #
positions = get_positions()

columns_to_keep = [
    'average_price_usd', 'total_profit_loss', 'average_price', 'theta', 'delta', 'vega',
    'instrument_name', 'mark_price', 'direction', 'size', 'kind', 'index_price'
]
positions = positions[columns_to_keep]

option_positions = positions[positions['kind'] == "option"].copy()
option_positions[['currency', 'expiry', 'strike', 'type']] = option_positions['instrument_name'].str.split('-', expand=True)
option_positions = option_positions[option_positions['currency'] == "BTC"]
option_positions['strike'] = option_positions['strike'].astype(float)
option_positions['expiry_date'] = pd.to_datetime(option_positions['expiry'], format='%d%b%y')
option_positions['expiry_date'] = option_positions['expiry_date'] + pd.Timedelta(hours=8)
option_positions = option_positions.sort_values(by='expiry_date')

print(option_positions)

app = Dash(title="Position Visualisation", external_stylesheets=[dbc.themes.DARKLY])

# Create the candlestick chart
fig = go.Figure(
    data=[go.Candlestick(
        x=df_candle['date'],
        open=df_candle['open'],
        high=df_candle['high'],
        low=df_candle['low'],
        close=df_candle['close'],
        name=instrument,
    )],
)

# Add arrows for each position
for index, pos in option_positions.iterrows():
    arrow_color = 'green' if pos['direction'] == 'buy' else 'red'
    y_offset = 5 if pos['type'] == 'C' else -5
    symbol = 'triangle-up' if pos['type'] == 'C' else 'triangle-down'
    fig.add_trace(go.Scatter(
        x=[pos['expiry_date']],
        y=[pos['strike']],
        mode='markers+text',  # markers+text to include text
        marker=dict(
            symbol=symbol,
            color=arrow_color,
            size=8
        ),
        text=pos['size'],
        textposition="top center",
        textfont=dict(size=8),
        name=pos['instrument_name'],
    ))

# Adjust layout settings
fig.update_layout(
    template='plotly_dark',
    title='Candlestick Chart with Option Positions',
    xaxis_title='Date',
    yaxis_title='Price',
    xaxis_rangeslider_visible=False,
    height=800
)

app.layout = html.Div(children=[
    dcc.Graph(id='candlestick-chart', figure=fig)
])

if __name__ == '__main__':
    app.run_server(debug=True)

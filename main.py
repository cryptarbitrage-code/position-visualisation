import plotly.graph_objs as go
from dash import Dash, dcc, html
import pandas as pd
from api_functions import get_tradingview_chart_data, get_positions
from datetime import datetime, timedelta

pd.set_option('display.max_columns', None)  # useful for testing

# --- GET CANDLE DATA --- #
instrument = "BTC-PERPETUAL"
resolution = 720  # resolution in minutes
end_time = datetime.now()
start_time = end_time - timedelta(minutes=20 * resolution)

# Convert start_timestamp and end_timestamp to unix time in milliseconds
start_timestamp = int(start_time.timestamp() * 1000)
end_timestamp = int(end_time.timestamp() * 1000)

candle_data = get_tradingview_chart_data(instrument, start_timestamp, end_timestamp, resolution)
df_candle = pd.DataFrame(candle_data)
print(df_candle)
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

### need to create column for expiry_date

print(option_positions)

app = Dash(__name__)

# Create the candlestick chart
fig = go.Figure(data=[go.Candlestick(x=df_candle['date'],
                                     open=df_candle['open'],
                                     high=df_candle['high'],
                                     low=df_candle['low'],
                                     close=df_candle['close'])])

# Add arrows for each position
for index, pos in option_positions.iterrows():
    arrow_color = 'green' if pos['direction'] == 'buy' else 'red'
    y_offset = 5 if pos['type'] == 'C' else -5
    symbol = 'triangle-up' if pos['type'] == 'C' else 'triangle-down'
    fig.add_trace(go.Scatter(
        x=[pos['expiry_date']],
        y=[pos['strike']],
        mode='markers',  # markers+text to include text
        marker=dict(
            symbol=symbol,
            color=arrow_color,
            size=12
        ),
        # text=pos['type'].capitalize(),
        # textposition="top center"
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

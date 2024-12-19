import dash
from dash import dcc, html
import plotly.graph_objects as go

def render_tab3(df):
    layout = html.Div([
        html.H1('Kanały sprzedaży', style={'text-align': 'center'}),
        html.Div([
            dcc.Dropdown(
                id='store-type-dropdown',
                options=[{'label': store, 'value': store} for store in df['Store_type'].unique()],
                value=df['Store_type'].unique()[0],
                placeholder='Wybierz kanał sprzedaży'
            )
        ], style={'width': '50%', 'margin': 'auto', 'padding-bottom': '20px'}),
        html.Div([
            html.Div([dcc.Graph(id='weekday-sales')], style={'width': '50%'}),
            html.Div([dcc.Graph(id='customer-demographics')], style={'width': '50%'})
        ], style={'display': 'flex'})
    ])
    return layout

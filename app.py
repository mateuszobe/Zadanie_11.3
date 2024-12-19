import pandas as pd
import datetime as dt
import os
import dash as dcc
import dash as html
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash as dash_auth
import plotly as go
import dash as tab1
import dash as tab2

from dash import dcc, html
from dash.dependencies import Input, Output
import dash
import plotly.graph_objects as go
from data_loading import db
from tab1 import render_tab1
from tab2 import render_tab2
from tab3 import render_tab3

# Wczytanie danych
df = db()
df.merge()

# Layout
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
app.layout = html.Div([
    html.Div([
        dcc.Tabs(
            id='tabs',
            value='tab-1',
            children=[
                dcc.Tab(label='Sprzedaż globalna', value='tab-1'),
                dcc.Tab(label='Produkty', value='tab-2'),
                dcc.Tab(label='Kanały sprzedaży', value='tab-3')
            ]
        ),
        html.Div(id='tabs-content')
    ], style={'width': '80%', 'margin': 'auto'})
], style={'height': '100%'})

# Callback dla zawartości zakładek
@app.callback(Output('tabs-content', 'children'), [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return render_tab1(df.merged)
    elif tab == 'tab-2':
        return render_tab2(df.merged)
    elif tab == 'tab-3':  
        return render_tab3(df.merged)

# Callbacki dla tab-1
@app.callback(Output('bar-sales', 'figure'),
              [Input('sales-range', 'start_date'), Input('sales-range', 'end_date')])
def tab1_bar_sales(start_date, end_date):
    truncated = df.merged[(df.merged['tran_date'] >= start_date) & (df.merged['tran_date'] <= end_date)]
    grouped = truncated[truncated['total_amt'] > 0].groupby(
        [pd.Grouper(key='tran_date', freq='M'), 'Store_type']
    )['total_amt'].sum().round(2).unstack()

    traces = []
    for col in grouped.columns:
        traces.append(go.Bar(
            x=grouped.index, y=grouped[col], name=col, hoverinfo='text',
            hovertext=[f'{y/1e3:.2f}k' for y in grouped[col].values]
        ))

    fig = go.Figure(data=traces, layout=go.Layout(title='Przychody', barmode='stack', legend=dict(x=0, y=-0.5)))
    return fig

@app.callback(Output('choropleth-sales', 'figure'),
              [Input('sales-range', 'start_date'), Input('sales-range', 'end_date')])
def tab1_choropleth_sales(start_date, end_date):
    truncated = df.merged[(df.merged['tran_date'] >= start_date) & (df.merged['tran_date'] <= end_date)]
    grouped = truncated[truncated['total_amt'] > 0].groupby('country')['total_amt'].sum().round(2)

    trace0 = go.Choropleth(
        colorscale='Viridis', reversescale=True,
        locations=grouped.index, locationmode='country names',
        z=grouped.values, colorbar=dict(title='Sales')
    )
    fig = go.Figure(data=[trace0], layout=go.Layout(title='Mapa', geo=dict(showframe=False, projection={'type': 'natural earth'})))
    return fig

# Callback dla tab-2
@app.callback(Output('barh-prod-subcat', 'figure'),
              [Input('prod_dropdown', 'value')])
def tab2_barh_prod_subcat(chosen_cat):
    grouped = df.merged[(df.merged['total_amt'] > 0) & (df.merged['prod_cat'] == chosen_cat)].pivot_table(
        index='prod_subcat', columns='Gender', values='total_amt', aggfunc='sum'
    ).assign(_sum=lambda x: x['F'] + x['M']).sort_values(by='_sum').round(2)

    traces = []
    for col in ['F', 'M']:
        traces.append(go.Bar(x=grouped[col], y=grouped.index, orientation='h', name=col))

    fig = go.Figure(data=traces, layout=go.Layout(barmode='stack', margin={'t': 20}))
    return fig

# Callback dla tab-3
@app.callback(Output('weekday-sales', 'figure'),
              [Input('store-type-dropdown', 'value')])
def weekday_sales(store_type):
    filtered = df.merged[df.merged['Store_type'] == store_type]
    filtered['day_of_week'] = filtered['tran_date'].dt.day_name()

    # Tworzenie słownika, który przypisuje dniom tygodnia odpowiednią wartość numeryczną
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    filtered['day_of_week_order'] = filtered['day_of_week'].apply(lambda x: day_order.index(x))

    # Grupowanie po dniu tygodnia i sumowanie sprzedaży
    grouped = filtered.groupby('day_of_week')['total_amt'].sum()

    # Sortowanie dni tygodnia zgodnie z kolejnością
    grouped = grouped.loc[day_order]

    fig = go.Figure(data=[go.Bar(x=grouped.index, y=grouped.values)],
                    layout=go.Layout(title=f'Sprzedaż w dniach tygodnia ({store_type})',
                                     xaxis=dict(title='Dzień tygodnia'),
                                     yaxis=dict(title='Sprzedaż')))
    return fig
@app.callback(Output('customer-demographics', 'figure'),
              [Input('store-type-dropdown', 'value')])
def customer_demographics(store_type):
    filtered = df.merged[df.merged['Store_type'] == store_type]
    gender_counts = filtered['Gender'].value_counts()

    fig = go.Figure(data=[go.Pie(labels=gender_counts.index, values=gender_counts.values)],
                    layout=go.Layout(title=f'Udział płci dla {store_type}'))
    return fig
# Uruchomienie aplikacji
if __name__ == '__main__':
    app.run_server(debug=True)

# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from collections import Counter

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dataPath = './tokens.json'
impWordsPath = './importantWords.txt'
importantWords = open(impWordsPath, "r").read().split(',')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_json(dataPath)
df['counts'] = df['counts'].apply(Counter)
countsByQuarter = df.groupby(by=['quarter'])['counts'].sum()
quarters = countsByQuarter.index

app.layout = html.Div(children=[
    html.H1(children='Deconstruct New Chinese'),

    html.Div(children=[dcc.Markdown('''
    	输入
    	''')]),
    html.Br(),
    html.Div([
    	dcc.Dropdown(
	    	id="select_words", 
	    	options=[{"label": w, "value": w} for w in importantWords],
            value=['改革','稳定'],
            multi=True,
	    	)]),
    dcc.Graph(
        id='timeseries',
        figure={}
    )
])

@app.callback(
    Output(component_id="timeseries", component_property="figure"),
    [Input(component_id='select_words', component_property='value')],
)
def generateTimeSeries(words):
	trends = pd.DataFrame()
	for w in words:
		trends[w] = countsByQuarter.apply(lambda x: x[w] if w in x else 0)

	fig = go.Figure()

	for w in words:
		trend = countsByQuarter.apply(lambda x: x[w] if w in x else 0)
		fig.add_trace(go.Scatter(x=quarters, y=trend, mode='lines', name=w, connectgaps=True))
		fig.add_trace(go.Scatter( x=[countsByQuarter.index[0], countsByQuarter.index[-1]], y=[trend[0], trend[-1]], mode='markers'))

	fig.update_layout(
	    xaxis=dict(
	        showline=True,
	        showgrid=False,
	        showticklabels=True,
	        linecolor='rgb(204, 204, 204)',
	        linewidth=2,
	        ticks='outside',
	        tickfont=dict(
	            family='Arial',
	            size=12,
	            color='rgb(82, 82, 82)',
	        ),
	    ),
	    yaxis=dict(
	        showgrid=False,
	        zeroline=False,
	        showline=False,
	        showticklabels=False,
	    ),
	    autosize=False,
	    margin=dict(
	        autoexpand=False,
	        l=100,
	        r=20,
	        t=110,
	    ),
	    showlegend=False,
	    plot_bgcolor='white'
	)


	return fig

if __name__ == "__main__":
    app.run_server(port=8000, host='127.0.0.1', debug=True)
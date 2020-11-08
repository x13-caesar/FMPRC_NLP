# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud, STOPWORDS 
import matplotlib.pyplot as plt
from collections import Counter



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dataPath = './tokens.json'
wordcloudFont = 'HuaWenZhongSong-1.ttf'

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_json(dataPath)


## 获取quarter数值
def m2q(month):
    month = int(month)
    if month<=3: q = 1
    elif month<=6: q = 2
    elif month<=9: q = 3
    else: q = 4
    return q

df['counts'] = df['counts'].map(Counter)
df['quarter'] = df['year'].map(str)+'Q'+df['month'].apply(m2q).map(str)
df['year-month'] = df['year'].map(str)+df['month'].map(str)

countsByQuarter = df.groupby(by=['quarter'])['counts'].sum()


app.layout = html.Div(children=[
    html.H1(children='Deconstruct New Chinese'),

    html.Div(children='''
        The Top Frequent Word in the Speechs of Minister for Foreign Affairs of China.
    '''),
    html.Br(),
    html.Div([
    	dcc.Dropdown(
	    	id="select_year", 
	    	options=[{"label": str(year), "value": int(year)} for year in range(2012, 2021)],
	    	placeholder="Select a year",
            value=2020,
	    	style={'width': '40%'}
	    	),
    	dcc.Dropdown(
    		id='select_quarter',
    		options=[{"label":'Q'+str(n), "value": n} for n in range(1,5)],
    		placeholder="Select a quarter",
            value=2,
    		style={'width': '40%'}
    		)
    	]),
    dcc.Graph(
        id='wordcloud',
        figure={}
    ) 
])


@app.callback(
    Output(component_id='wordcloud', component_property='figure'),
    [Input(component_id='select_year', component_property='value'),
    Input(component_id='select_quarter', component_property='value')]
)
def update_output_div(year, quarter):
    time = str(year)+'Q'+str(quarter)
    wordcloud = WordCloud(font_path = wordcloudFont, 
        width = 300, height = 400, 
        background_color ='white', 
        max_font_size = 10,
        max_words = 20, 
        colormap = 'Set2')
    words = countsByQuarter[time]
    wordcloud.fit_words(words) 
  
    # plot the WordCloud image     
    
    fig = px.imshow(wordcloud) 
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_xaxes(visible=False, showticklabels=False)
    fig.update_layout(
    title=str(time),
    yaxis={'visible': False, 'showticklabels': False},
    xaxis={'visible': False, 'showticklabels': False},
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="RebeccaPurple"
        )
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(port=8000, host='127.0.0.1', debug=True)

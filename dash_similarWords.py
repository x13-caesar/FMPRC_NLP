# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from collections import Counter

import gensim 
from gensim.models import Word2Vec
import numpy as np

import plotly.graph_objects as go


## some constant

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dataPath = './tokens.json'

w2v = Word2Vec.load("./word2vec.model")


## Dash App

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_json(dataPath)
df['counts'] = df['counts'].apply(Counter)
countsByQuarter = df.groupby(by=['quarter'])['counts'].sum()
quarters = countsByQuarter.index

app.layout = html.Div(children=[
    html.H1(children='解构新华文体'),

    html.Div(children='''
        输入任意数量的汉语词，我们将告诉你与它们最具相似度/相关性的三个词。
        使用全角逗号（，）隔开不同词汇，例如「经济，民生」。
        部分超高频词与无意义助词已经被剔除，无法查询或出现在结果中，例如`但、国家、会`。
        分析基于2011年来的外交部长讲话。
    '''),
    html.Br(),
    html.Div([
    	dcc.Input(
	    	id="init_words", 
	    	placeholder='在这里进行输入',
	    	style={'width': '80%'},
	    	)]),
    html.Br(),
    html.Div([
    	html.Table([
    		html.Tbody([
    			html.Tr(id='r1'),
    			html.Tr(id='r2'),
    			html.Tr(id='r3')])])]
        )
])


@app.callback(
    [Output(component_id="r1", component_property="children"),
    Output(component_id="r2", component_property="children"),
    Output(component_id="r3", component_property="children")
    ],
    [Input(component_id='init_words', component_property='value')],
)

def getSimilarWords(words):
	if not words: return '', '', ''
	try:
		words = words.split("，")
		result = ["相关词：{:　<8}  |  相关系数：{:.2%}".format(r[0], r[1]) for r in w2v.wv.most_similar(positive=words, topn=3)]
	except:
		return '该词语不在词库中，或格式有误', '', ''
	return result[0], result[1], result[2]



if __name__ == "__main__":
    app.run_server(port=8000, host='127.0.0.1', debug=True)

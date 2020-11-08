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

import numpy as np
from gensim.models import Word2Vec


## some constant

external_stylesheets = ['https://codepen.io/x13caesar/pen/dyXqVgr.css']
dataPath = 'tokens.json'

w2v = Word2Vec.load("word2vec.model")


## Dash App

app = dash.Dash(__name__, 
    title='解构新华文体')

df = pd.read_json(dataPath)
df['counts'] = df['counts'].apply(Counter)
countsByQuarter = df.groupby(by=['quarter'])['counts'].sum()
quarters = countsByQuarter.index

app.layout = html.Div(children=[
    html.H1(children='解构新华文体'),

    html.Div(children=[
        dcc.Markdown('''
        **输入任意数量的汉语词，下方将显示：**
        - 与输入词汇最具 **相似度/相关性** 的三个词；
        - 输入词汇使用频次随时间变化的趋势；

        **【注意】**
        - 请使用全角逗号 **，** 隔开不同词汇，例如：
        >   经济，民生
        - 部分超高频词与无意义助词已经被剔除，无法被查询或出现在结果中，例如： 
        >   国家，会，但
        - *所有分析均基于2011年以来的[外交部长讲话](https://www.fmprc.gov.cn/web/wjbz_673089/zyjh_673099/default.shtml)。*
        ''', 
        highlight_config={'theme':'dark'})]),
    html.Br(),
    html.Div([
        dcc.Input(
            id="init_words",
            placeholder='在这里进行输入',
            style={'width': '80%'},
            )]),
    html.Br(),
    html.Div([
        html.H5("相关词"),
        html.Table([
            html.Tbody([
                html.Tr(id='r1'),
                html.Tr(id='r2'),
                html.Tr(id='r3')])])]
        ),
    html.Br(),
    html.Div([
        html.H5("词频变化"),
        dcc.Graph(
            id='timeseries',
            figure={}
            )
    ]),
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


@app.callback(
    Output(component_id="timeseries", component_property="figure"),
    [Input(component_id='init_words', component_property='value')],
)
def generateTimeSeries(words):
    words = words.split("，")
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
        showlegend=True,
        plot_bgcolor='white'
    )


    return fig


if __name__ == "__main__":
    app.run_server(port=8000, host='127.0.0.1', debug=True)

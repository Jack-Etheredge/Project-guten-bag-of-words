# -*- coding: utf-8 -*-
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, Event
import plotly.graph_objs as go
import plotly.figure_factory as ff

import pandas as pd
import numpy as np
import pickle

# application = dash.Dash(__name__)
# server = application.server

app = dash.Dash(__name__)
application = app.server

#import flask

#server = flask.Flask(__name__)
#app = dash.Dash(__name__, server=server)

app.config.supress_callback_exceptions=True
app.title='Guten-bag-of-words (Jack Etheredge)'

############################################################################
# Load the initial data from pickle

# Set the book that initially loads
initial_novel_index=1

# pickloader = open("./04_Project_4/clean_books.pkl","rb")
# clean_books = pickle.load(pickloader)
# pickloader.close()

pickloader = open('./04_Project_4/'+'novel_names_dash'+'.pkl', 'rb')
novel_names = pickle.load(pickloader)
pickloader.close()

pickloader = open('./04_Project_4/'+'complexities'+'.pkl', 'rb')
complexities = pickle.load(pickloader)
pickloader.close()

pickloader = open('./04_Project_4/'+'book_clusters'+'.pkl', 'rb')
book_clusters = pickle.load(pickloader)
pickloader.close()

hist_data = [complexities]
group_labels = ['distplot']
fig = ff.create_distplot(hist_data, group_labels)
fig.layout.update({'title': 'Distribution of total complexity scores'})

min_complexity = min(complexities)
max_complexity = max(complexities)

############################################################################

app.layout = html.Div(className="gallery", children=[

    # Header:
    html.Div([
        html.H1('Project Guten-Bag-of-Words (Jack Etheredge)',style={'textAlign': 'center'}),
        html.Div(
            html.H2(['Visualize narrative patterns in ',
            html.A('Project Gutenberg' , href='http://www.gutenberg.org/'),
            ' books.'],style={'textAlign': 'center'}),
            )
    ]),

    # Dropdown:
    html.Div([
        dcc.Location(id='dropdown_selection', refresh=False),
        html.Div(id='page-content')
    ]),

    # Spacer:
    html.Div([
        html.H3('   ',style={'textAlign': 'center'})
    ]),

    html.Div([
        dcc.Location(id='complexity-message-div', refresh=False),
        html.Div(id='page-content-complexity')
    ]),

    # Spacer:
    html.Div([
        html.H3('   ',style={'textAlign': 'center'})
    ]),

    html.Div([
        dcc.Location(id='genre-message-div', refresh=False),
        html.Div(id='page-content-genre')
    ]),

    # Spacer:
    html.Div([
        html.H3('   ',style={'textAlign': 'center'})
    ]),

    html.Div([
        dcc.Location(id='random-books-message-div', refresh=False),
        html.Div(id='page-content-book-suggest', )
    ]),

    # Graph 1:
    html.Div([
        dcc.Graph(id='sentiment-graph')
    ]),

    # Graph 2:
    html.Div([
        dcc.Graph(id='topic-graph')
    ]),

    # Graph 3:
    html.Div([
        dcc.Graph(id='complexity-histogram-graph',
        figure=fig
                )
    ]),

    # Footer:

    html.Div([
    dcc.Markdown('''
#### Project Guten-Bag-of-Words

This project visualizes narrative patterns in [Project Gutenberg](http://www.gutenberg.org/) books.

**Jack Etheredge**

Check out my [blog](https://jack-etheredge.github.io/).

Check out my [Github](https://github.com/Jack-Etheredge).

Check out my [LinkedIn](https://www.linkedin.com/in/jack-etheredge-phd-84532585/).
''')
    ],style={'textAlign': 'right'}),

    ])

##############################################################################

# html.Div([html.H1(print('Total "complexity":', sum([delta-0.85 if delta>0 else 0 for delta in topic_deltas])))])


@app.callback(Output('page-content', 'children'),[Input('dropdown_selection', 'pathname')])
def generate_layout(url):
    return html.Div([
        html.Label('Select the book you wish to view:'),
        dcc.Dropdown(
            options=[{"label": novel_names[i],"value": i} for i in range(len(novel_names))],
            value=initial_novel_index,
            multi=False,
            id='input'
        )
    ])

@app.callback(Output('page-content-complexity', 'children'),[Input('complexity-message-div', 'pathname')])
def generate_layout(url):
    return html.Div([
        html.Div(id='complexity-message')
    ])

@app.callback(Output('page-content-genre', 'children'),[Input('genre-message-div', 'pathname')])
def generate_layout(url):
    return html.Div([
        html.Div(id='genre-message')
    ])

@app.callback(Output('page-content-book-suggest', 'children'),[Input('random-books-message-div', 'pathname')])
def generate_layout(url):
    return html.Div([
        html.Div(id='random-books-message')
    ])

# @app.callback(Output('page-content2', 'children'),[Input('dropdown_selection', 'pathname')])
# def generate_layout():
#     return html.Div([
#         html.Div(id='complexity-message')
#     ])

@app.callback(Output('random-books-message', 'children'), [Input('input', 'value')])
def display_output(novel_index):
    currentcluster = int(book_clusters[book_clusters['book'] == novel_names[novel_index]]['cluster'])
    bookslist = list(book_clusters[book_clusters['cluster']==currentcluster].sample(5).book)
    return(f"Five random books from this genre: {(', ').join(bookslist)}\n")

@app.callback(Output('genre-message', 'children'), [Input('input', 'value')])
def display_output(novel_index):
    wordslist = list(book_clusters[book_clusters['book'] == novel_names[novel_index]]['max_topic_cluster_words'])[0]
    return(f"Words associated with this genre: {(', ').join(wordslist)}\n")

# @app.callback(Output('output object id', 'children'), [Input('input object id', 'variable from input object id')])

@app.callback(Output('complexity-message', 'children'), [Input('input', 'value')])
def display_output(novel_index):
    pickloader = open('./04_Project_4/'+str(novel_index)+'/topic_deltas'+'.pkl', 'rb')
    topic_deltas = pickle.load(pickloader)
    pickloader.close()
    sumcomplexity = sum([delta-0.75 if delta>0 else 0 for delta in topic_deltas])
    return(f'Total "complexity": %.3f (range %.3f - %.3f)' % (sumcomplexity,min_complexity,max_complexity) )

@app.callback(Output('topic-graph','figure'),[Input('input','value')])
def update_graph(novel_index):
    # print(book_name)
    # selected_index = novel_names.index(book_name)

    # choosing the book:
    # novel_index=selected_index
    # print('Novel name:', novel_names[novel_index])
    pickloader = open('./04_Project_4/'+str(novel_index)+'/topic_deltas'+'.pkl', 'rb')
    topic_deltas = pickle.load(pickloader)
    pickloader.close()

    y_pos_topic = np.arange(len(topic_deltas))

    # print('Total "complexity":', sum([delta-0.85 if delta>0 else 0 for delta in topic_deltas]))

    return {'data': [
            go.Bar(
                x=list(y_pos_topic),
                y=[delta-0.75 if delta>0 else 0 for delta in topic_deltas],
                opacity=0.7,
            )],
        'layout': go.Layout(
            title=f'Topic change distance for {novel_names[novel_index]}',
            xaxis={'title': 'Beginning --> Book narrative --> End'},
            yaxis={'title': "Topic change distance"},
            hovermode='closest'
        )}

@app.callback(Output('sentiment-graph','figure'),[Input('input','value')])
def update_graph(novel_index):
    # Updating the sentiment graph:
    # selected_index = novel_names.index(book_name)
    # novel_index=selected_index

    pickloader = open('./04_Project_4/'+str(novel_index)+'/sentiments_binned'+'.pkl', 'rb')
    sentiments_binned = pickle.load(pickloader)
    pickloader.close()

    y_pos = np.arange(len(sentiments_binned))

    return {'data': [
                go.Bar(
                    x=list(y_pos),
                    y=sentiments_binned,
                    opacity=0.7,
                )],
            'layout': go.Layout(
                title=f'Sentiment shape over the course of the narrative: {novel_names[novel_index]}',
                xaxis={'title': 'Beginning --> Book narrative --> End'},
                yaxis={'title': 'Sentiment polarity'},
                hovermode='closest'
            )}

if __name__ == '__main__':
    application.run(debug=True)

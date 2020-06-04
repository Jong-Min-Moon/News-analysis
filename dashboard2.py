import flask
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go


import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.colors as mcolors



######################### FUCNTIONS #########################

import work
data = work.merge('D:/crawling/NN')
data_topic = work.merge('D:/crawling/LDAs')

print(data)
print(data_topic)

######################### FUCNTIONS #########################



all_days = np.sort(data.time.unique())
wordcloud_dropdown_day = dcc.Dropdown(id = "day", options = [ {"label": YMD, "value": YMD} for YMD in all_days ], value = all_days[0])
wordcloud_dropdown_topic = dcc.Dropdown(id = "topic") 

f_app = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server = f_app)

app.layout = html.Div([wordcloud_dropdown_day, wordcloud_dropdown_topic])


if __name__ == '__main__':
    
    app.run_server(debug=True)



################################################################################
#CALLBACKS

@app.callback(
    [Output("topic", "options"),
     Output("topic", "value")],
    [Input("day", "value")]
)
def set_topic_options(selected_day):
    print(type(selected_day))
    print(selected_day)
    today_data = data_topic[ (data_topic.time == selected_day) ]
    options_for_today = [ {"label": '{}번째 주제'.format(i), "value": i} for i in today_data.topic ]
    return options_for_today, 0



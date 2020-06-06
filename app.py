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

import os #파일 및 폴더 관리


######################### DATA #########################
def merge(mypath):
    file_list = os.listdir(mypath)
    file_list.sort()

    data = pd.read_csv( mypath + '/' + file_list[0], encoding='utf-8-sig')
    for filename in file_list[1:]:
        data = data.append(pd.read_csv(mypath + '/' + filename, encoding='utf-8-sig'), ignore_index=True)
        print(filename)
    
    return(data)

data = merge('./NN')
data_topic = merge('./LDAs')

print(data)
print(data_topic)

all_days = np.sort(data.time.unique())
data_sent_timeseries = pd.DataFrame()
for YMD in all_days:
    data_today = data[data.time == YMD]
    pos = len(data_today[data_today.sent_score > 0])
    neu = len(data_today[data_today.sent_score == 0])
    neg = len(data_today[data_today.sent_score < 0])
    total = len(data_today)
    data_sent_timeseries = data_sent_timeseries.append(pd.Series([YMD, pos, neu, neg, total]), ignore_index = True)
data_sent_timeseries.columns = ['time', 'pos', 'neu', 'neg', 'total']

######################### FUCNTIONS #########################
def plotly_wordcloud(data_frame):
    """A wonderful function that returns figure data for three equally
    wonderful plots: wordcloud, frequency histogram and treemap"""
    #complaints_text = list(data_frame["Consumer complaint narrative"].dropna().values)
    complaints_text = data_frame
    if len(complaints_text) < 1:
        return {}, {}, {}

    # join all documents in corpus
    #text = " ".join(list(complaints_text))

    word_cloud = WordCloud(max_words=20, max_font_size=90).generate_from_frequencies(complaints_text)


    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in word_cloud.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # get the positions
    x_arr = []
    y_arr = []
    for i in position_list:
        x_arr.append(i[0])
        y_arr.append(i[1])

    # get the relative occurence frequencies
    new_freq_list = []
    for i in freq_list:
        new_freq_list.append(i * 80000)

    trace = go.Scatter(
        x=x_arr,
        y=y_arr,
        textfont=dict(size=new_freq_list, color=color_list),
        hoverinfo="text",
        textposition="top center",
        hovertext=["{0} - {1}".format(w, f) for w, f in zip(word_list, freq_list)],
        mode="text",
        text=word_list,
    )

    layout = go.Layout(
        {
            "xaxis": {
                "showgrid": False,
                "showticklabels": False,
                "zeroline": False,
                "automargin": True,
                "range": [-100, 250],
            },
            "yaxis": {
                "showgrid": False,
                "showticklabels": False,
                "zeroline": False,
                "automargin": True,
                "range": [-100, 450],
            },
            "margin": dict(t=20, b=20, l=10, r=10, pad=4),
            "hovermode": "closest",
        }
    )

    wordcloud_figure_data = {"data": [trace], "layout": layout}
    word_list_top = word_list[:25]
    word_list_top.reverse()
    freq_list_top = freq_list[:25]
    freq_list_top.reverse()

    frequency_figure_data = {
        "data": [
            {
                "y": word_list_top,
                "x": freq_list_top,
                "type": "bar",
                "name": "",
                "orientation": "h",
            }
        ],
        "layout": {"height": 550, "margin": dict(t=20, b=20, l=100, r=20, pad=4)},
    }
    treemap_trace = go.Treemap(
        labels=word_list_top, parents=[""] * len(word_list_top), values=freq_list_top
    )
    treemap_layout = go.Layout({"margin": dict(t=10, b=10, l=5, r=5, pad=4)})
    treemap_figure = {"data": [treemap_trace], "layout": treemap_layout}
    return wordcloud_figure_data, frequency_figure_data, treemap_figure


def populate_lda_scatter(data_input):
    """Calculates LDA and returns figure data_input you can jam into a dcc.Graph()"""
    mycolors = np.array([color for name, color in mcolors.TABLEAU_COLORS.items()])
    
    
    # for each topic we create a separate trace
    traces = []
    #for topic_id in df_top3words["topic_id"]:
    for i in data_input.label.unique():
        df_topic = data_input[ data_input.label == i]
        cluster_name = df_topic.iloc[0,-1]
        trace = go.Scatter(
            name = str(cluster_name),
            x=df_topic["x"],
            y=df_topic["y"],
            mode="markers",
            hovertext=df_topic["title"],
            marker=dict(
                size=6,
                color=mycolors[i],  # set color equal to a variable
                colorscale="Viridis",
                showscale=False,
            ),
        )
        traces.append(trace)

    layout = go.Layout({"title": "LDA를 이용한 주제 분류"})

    return {"data": traces, "layout": layout}



############################## BODY ######################################
NAVBAR = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    
                    dbc.Col(
                        dbc.NavbarBrand("육군 보도 분석", className="ml-2")
                    ),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://plot.ly",
        )
    ],
    color="dark",
    dark=True,
    sticky="top",
)



wordcloud_dropdown_day = dcc.Dropdown(id = "day", options = [ {"label": YMD, "value": YMD} for YMD in all_days ], value = all_days[0])
wordcloud_dropdown_topic = dcc.Dropdown(id = "topic") 
wordcloud_freqtable = dcc.Loading(id = "loading-frequencies", children = [dcc.Graph(id = "frequency_figure")], type="default")
wordcloud_treemap = dcc.Loading(id = "loading-treemap", children = [dcc.Graph(id = "bank-treemap")], type="default")
wordcloud_cloudmap = dcc.Loading(id = "loading-wordcloud", children = [dcc.Graph(id = "bank-wordcloud")], type="default")
WORDCLOUD_PLOTS = [
    dbc.CardHeader(html.H5("주제별 주요 어휘")),
    dbc.Alert(
        "Not enough data to render these plots, please adjust the filters",
        id="no-data-alert",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dbc.Row(
                [ dbc.Col(wordcloud_dropdown_day), dbc.Col(wordcloud_dropdown_topic) ]
                ),
            dbc.Row(html.Hr()),
            dbc.Row(
                [ dbc.Col(wordcloud_freqtable),
                  dbc.Col(
                        [
                            dcc.Tabs(
                                id="tabs",
                                children=[
                                    dcc.Tab(
                                        label="Treemap",
                                        children=[wordcloud_treemap]
                                    ),
                                    dcc.Tab(
                                        label="Wordcloud",
                                        children=[wordcloud_cloudmap]
                                    )
                                ]
                            )
                        ],
                        md=8,
                    )
                ]
            )
        ]
    )
]


LDA_PLOT = dcc.Loading(
    id="loading-lda-plot", children=[dcc.Graph(id="tsne-lda")], type="default"
)


LDA_PLOTS = [
    dbc.CardHeader(html.H5("T-SNE 시각화")),
    dbc.Alert(
        "Not enough data to render LDA plots, please adjust the filters",
        id="no-data-alert-lda",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            html.P(
                "Click on a complaint point in the scatter to explore that specific complaint",
                className="mb-0",
            ),
            html.P(
                "(not affected by sample size or time frame selection)",
                style={"fontSize": 10, "font-weight": "lighter"},
            ),
            LDA_PLOT,
            html.Hr(),
            #LDA_TABLE,
        ]
    ),
]


############################################ TIME SERIES ####################################################
#5. 시계열 그래프
df1 = pd.read_csv('./finance-charts-apple.csv')

fig_timeseries = go.Figure()



fig_timeseries.add_trace(
    go.Scatter(
    x = data_sent_timeseries['time'],
    y = data_sent_timeseries['pos'],
    name='긍정'
))
fig_timeseries.add_trace(
    go.Scatter(
    x = data_sent_timeseries['time'],
    y = data_sent_timeseries['neg'],
    name = '부정'
))
fig_timeseries.add_trace(
    go.Scatter(
    x = data_sent_timeseries['time'],
    y = data_sent_timeseries['neu'],
    name = '중립'
))
fig_timeseries.add_trace(
    go.Scatter(
    x = data_sent_timeseries['time'],
    y = data_sent_timeseries['total'],
    name = '총 보도 건수'
))


fig_timeseries.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    )
)
#timeseries_dropdown_day = dcc.Dropdown(id = "day_for_timeseries", options = [ {"label": YMD, "value": YMD} for YMD in all_days ], value = all_days[0])

TIMESERIES_PLOT = dcc.Loading(
     id="loading-timeseries-plot", children=[dcc.Graph(id="timeseries", figure = fig_timeseries)], type="default"
)
TIMESERIES_PLOTS = [
    dbc.CardHeader(html.H5("육군 관련 보도 시계열 그래프")),
    dbc.Alert(
        "Not enough data to render TIME SERIES plots, please adjust the filters",
        id="no-data-alert-timeseries",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
           #timeseries_dropdown_day,
            html.P(
                "아래쪽 탐색기의 양 끝 막대를 드래그하면 원하는 구간을 자세히 볼 수 있습니다. 위쪽의 그래프를 더블클릭하면 구간 설정이 리셋됩니다.",
                className="mb-0",
            ),
            html.P(
                "(not affected by sample size or time frame selection)",
                style={"fontSize": 10, "font-weight": "lighter"},
            ),
            TIMESERIES_PLOT,
            html.Hr()
            #LDA_TABLE,
        ]
    ),
]


# )



######################################################################################################

############################################ PIE ####################################################

fig6 = go.Figure()
labels = ['Oxygen','Hydrogen','Carbon_Dioxide','Nitrogen']
values = [4500, 2500, 1053, 500]

fig6.add_trace(
   go.Pie(labels=labels, values=values),
   
)

######################################################################################################

###########################################################################
#1. 막대그래프
fig1 = go.Figure()
fig1.add_trace(go.Bar(
    y = [1,2,3,4,5,6],
    x=[20, 14, 23, 11, 12, 11],
    name='긍정',
    orientation='h',
    marker=dict(
        color='rgba(246, 78, 139, 0.6)',
        line=dict(color='rgb(67, 67, 67)', width=3)
    )
))
fig1.add_trace(go.Bar(
    y = [1,2,3,4,5,6],
    x=[12, 18, 29, 4, 5, 13],
    name='부정',
    orientation='h',
    marker=dict(
        color='rgba(58, 71, 80, 0.6)',
        line=dict(color='rgba(246, 78, 139, 1.0)', width=3)
    )
))
fig1.add_trace(go.Bar(
    y = [1,2,3,4,5,6],
    x=[15, 20, 19, 10, 11, 10],
    name='중립',
    orientation='h',
    marker=dict(
        color='rgba(58, 71, 80, 0.6)',
        line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
    )
))

fig1.update_layout(
    title='주제별 감성 비율(더미 데이터)',
    barmode='stack',
    font=dict(family="NanumBarunGothic", size=16)
    )


######################################################################
BODY = dbc.Container(
    [
        
        dbc.Card(WORDCLOUD_PLOTS),
        dbc.Row([dbc.Col([dbc.Card(LDA_PLOTS)])], style={"marginTop": 50}),
        dbc.Row([dbc.Col([dbc.Card(TIMESERIES_PLOTS)])], style={"marginTop": 50})
    ],
    className="mt-12",
)
#########################################################

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div([
    NAVBAR, BODY, dcc.Graph(figure = fig6), dcc.Graph(figure = fig1)
])





################################################################################
#CALLBACKS
@app.callback(
    [Output("topic", "options")],
    [Input("day", "value")]
)
def set_topic_options(selected_day):
    today_data = data_topic[ (data_topic.time == selected_day) ]
    print('today_data', today_data.label)
    opp = [[ {"label": '{}번째 주제:{}'.format(i, today_data[today_data.label == i].top3.item()), "value": i} for i in today_data.label]] #one-element list, whose the only element is a 6-element list.
    print(opp)
    return opp 

    
@app.callback(
    Output('topic', 'value'),
    [Input('topic', 'options')])
def set_topic_value(available_options):
    return available_options[0]['value']

@app.callback(
    [
        Output("bank-wordcloud", "figure"),
        Output("frequency_figure", "figure"),
        Output("bank-treemap", "figure"),
        Output("no-data-alert", "style"),
    ],
    [
        Input("day", "value"),
        Input("topic", "value")
    ],
)
def update_wordcloud_plot(selected_day, topic_no):
    """ Callback to rerender wordcloud plot """
    row = data_topic[(data_topic.time == selected_day) & (data_topic.label == topic_no)].iloc[0][:-3]
    plot_data = [eval(tup) for tup in row]

    
    
    wordcloud, frequency_figure, treemap = plotly_wordcloud(dict(plot_data))
    alert_style = {"display": "none"}
    if (wordcloud == {}) or (frequency_figure == {}) or (treemap == {}):
        alert_style = {"display": "block"}
    print("redrawing bank-wordcloud...done")
    return (wordcloud, frequency_figure, treemap, alert_style)







@app.callback(
    [
        #Output("lda-table", "data"),
        #Output("lda-table", "columns"),
        Output("tsne-lda", "figure"),
        Output("no-data-alert-lda", "style")],
    [Input("day", "value")],
)
def update_lda_table(day):
    """ Update LDA table and scatter plot based on precomputed data """
    data_today = data[data.time == day]
    lda_scatter_figure = populate_lda_scatter(data_today)
    #columns = [{"name": i, "id": i} for i in data_today.columns]
    #data = df_dominant_topic.to_dict("records")

    return lda_scatter_figure, {"display": "none"}


# @app.callback(
#     [ Output("timeseries", "figure") ],
#     [ Input("day_for_timeseries", "value")]
# )
# def update_timeseries_plot(selected_day):
#     """ Callback to rerender wordcloud plot """
#     data_today = data[data.time == day]
#     plot_data = [eval(tup) for tup in row]

    

#     return (wordcloud, frequency_figure, treemap, alert_style)


if __name__ == '__main__': #이게 callback보다 앞에 와야 callback이 디버깅됨
    app.run_server(debug=True)
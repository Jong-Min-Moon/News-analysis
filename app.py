import flask

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Output, Input, State
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
data['Document_No'] = np.arange(0, len(data))
data_comment = merge('./NC')
data_comment = pd.merge(data_comment, data[['url', 'Document_No']], how = 'left', on = 'url')



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
        new_freq_list.append(i * 80)

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
    
    
    # for each topic and sentiment, we create a separate trace
    traces = []
    markers_list = ['circle', 'x', 'square']
    for topic_no in data_input.label.unique():
        df_topic = data_input[ data_input.label == topic_no]
        bools = {'pos' : (df_topic.sent_score > 0), 'neg' : (df_topic.sent_score < 0), 'neu' : (df_topic.sent_score == 0)}
        cluster_name = df_topic.iloc[0,-2]

        for i, abool in enumerate(bools):
            trace = go.Scatter(
                name = '{}_{}'.format(cluster_name, abool ),
                x=df_topic[bools[abool]]["x"],
                y=df_topic[bools[abool]]["y"],
                mode="markers",
                hovertext = df_topic['Document_No'].astype('str') + '@' + df_topic.press + '@' + df_topic.title,
                marker_symbol = markers_list[i],
                opacity=0.6,
                marker=dict(
                    size=7,
                    color=mycolors[topic_no],  # set color equal to a variable
                    colorscale="Viridis",
                    showscale=False,
                )
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
###################################1. 막대그래프################################################################################
latest_data = data[ (data.time == all_days[-1]) ]
bar_y = [ '{}번째 주제:{}'.format(i, latest_data[latest_data.label == i].top3.iloc[0]) for i in np.sort(latest_data.label.unique())]
bar_x = [[],[],[]]
for i in np.sort(latest_data.label.unique()): 
    latest_data_for_topic = latest_data[latest_data.label == i]
    bar_x[0].append( len(latest_data_for_topic[latest_data_for_topic.sent_score > 0]) ) #pos
    bar_x[1].append( len(latest_data_for_topic[latest_data_for_topic.sent_score == 0]) ) #neu
    bar_x[2].append( len(latest_data_for_topic[latest_data_for_topic.sent_score < 0]) ) #neg




fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    y = bar_y,
    x = bar_x[0],
    name='긍정',
    orientation='h',
    marker=dict(
        color = 'rgb(1, 102, 94)',
        line = dict(color = 'rgb(1, 102, 94)', width=3)
    )
))
fig_bar.add_trace(go.Bar(
    y = bar_y,
    x = bar_x[1],
    name = '중립',
    orientation='h',
    marker=dict(
        color = 'rgb(135, 135, 135)',
        line = dict(color = 'rgb(135, 135, 135)', width=3)
    )
))
fig_bar.add_trace(go.Bar(
    y = bar_y,
    x = bar_x[2],
    name = '부정',
    orientation='h',
    marker=dict(
        color = 'rgb(172, 43, 36)',
        line = dict(color = 'rgb(172, 43, 36)', width=3)
    )
))

fig_bar.update_layout(
    barmode='stack',
    font=dict(family="NanumBarunGothic", size=16)
    )

BAR_PLOT = dcc.Loading(
     id="loading-BAR-plot", children=[dcc.Graph(id="BAR", figure = fig_bar)], type="default"
)


BAR_PLOTS = [
    dbc.CardHeader(html.H5("오늘의 육군 관련 뉴스 주제별 감성 현황")),
    dbc.Alert(
        "Not enough data to render BAR plots, please adjust the filters",
        id="no-data-alert-BAR",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            BAR_PLOT,
            html.Hr(),
           
        ]
    ),
]
################################################################################################
latest_data_comment = data_comment[data_comment.time.str.slice(start = 0, stop = 10) == all_days[-1] ]
latest_data_comment_top5 = latest_data_comment.sort_values(by = 'like', ascending = False).iloc[:5, :]
latest_data_comment_bottom5 = latest_data_comment.sort_values(by = 'dislike', ascending = False).iloc[:5, :]

COMMENT_TOP5_SHOW = dash_table.DataTable(
    data = latest_data_comment_top5.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in latest_data_comment_top5.columns]
)

COMMENT_BOTTOM5_SHOW = dash_table.DataTable(
    data = latest_data_comment_bottom5.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in latest_data_comment_bottom5.columns]
)

COMMENT_TOP5_PLOTS = [
    dbc.CardHeader(html.H5("오늘의 육군 관련 뉴스에 달린 댓글 중 좋아요가 가장 많은 5개")),
    dbc.Alert(
        "Not enough data to render comment plots, please adjust the filters",
        id="no-data-alert-comment",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            COMMENT_TOP5_SHOW
        ]
    ),
]

COMMENT_BOTTOM5_PLOTS = [
    dbc.CardHeader(html.H5("오늘의 육군 관련 뉴스에 달린 댓글 중 싫어요가 가장 많은 5개")),
    dbc.Alert(
        "Not enough data to render comment plots, please adjust the filters",
        id="no-data-alert-comment",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            COMMENT_BOTTOM5_SHOW
        ]
    ),
]

################################################################################################
wordcloud_dropdown_day = dcc.Dropdown(id = "day", options = [ {"label": YMD, "value": YMD} for YMD in all_days ], value = all_days[-1])
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

LDA_dropdown_day = dcc.Dropdown(id = "day_for_LDA", options = [ {"label": YMD, "value": YMD} for YMD in all_days ], value = all_days[-1])

LDA_PLOT = dcc.Loading(
    id="loading-lda-plot", children=[dcc.Graph(id="tsne-lda")], type="default"
)

LDA_TABLE = html.Div(
    id="lda-table-block",
    children=[
        dcc.Loading(
            id="loading-lda-table",
            children=[
                dash_table.DataTable(
                    id="lda-table",
                    style_cell_conditional=[
                        {
                            "if": {"column_id": "text"},
                            "textAlign": "left",
                            "whiteSpace": "normal",
                            "height": "auto",
                            "min-width": "80%",
                        }
                    ],
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "rgb(243, 246, 251)",
                        }
                    ],
                    style_cell={
                        "padding": "16px",
                        "whiteSpace": "normal",
                        "height": "auto",
                        "max-width": "0",
                    },
                    style_header={"backgroundColor": "white", "fontWeight": "bold"},
                    style_data={"whiteSpace": "normal", "height": "auto"},
                    filter_action="native",
                    page_action="native",
                    page_current=0,
                    page_size=5,
                    columns=[],
                    data=[],
                )
            ],
            type="default",
        )
    ],
    style={"display": "none"},
)

COMMENT_TABLE = html.Div(
    id="comment-table-block",
    children=[
        dcc.Loading(
            id="loading-comment-table",
            children=[
                dash_table.DataTable(
                    id="comment-table",
                    style_cell_conditional=[
                        {
                            "if": {"column_id": "댓글"},
                            "textAlign": "left",
                            "whiteSpace": "normal",
                            "height": "auto",
                            "min-width": "60%",
                        }
                    ],
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "rgb(243, 246, 251)",
                        }
                    ],
                    style_cell={
                        "padding": "16px",
                        "whiteSpace": "normal",
                        "height": "auto",
                        "max-width": "0",
                    },
                    style_header={"backgroundColor": "white", "fontWeight": "bold"},
                    style_data={"whiteSpace": "normal", "height": "auto"},
                    filter_action="native",
                    page_action="native",
                    page_current=0,
                    page_size=7,
                    columns=[],
                    data=[],
                )
            ],
            type="default",
        )
    ],
    style={"display": "none"},
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
                "날짜를 선택하면 해당일의 기사들 간의 상대적인 거리와 위치를 볼 수 있습니다.",
                className="mb-0",
            ),
            LDA_dropdown_day,
            LDA_PLOT,
            html.Hr(),
            LDA_TABLE,
            html.Hr(),
            COMMENT_TABLE
        ]
    ),
]


############################################ TIME SERIES ####################################################
#5. 시계열 그래프

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
            TIMESERIES_PLOT,
            html.Hr()
        ]
    ),
]

#####################################################################################################
############################################ TIME SERIES ####################################################
#5. 시계열 그래프

fig_timeseries_comment = go.Figure()

data_comment_for_timeseries = data_comment.copy()
data_comment_for_timeseries['time2'] = data_comment_for_timeseries.time.str.slice(start = 0, stop = 10)
data_comment_for_timeseries_agg = data_comment_for_timeseries.groupby(by = ['time2'], as_index = False).count()
print(data_comment_for_timeseries_agg)

fig_timeseries_comment.add_trace(
    go.Scatter(
    x = data_comment_for_timeseries_agg['time2'],
    y = data_comment_for_timeseries_agg['press'],
    name = '총 댓글 건수'
))


fig_timeseries_comment.update_xaxes(
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

timeseries_comment_PLOT = dcc.Loading(
     id="loading-timeseries_comment-plot", children=[dcc.Graph(id="timeseries_comment", figure = fig_timeseries_comment)], type="default"
)
timeseries_comment_PLOTS = [
    dbc.CardHeader(html.H5("육군 관련 보도 댓글 시계열 그래프")),
    dbc.Alert(
        "Not enough data to render TIME SERIES plots, please adjust the filters",
        id="no-data-alert-timeseries_comment",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
           #timeseries_comment_dropdown_day,
            html.P(
                "아래쪽 탐색기의 양 끝 막대를 드래그하면 원하는 구간을 자세히 볼 수 있습니다. 위쪽의 그래프를 더블클릭하면 구간 설정이 리셋됩니다.",
                className="mb-0",
            ),
            timeseries_comment_PLOT,
            html.Hr()
        ]
    ),
]



######################################################################################################

############################################ PIE ####################################################
PIE_dropdown_day = dcc.Dropdown(id = "day_for_pie", options = [ {"label": YMD, "value": YMD} for YMD in all_days ], value = all_days[-1])
PIE_dropdown_topic = dcc.Dropdown(id = "topic_for_pie") 
PIE_PLOT = dcc.Loading(
     id="loading-PIE-plot", children=[dcc.Graph(id="PIE")], type="default"
)
PIE_PLOTS = [
    dbc.CardHeader(html.H5("육군 관련 보도 감성분석 파이 그래프")),
    dbc.Alert(
        "Not enough data to render PIE plots, please adjust the filters",
        id="no-data-alert-PIE",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            html.P(
                '날짜와 주제를 선택하세요.',
                className="mb-0",
            ),
           dbc.Row(
                [ dbc.Col(PIE_dropdown_day), dbc.Col(PIE_dropdown_topic) ]
                ),
            
            PIE_PLOT,
            html.Hr()
        ]
    ),
]
######################################################################################################

###########################################################################

######################################################################
BODY = dbc.Container(
    [
        dbc.Card(BAR_PLOTS),
        dbc.Row([dbc.Col([dbc.Card(COMMENT_TOP5_PLOTS)])], style={"marginTop": 50}),
        dbc.Row([dbc.Col([dbc.Card(COMMENT_BOTTOM5_PLOTS)])], style={"marginTop": 50}),
        dbc.Row([dbc.Col([dbc.Card(PIE_PLOTS)])], style={"marginTop": 50}),
        dbc.Row([dbc.Col([dbc.Card(WORDCLOUD_PLOTS)])], style={"marginTop": 50}),
        dbc.Row([dbc.Col([dbc.Card(LDA_PLOTS)])], style={"marginTop": 50}),
        dbc.Row([dbc.Col([dbc.Card(TIMESERIES_PLOTS)])], style={"marginTop": 50}),
        dbc.Row([dbc.Col([dbc.Card(timeseries_comment_PLOTS)])], style={"marginTop": 50})
        
        
    ],
    className="mt-12",
)
#########################################################
texttest = html.Div(
children=[
                        html.H4(className='what-is', children='What is Clustergram?'),
                        html.P('Clustergram is a combination of a heatmap and '
                               'dendrograms that allows you to display '
                               'hierarchical clustering data. '
                               'Clusters on the dendrograms are highlighted in '
                               'one color if they comprise data points '
                               'that share some minimal level of correlation.'),
                        html.P('In the "Data" tab, you can select a preloaded '
                               'dataset to display or, alternatively, upload one '
                               'of your own. A sample dataset is also available '
                               'for download in the tab.'),
                        html.P('In the "Graph" tab, you can choose the '
                               'dimension(s) along which clustering will be '
                               'performed (row or column). You can also change '
                               'the threshold that determines the point at which '
                               'clusters are highlighted for the row and column '
                               'dendrograms, and choose which rows and columns '
                               'are used to compute the clustering.'),
                        html.P('In addition, you can highlight specific clusters '
                               'by adding annotations to the clustergram, and '
                               'choose whether to show or hide the labels for the '
                               'rows and/or columns.')
                    ])
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div([
    NAVBAR, BODY,texttest
])

server = app.server



################################################################################
#CALLBACKS
@app.callback(
    [Output("topic", "options")],
    [Input("day", "value")]
)
def set_topic_options(selected_day):
    today_data = data_topic[ (data_topic.time == selected_day) ]
    #print('today_data', today_data.label)
    opp = [[ {"label": '{}번째 주제:{}'.format(i, today_data[today_data.label == i].top3.item()), "value": i} for i in today_data.label]] #one-element list, whose the only element is a 6-element list.
    #print(opp)
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
       
        Output("tsne-lda", "figure"),
        Output("no-data-alert-lda", "style")],
    [Input("day_for_LDA", "value")],
)
def update_lda_table(day):
    """ Update LDA table and scatter plot based on precomputed data """
    data_today = data[data.time == day]
    lda_scatter_figure = populate_lda_scatter(data_today)
    return lda_scatter_figure, {"display": "none"}


@app.callback(
    [
        Output("lda-table", "data"),
        Output("lda-table", "columns"),
        Output("lda-table-block", "style"),
        Output("comment-table", "data"),
        Output("comment-table", "columns"),
        Output("comment-table-block", "style")],
    [Input("tsne-lda", "clickData")]
)
def filter_table_on_scatter_click(tsne_click):
    """ TODO """
    if tsne_click is not None:
        click_item = str(tsne_click["points"][0]["hovertext"]).split('@')
        selected_doc_no = click_item[0]
        selected_press = click_item[1]
        selected_title = click_item[2]
        
        
        data_today_clicked = data[data['Document_No'] == int(selected_doc_no)].T
        data_today_clicked.reset_index(drop = False, inplace = True)
        data_today_clicked.columns = ['item', 'text']
        columns_news = [{"name": 'item', "id": 'item'}, {"name": 'text', "id": 'text'}]
        data_lda_table = data_today_clicked.to_dict("records")
        
        
        comment_today_clicked = data_comment[data_comment['Document_No'] == int(selected_doc_no)].iloc[:,3:8]
        comment_today_clicked.columns = ['댓글', '좋아요', '싫어요', '작성시간', '답글']
        if len(comment_today_clicked) == 0:
            comment_today_clicked = comment_today_clicked.append(pd.DataFrame(['댓글 없음', '','','',''], columns = ['댓글', '좋아요', '싫어요', '작성시간', '답글']), ignore_index = True)
        
        columns_comment = [{"name": i, "id": i} for i in comment_today_clicked.columns]
        comment_table = comment_today_clicked.to_dict("records")

        return (data_lda_table, columns_news,  {"display": "block"} , comment_table, columns_comment, {"display": "block"})
    else:
        return ( [], [], {"display": "none"} , [], [], {"display": "none"})
        



#PIE
@app.callback(
    [Output("topic_for_pie", "options")],
    [Input("day_for_pie", "value")]
)
def set_topic_options(selected_day):
    today_data = data_topic[ (data_topic.time == selected_day) ]
    #print('today_data', today_data.label)
    opp = [[{'label': '전체', 'value' : -1}] + [ {"label": '{}번째 주제:{}'.format(i, today_data[today_data.label == i].top3.item()), "value": i} for i in today_data.label]] #one-element list, whose the only element is a 6-element list.
    #print(opp)
    return opp 

@app.callback(
    Output('topic_for_pie', 'value'),
    [Input('topic_for_pie', 'options')])
def set_topic_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output("PIE", "figure"),
    [ Input("day_for_pie", "value"),
    Input("topic_for_pie", "value")]
)
def update_pie_plot(selected_day, selected_topic):
    """ Callback to rerender pie plot """
    if selected_topic == -1:
        data_today_sent = data_sent_timeseries[data_sent_timeseries.time == selected_day]
        sent_values = list(data_today_sent.iloc[0,1:-1])
    else:
        data_today = data[(data.time == selected_day) & (data.label == selected_topic)]
        #print(data_today)
        pos = len(data_today[data_today.sent_score > 0])
        neu = len(data_today[data_today.sent_score == 0])
        neg = len(data_today[data_today.sent_score < 0])
        sent_values = [pos, neu, neg]
    
    fig = go.Figure()
    #print(sent_values)
    fig.add_trace(
        go.Pie(labels = ['긍정','중립','부정'], values = sent_values))
    #print(fig)
    return fig



if __name__ == '__main__': #이게 callback보다 앞에 와야 callback이 디버깅됨
    app.run_server()

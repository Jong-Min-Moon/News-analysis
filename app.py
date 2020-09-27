
from wordcloud import WordCloud
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go


import pandas as pd
import numpy as np
#from wordcloud import WordCloud
#import matplotlib.colors as mcolors

import os #파일 및 폴더 관리
import sqlite3


from widgets import functions 
from widgets import basic



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])
server = app.server


######################### DATA #########################
con = sqlite3.connect('./rokanews.db')
data_news = pd.read_sql('SELECT *, substr(time_written, 0, 11) as time_written_short FROM naver_news', con)
data_comment = pd.read_sql('SELECT *, substr(time_written, 0, 11) as time_written_short FROM naver_comment_sent', con)

print(data_comment['url'])
# data_topic = pd.read_sql('SELECT * FROM LDA', con)
data_top10 = pd.read_sql('SELECT * FROM pagerank', con)
con.close()

data_top10_daylist = np.sort( data_top10.time_written.unique() )


# all_days = np.sort(data.time.unique())
# data_sent_timeseries = pd.DataFrame()
# for YMD in all_days:
#     data_today = data[data.time == YMD]
#     pos = len(data_today[data_today.sent_score > 0])
#     neu = len(data_today[data_today.sent_score == 0])
#     neg = len(data_today[data_today.sent_score < 0])
#     total = len(data_today)
#     data_sent_timeseries = data_sent_timeseries.append(pd.Series([YMD, pos, neu, neg, total]), ignore_index = True)
# data_sent_timeseries.columns = ['time', 'pos', 'neu', 'neg', 'total']

######################### FUCNTIONS #########################
# def rescale(series, range):
#     #min to 0
#     new = series - series.min()
#     new = new / new.max()
#     new = new * range - (range/2)
#     return new




# def populate_lda_scatter(data_input):
#     """Calculates LDA and returns figure data_input you can jam into a dcc.Graph()"""
#     mycolors = np.array([color for name, color in mcolors.TABLEAU_COLORS.items()])
    
    
#     # for each topic and sentiment, we create a separate trace
#     traces = []
#     markers_list = ['circle', 'x', 'square']
#     for topic_no in data_input.label.unique():
#         df_topic = data_input[ data_input.label == topic_no]
#         bools = {'pos' : (df_topic.sent_score > 0), 'neg' : (df_topic.sent_score < 0), 'neu' : (df_topic.sent_score == 0)}
#         cluster_name = df_topic.iloc[0,-2]

#         for i, abool in enumerate(bools):
#             trace = go.Scatter(
#                 name = '{}_{}'.format(cluster_name, abool ),
#                 x=df_topic[bools[abool]]["x"],
#                 y=df_topic[bools[abool]]["y"],
#                 mode="markers",
#                 hovertext = df_topic['doc_id'].astype('str') + '@' + df_topic.press + '@' + df_topic.title,
#                 marker_symbol = markers_list[i],
#                 opacity=0.6,
#                 marker=dict(
#                     size=7,
#                     color=mycolors[topic_no],  # set color equal to a variable
#                     colorscale="Viridis",
#                     showscale=False,
#                 )
#             )
#             traces.append(trace)


       

#     layout = go.Layout({"title": "LDA를 이용한 주제 분류"})

#     return {"data": traces, "layout": layout}



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
            
        )
    ],
    color="dark",
    dark=True,
    sticky="top",
)

##################################################################################

Dropdown_Top10_Day = dcc.Dropdown(id = "Dropdown_Top10_Day", options = [ {"label": YMD, "value": YMD} for YMD in data_top10_daylist ], value = data_top10_daylist[-1])

Top10_Table = html.Div(className = 'section',
                       children=[
                            html.Div(
                                className='page',
                                id = 'Top10_Table'
                            )
                       ]
) 
                
                    

Daily_Top10_Card = [
    dbc.CardHeader(html.H5("오늘의 육군 관련 뉴스 주요 주제")),
    dbc.CardBody([ Dropdown_Top10_Day,
                   html.Hr(),
                   Top10_Table]),
]

@app.callback(
    Output('Top10_Table', 'children'),
    [Input('Dropdown_Top10_Day', 'value')])
def Dropdown_Top10_day__Top10_Table(selected_day):
    return functions.generate_Top10_Table(selected_day)



############################# 1. 댓글 건수 시계열 그래프 ###############################################

fig_timeseries = go.Figure()



def get_sent_freq_by_day(day):
    comments_for_url= data_comment[data_comment['time_written_short'] == day]
    
    n_comments = len(comments_for_url)
    n_comments_positive = len(comments_for_url[comments_for_url.sent_score > 0])
    n_comments_negative = len(comments_for_url[comments_for_url.sent_score < 0])
    n_comments_neutral = n_comments - n_comments_positive - n_comments_negative
    
    return np.array([n_comments_positive, n_comments_negative, n_comments_neutral])

sent_freq_list_by_day = list(map(get_sent_freq_by_day, data_top10_daylist))

sent_freq_timeseries_positive = list(map(lambda x : x[0], sent_freq_list_by_day))
sent_freq_timeseries_negative = list(map(lambda x : x[1], sent_freq_list_by_day))
sent_freq_timeseries_neutral  = list(map(lambda x : x[2], sent_freq_list_by_day))
sent_freq_timeseries_total    = list(map(np.sum, sent_freq_list_by_day))
 

trace_positive = go.Scatter(
        x = data_top10_daylist,
        y = sent_freq_timeseries_positive,
        name='긍정',
        )

trace_negative = go.Scatter(
        x = data_top10_daylist,
        y = sent_freq_timeseries_negative,
        name = '부정',
        )

trace_neutral = go.Scatter(
        x = data_top10_daylist,  
        y = sent_freq_timeseries_neutral,
        name = '중립',
        )

trace_total= go.Scatter(
        x = data_top10_daylist,  
        y = sent_freq_timeseries_total,
        name = '일일종합',
        )

fig_timeseries.add_trace(trace_positive)
fig_timeseries.add_trace(trace_negative)
fig_timeseries.add_trace(trace_neutral)
fig_timeseries.add_trace(trace_total)



TIMESERIES_PLOT = dcc.Loading(
     id="loading-timeseries-plot", children=[dcc.Graph(id="timeseries", figure = fig_timeseries)], type="default"
)
Timeseries_Plot_Card = [
    dbc.CardHeader(html.H5("육군 보도 댓글 종합 현황")),
    dbc.Alert(
        "Not enough data to render TIME SERIES plots, please adjust the filters",
        id="no-data-alert-timeseries",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            TIMESERIES_PLOT,
        ]
    ),
]
###################################1. 막대그래프################################################################################
def group_url_comments_into_master(data_news_oneday, data_comment_oneday):
    return [[url for url in master.in_url if url in data_comment_oneday.url.values] for i, master in data_news_oneday.groupby('master')]

def get_sent_freq_by_master(url_data_one_master):
    sent_vec_for_master = np.array([0, 0, 0])
    if url_data_one_master:
        for url in url_data_one_master:
            sent_vec_for_master += get_sent_freq_by_url(url)
    return sent_vec_for_master

def get_sent_freq_by_url(url):
    comments_for_url= data_comment[data_comment['url'] == url]
    
    n_comments = len(comments_for_url)
    n_comments_positive = len(comments_for_url[comments_for_url.sent_score > 0])
    n_comments_negative = len(comments_for_url[comments_for_url.sent_score < 0])
    n_comments_neutral = n_comments - n_comments_positive - n_comments_negative
    
    return np.array([n_comments_positive, n_comments_negative, n_comments_neutral])

def barstack(selected_day):
    top_labels = ['긍정', '중립', '부정']
    colors = ['rgb(1, 102, 94)', 'rgb(135, 135, 135)', 'rgb(172, 43, 36)']

    data_news_for_selected_day = data_news[ (data_news.time_written_short == selected_day) ]
    data_comment_for_selected_day = data_comment[ (data_comment.time_written_short == selected_day) ]
    url_list_for_selected_day = group_url_comments_into_master(data_news_for_selected_day, data_comment_for_selected_day)

    x_data = [ get_sent_freq_by_master(url_list_for_one_master) for url_list_for_one_master in url_list_for_selected_day ]
    x_data_array = np.array(x_data)
    x_data.append(x_data_array.sum(axis = 0))

    y_data = [ '{}번째 주제'.format(i+1) for i in range(len(url_list_for_selected_day))] + ['일일종합']

    fig = go.Figure()

    for i in range(0, len(x_data[0])): #긍정, 중립, 부정
        for xd, yd in zip(x_data, y_data):
            fig.add_trace(go.Bar(
                x=[xd[i]], y=[yd],
                orientation='h',
                hovertext = yd[0],
                marker=dict(
                    color=colors[i],
                    line=dict(color='rgb(248, 248, 249)', width=1)
                )
            ))

    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            domain=[0.15, 1]
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        barmode='stack',
        paper_bgcolor='rgb(248, 248, 255)',
        plot_bgcolor='rgb(248, 248, 255)',
        margin=dict(l=120, r=10, t=140, b=80),
        showlegend=False,
    )

    annotations = []

    for yd, xd in zip(y_data, x_data):
        # labeling the y-axis
        annotations.append(dict(xref='paper', yref='y',
                                x=0.14, y=yd,
                                xanchor='right',
                                text=str(yd),
                                font=dict(family='Arial', size=14,
                                        color='rgb(67, 67, 67)'),
                                showarrow=False, align='right'))
        # labeling the first percentage of each bar (x_axis)
        annotations.append(dict(xref='x', yref='y',
                                x=xd[0] / 2, y=yd,
                                text=str(xd[0]) + '%',
                                font=dict(family='Arial', size=14,
                                        color='rgb(248, 248, 255)'),
                                showarrow=False))
        # labeling the first Likert scale (on the top)
        if yd == y_data[-1]:
            annotations.append(dict(xref='x', yref='paper',
                                    x=xd[0] / 2, y=1.1,
                                    text=top_labels[0],
                                    font=dict(family='Arial', size=14,
                                            color='rgb(67, 67, 67)'),
                                    showarrow=False))
        space = xd[0]
        for i in range(1, len(xd)):
                # labeling the rest of percentages for each bar (x_axis)
                annotations.append(dict(xref='x', yref='y',
                                        x=space + (xd[i]/2), y=yd,
                                        text=str(xd[i]) + '%',
                                        font=dict(family='Arial', size=14,
                                                color='rgb(248, 248, 255)'),
                                        showarrow=False))
                # labeling the Likert scale
                if yd == y_data[-1]:
                    annotations.append(dict(xref='x', yref='paper',
                                            x=space + (xd[i]/2), y=1.1,
                                            text=top_labels[i],
                                            font=dict(family='Arial', size=14,
                                                    color='rgb(67, 67, 67)'),
                                            showarrow=False))
                space += xd[i]

    fig.update_layout(annotations=annotations)
    
    
    return fig

Dropdown_Top10_Day_Barstack = dcc.Dropdown(id = "Dropdown_Top10_Day_Barstack", options = [ {"label": YMD, "value": YMD} for YMD in data_top10_daylist ], value = data_top10_daylist[-1])

BAR_PLOT = dcc.Loading(
     id="loading-BAR-plot", children=[dcc.Graph(id="BAR")], type="default"
)

Barstack_Comment_Table = html.Div(
    id="barstack-comment-table-block",
    children=[
        dcc.Loading(
            id="loading-barstack-comment-table",
            children=[
                dash_table.DataTable(
                    id="barstack-comment-table",
                    style_cell_conditional=[
                        {
                            "if": {"column_id": "content"},
                            "textAlign": "left",
                            "whiteSpace": "normal",
                            "height": "auto",
                            "min-width": "70%",
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



Daily_Top10_Barstack_Card = [
    dbc.CardHeader(html.H5("오늘의 육군 관련 뉴스 주제별 댓글 감성 현황")),
    dbc.Alert(
        "Not enough data to render BAR plots, please adjust the filters",
        id="no-data-alert-BAR",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [   Dropdown_Top10_Day_Barstack,
            BAR_PLOT,
            html.Hr(),
            Barstack_Comment_Table
        ]
    ),
]



#주제별 감성 bar 그래프 날짜 설정
@app.callback(
    Output('BAR', 'figure'),
    [Input('Dropdown_Top10_Day_Barstack', 'value')])
def set_barstack_for_selected_day(selected_day):
    return barstack(selected_day)




#3. 점을 클릭하면 댓글이 나오도록
@app.callback(
    [
        Output("barstack-comment-table", "data"),
        Output("barstack-comment-table", "columns"),
        Output("barstack-comment-table-block", "style"),
    ],
    [
     Input('BAR', 'clickData'),   
     Input('Dropdown_Top10_Day_Barstack', 'value')
    ]
)
def filter_table_on_bar_click(bar_click, day):
    if bar_click is not None:
        news_for_comment = data_news[data_news.time_written_short == day ]

        master_id = bar_click['points'][0]['y'][0]
        if master_id != '일':
            news_for_comment = [df for i, (doc_id, df) in enumerate(news_for_comment.groupby('master')) if i+1 == int(master_id)][0]
        url_list = [url for url in news_for_comment.in_url if url in data_comment.url.values] 
        df_list = list(map(lambda x : data_comment[data_comment.url == x], url_list))

        comment_for_day_and_master = pd.concat(df_list, ignore_index = True)
        comment_for_day_and_master = comment_for_day_and_master[[ 'press', 'title', 'content', 'like', 'dislike'] ]
        comment_for_day_and_master = comment_for_day_and_master.sort_values(by = 'like', ascending = False)

      
        colnames  = ['언론사', '기사제목', '댓글내용', '좋아요', '싫어요']
        comment_for_day_and_master.columns = ['언론사', '기사제목', '댓글내용', '좋아요', '싫어요']
        if len(comment_for_day_and_master) == 0:
            comment_for_day_and_master = comment_for_day_and_master.append(pd.DataFrame(['댓글 없음', '','','',''], columns = colnames ), ignore_index = True)
        columns_to_display = [ {"name": i, "id": i} for i in colnames]
  
     
        data_comment_table = comment_for_day_and_master.to_dict("records")
        return (data_comment_table, columns_to_display,  {"display": "block"} )
    else:
        return ( [], [], {"display": "none"})



wordcloud_cloudmap = dcc.Loading(id = "loading-wordcloud", children = [dcc.Graph(id = "bank-wordcloud")], type="default")
wordcloud_treemap = dcc.Loading(id = "loading-treemap", children = [dcc.Graph(id = "bank-treemap")], type="default")

Wordcloud_Card = [
    dbc.CardHeader(html.H5("주제어")),
    dbc.Alert(
        "Not enough data to render these plots, please adjust the filters",
        id="no-data-alert",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [dbc.Row(
                [
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
                                    )])],md=8,)])])]

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
    return wordcloud_figure_data, treemap_figure



from sklearn.feature_extraction.text import CountVectorizer
from kiwipiepy import Kiwi
import pickle
# tokenize 함수를 정의합니다. 한국어 문장을 입력하면 형태소 단위로 분리하고, 
# 불용어 및 특수 문자 등을 제거한 뒤, list로 반환합니다.

#prepare tokenizer
kiwi = Kiwi()
kiwi.prepare()

#import stopwords
with open('./korean_stopwords.txt', 'rb') as f:
    stopwords = pickle.load(f)
stopwords = set(stopwords)

def tokenize(sent):
    res, score = kiwi.analyze(sent)[0] # 첫번째 결과를 사용
    return [word + ('다' if tag.startswith('V') else '') # 동사에는 '다'를 붙여줌
            for word, tag, _, _ in res
            if not tag.startswith('E') and not tag.startswith('J') and not tag.startswith('S') and word not in stopwords] # 조사, 어미, 특수기호는 제거
@app.callback(
    [
        Output("bank-wordcloud", "figure"),
        Output("bank-treemap", "figure"),
        Output("no-data-alert", "style"),
    ],
    [
     Input('BAR', 'clickData'),   
     Input('Dropdown_Top10_Day_Barstack', 'value')
    ]
)
def update_wordcloud_plot(bar_click, day):
    if bar_click is not None:
        news_for_comment = data_news[data_news.time_written_short == day ]

        master_id = bar_click['points'][0]['y'][0]
        if master_id != '일':
            news_for_comment = [df for i, (doc_id, df) in enumerate(news_for_comment.groupby('master')) if i+1 == int(master_id)][0]
        url_list = [url for url in news_for_comment.in_url if url in data_comment.url.values] 
        df_list = list(map(lambda x : data_comment[data_comment.url == x], url_list))

        comment_for_day_and_master = pd.concat(df_list, ignore_index = True)
        comments_for_count = [' '.join(tokenize(comment)) for comment in  comment_for_day_and_master.content]
        print(comments_for_count)
        comments_word_counter = CountVectorizer(analyzer='word',       
                                token_pattern = '[가-힣]{2,}', max_df = 0.8, min_df = 2)
        comments_word_counter.fit(comments_for_count)
        #plot_data = [(keyword, comments_word_counter.vocabulary_[keyword])for keyword in comments_word_counter.vocabulary_]
        #print(plot_data)
        wordcloud, treemap = plotly_wordcloud(comments_word_counter.vocabulary_)
        alert_style = {"display": "none"}
        if (wordcloud == {}) or (treemap == {}):
            alert_style = {"display": "block"}
        print("redrawing bank-wordcloud...done")
        return (wordcloud, treemap, alert_style)





# ################################################################################################
SEARCH_GRAPH =  dcc.Loading(
     id="loading-search-timeseries_comment-plot", children=[dcc.Graph(id="search-timeseries_comment")], type="default"
)
Search_Card = [
    dbc.CardHeader(html.H5("특정 키워드 관련 내용 추이 보기")),
    
    dbc.CardBody(
        [   dcc.Input(id='my-id', value='추미애', type='text', debounce = True),
            html.Hr(),
            html.Div(id='my-div'),
            html.Hr(),
            SEARCH_GRAPH
           
        ]
    )]



def get_sent_freq_by_day_for_keyword(day, dataset):
    comments_for_url= dataset[dataset['time_written_short'] == day]
    
    n_comments = len(comments_for_url)
    n_comments_positive = len(comments_for_url[comments_for_url.sent_score > 0])
    n_comments_negative = len(comments_for_url[comments_for_url.sent_score < 0])
    n_comments_neutral = n_comments - n_comments_positive - n_comments_negative
    
    return np.array([n_comments_positive, n_comments_negative, n_comments_neutral])

def make_figure_for_search_timeseries(keyword):
    fig_for_keyword = go.Figure()
    comments_for_keyword = data_comment[data_comment.content.str.contains(keyword) | data_comment.title.str.contains(keyword)]
    print(comments_for_keyword)
    sent_freq_list_by_day_for_keyword = list(map(lambda x : get_sent_freq_by_day_for_keyword(x, comments_for_keyword), data_top10_daylist))

    sent_freq_timeseries_positive_for_keyword = list(map(lambda x : x[0], sent_freq_list_by_day_for_keyword))
    sent_freq_timeseries_negative_for_keyword = list(map(lambda x : x[1], sent_freq_list_by_day_for_keyword))
    sent_freq_timeseries_neutral_for_keyword  = list(map(lambda x : x[2], sent_freq_list_by_day_for_keyword))
    sent_freq_timeseries_total_for_keyword    = list(map(np.sum, sent_freq_list_by_day_for_keyword))
 

    trace_positive_for_keyword = go.Scatter(
            x = data_top10_daylist,
            y = sent_freq_timeseries_positive_for_keyword,
            name='긍정',
            )

    trace_negative_for_keyword = go.Scatter(
            x = data_top10_daylist,
            y = sent_freq_timeseries_negative_for_keyword,
            name = '부정',
            )

    trace_neutral_for_keyword = go.Scatter(
            x = data_top10_daylist,  
            y = sent_freq_timeseries_neutral_for_keyword,
            name = '중립',
            )

    trace_total_for_keyword = go.Scatter(
            x = data_top10_daylist,  
            y = sent_freq_timeseries_total_for_keyword,
            name = '일일종합',
            )

    fig_for_keyword.add_trace(trace_positive_for_keyword)
    fig_for_keyword.add_trace(trace_negative_for_keyword)
    fig_for_keyword.add_trace(trace_neutral_for_keyword)
    fig_for_keyword.add_trace(trace_total_for_keyword)
    return fig_for_keyword

@app.callback(
    Output(component_id='search-timeseries_comment', component_property='figure'),
    [Input(component_id='my-id', component_property = 'value')]
)
def update_timeseries_for_search(keyword):
    return make_figure_for_search_timeseries(keyword)
@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property = 'value')]
)
def update_output_div(keyword):
    return '키워드 "{}" 에 대한 뉴스 및 댓글 추이:'.format(keyword)

# ##############################################################################################
# latest_data_comment = data_comment[data_comment.time.str.slice(start = 0, stop = 10) == all_days[-1] ]
# latest_data_comment_top5 = latest_data_comment.sort_values(by = 'like', ascending = False).iloc[:5, :]
# latest_data_comment_bottom5 = latest_data_comment.sort_values(by = 'dislike', ascending = False).iloc[:5, :]

# COMMENT_TOP5_SHOW = dash_table.DataTable(
#     data = latest_data_comment_top5.to_dict('records'),
#     columns=[{'id': c, 'name': c} for c in latest_data_comment_top5.columns]
# )

# COMMENT_BOTTOM5_SHOW = dash_table.DataTable(
#     data = latest_data_comment_bottom5.to_dict('records'),
#     columns=[{'id': c, 'name': c} for c in latest_data_comment_bottom5.columns]
# )

# replys_top5 = []
# for i, top1 in latest_data_comment_top5.iterrows():
    
#     reply_press = top1.press
#     reply_title = top1.title
#     reply_url = top1.url
#     reply_time = top1.time
#     reply_like = top1.like
#     reply_dislike = top1.dislike
#     reply_content = top1.content

#     reply_header = html.Div(
#     children=[
#                             html.H4(children='[{}] {}'.format(reply_press, reply_title)),
#                             html.P(children = '기사 주소: {}'.format(reply_url)),
#                             html.P('댓글 작성 시간: {}'.format(reply_time)),
#                             html.P('좋아요: {}개 / 싫어요: {}개'.format(reply_like, reply_dislike))
#                         ],  style = {'fontSize' : 10})

#     reply_body = html.Div( html.P(reply_content))
#     reply_split = html.Div( html.P('--------------------------------------------------------------------'))
#     reply_one = [reply_header, reply_body, reply_split]
#     replys_top5 = replys_top5 + reply_one

# COMMENT_TOP5_PLOTS = [
#     dbc.CardHeader(html.H5("오늘의 육군 관련 뉴스에 달린 댓글 중 좋아요가 가장 많은 5개")),
#     dbc.Alert(
#         "Not enough data to render comment plots, please adjust the filters",
#         id="no-data-alert-comment-top5",
#         color="warning",
#         style={"display": "none"},
#     ),
#     dbc.CardBody( replys_top5  ),
# ]


# replys_bottom5 = []
# for i, top1 in latest_data_comment_bottom5.iterrows():
    
#     reply_press = top1.press
#     reply_title = top1.title
#     reply_url = top1.url
#     reply_time = top1.time
#     reply_like = top1.like
#     reply_dislike = top1.dislike
#     reply_content = top1.content

#     reply_header = html.Div(
#     children=[
#                             html.H4(children='[{}] {}'.format(reply_press, reply_title)),
#                             html.P(children = '기사 주소: {}'.format(reply_url)),
#                             html.P('댓글 작성 시간: {}'.format(reply_time)),
#                             html.P('좋아요: {}개 / 싫어요: {}개'.format(reply_like, reply_dislike))
#                         ],  style = {'fontSize' : 10})

#     reply_body = html.Div( html.P(reply_content))
#     reply_split = html.Div( html.P('--------------------------------------------------------------------'))
#     reply_one = [reply_header, reply_body, reply_split]
#     replys_bottom5 = replys_bottom5 + reply_one

# COMMENT_BOTTOM5_PLOTS = [
#     dbc.CardHeader(html.H5("오늘의 육군 관련 뉴스에 달린 댓글 중 싫어요가 가장 많은 5개")),
#     dbc.Alert(
#         "Not enough data to render comment plots, please adjust the filters",
#         id="no-data-alert-comment-bottom5",
#         color="warning",
#         style={"display": "none"},
#     ),
#     dbc.CardBody(
        
#             replys_bottom5
        
#     ),
# ]

# ################################################################################################


# LDA_dropdown_day = dcc.Dropdown(id = "day_for_LDA", options = [ {"label": YMD, "value": YMD} for YMD in all_days ], value = all_days[-1])

# LDA_PLOT = dcc.Loading(
#     id="loading-lda-plot", children=[dcc.Graph(id="tsne-lda")], type="default"
# )

# LDA_TABLE = html.Div(
#     id="lda-table-block",
#     children=[
#         dcc.Loading(
#             id="loading-lda-table",
#             children=[
#                 dash_table.DataTable(
#                     id="lda-table",
#                     style_cell_conditional=[
#                         {
#                             "if": {"column_id": "text"},
#                             "textAlign": "left",
#                             "whiteSpace": "normal",
#                             "height": "auto",
#                             "min-width": "80%",
#                         }
#                     ],
#                     style_data_conditional=[
#                         {
#                             "if": {"row_index": "odd"},
#                             "backgroundColor": "rgb(243, 246, 251)",
#                         }
#                     ],
#                     style_cell={
#                         "padding": "16px",
#                         "whiteSpace": "normal",
#                         "height": "auto",
#                         "max-width": "0",
#                     },
#                     style_header={"backgroundColor": "white", "fontWeight": "bold"},
#                     style_data={"whiteSpace": "normal", "height": "auto"},
#                     filter_action="native",
#                     page_action="native",
#                     page_current=0,
#                     page_size=5,
#                     columns=[],
#                     data=[],
#                 )
#             ],
#             type="default",
#         )
#     ],
#     style={"display": "none"},
# )

# COMMENT_TABLE = html.Div(
#     id="comment-table-block",
#     children=[
#         dcc.Loading(
#             id="loading-comment-table",
#             children=[
#                 dash_table.DataTable(
#                     id="comment-table",
#                     style_cell_conditional=[
#                         {
#                             "if": {"column_id": "댓글"},
#                             "textAlign": "left",
#                             "whiteSpace": "normal",
#                             "height": "auto",
#                             "min-width": "60%",
#                         }
#                     ],
#                     style_data_conditional=[
#                         {
#                             "if": {"row_index": "odd"},
#                             "backgroundColor": "rgb(243, 246, 251)",
#                         }
#                     ],
#                     style_cell={
#                         "padding": "16px",
#                         "whiteSpace": "normal",
#                         "height": "auto",
#                         "max-width": "0",
#                     },
#                     style_header={"backgroundColor": "white", "fontWeight": "bold"},
#                     style_data={"whiteSpace": "normal", "height": "auto"},
#                     filter_action="native",
#                     page_action="native",
#                     page_current=0,
#                     page_size=7,
#                     columns=[],
#                     data=[],
#                 )
#             ],
#             type="default",
#         )
#     ],
#     style={"display": "none"},
# )

# LDA_PLOTS = [
#     dbc.CardHeader(html.H5("T-SNE 시각화")),
#     dbc.Alert(
#         "Not enough data to render LDA plots, please adjust the filters",
#         id="no-data-alert-lda",
#         color="warning",
#         style={"display": "none"},
#     ),
#     dbc.CardBody(
#         [
#             html.P(
#                 "날짜를 선택하면 해당일의 기사들 간의 상대적인 거리와 위치를 볼 수 있습니다.",
#                 className="mb-0",
#             ),
#             LDA_dropdown_day,
#             LDA_PLOT,
#             html.Hr(),
#             LDA_TABLE,
#             html.Hr(),
#             COMMENT_TABLE
#         ]
#     ),
# ]



# #####################################################################################################
# ############################################ TIME SERIES ####################################################
# #5. 시계열 그래프

# fig_timeseries_comment = go.Figure()

# data_comment_for_timeseries = data_comment.copy()
# data_comment_for_timeseries['time2'] = data_comment_for_timeseries.time.str.slice(start = 0, stop = 10)
# data_comment_for_timeseries_agg = data_comment_for_timeseries.groupby(by = ['time2'], as_index = False).count()
# print(data_comment_for_timeseries_agg)

# fig_timeseries_comment.add_trace(
#     go.Scatter(
#     x = data_comment_for_timeseries_agg['time2'],
#     y = data_comment_for_timeseries_agg['press'],
#     name = '총 댓글 건수'
# ))


# fig_timeseries_comment.update_xaxes(
#     rangeslider_visible=True,
#     rangeselector=dict(
#         buttons=list([
#             dict(count=1, label="1m", step="month", stepmode="backward"),
#             dict(count=6, label="6m", step="month", stepmode="backward"),
#             dict(count=1, label="YTD", step="year", stepmode="todate"),
#             dict(count=1, label="1y", step="year", stepmode="backward"),
#             dict(step="all")
#         ])
#     )
# )




# ######################################################################################################

# ############################################ PIE ####################################################
# PIE_dropdown_day = dcc.Dropdown(id = "day_for_pie", options = [ {"label": YMD, "value": YMD} for YMD in all_days ], value = all_days[-1])
# PIE_dropdown_topic = dcc.Dropdown(id = "topic_for_pie") 
# PIE_PLOT = dcc.Loading(
#      id="loading-PIE-plot", children=[dcc.Graph(id="PIE")], type="default"
# )
# PIE_PLOTS = [
#     dbc.CardHeader(html.H5("육군 관련 보도 감성분석 파이 그래프")),
#     dbc.Alert(
#         "Not enough data to render PIE plots, please adjust the filters",
#         id="no-data-alert-PIE",
#         color="warning",
#         style={"display": "none"},
#     ),
#     dbc.CardBody(
#         [
#             html.P(
#                 '날짜와 주제를 선택하세요.',
#                 className="mb-0",
#             ),
#            dbc.Row(
#                 [ dbc.Col(PIE_dropdown_day), dbc.Col(PIE_dropdown_topic) ]
#                 ),
            
#             PIE_PLOT,
#             html.Hr()
#         ]
#     ),
# ]
# ######################################################################################################

###########################################################################

######################################################################
BODY = basic.bodymaker([
    Daily_Top10_Card, 
    Timeseries_Plot_Card,
    Daily_Top10_Barstack_Card,
    Wordcloud_Card,
    Search_Card
    # SEARCH,
    # PIE_PLOTS,
    # WORDCLOUD_PLOTS,
    # LDA_PLOTS,
    # TIMESERIES_PLOTS,
    # timeseries_comment_PLOTS
])

app.layout = html.Div([
    NAVBAR, BODY,

])
#########################################################


















################################################################################
#CALLBACKS


################################################################################
#BARSTACK




# ########################################################################################################################






# #######################################################################################################################
# @app.callback(
#     [Output("topic", "options")],
#     [Input("day", "value")]
# )
# def set_topic_options(selected_day):
#     today_data = data_topic[ (data_topic.time == selected_day) ]
#     #print('today_data', today_data.label)
#     opp = [[ {"label": '{}번째 주제:{}'.format(i, today_data[today_data.label == i].top3.item()), "value": i} for i in today_data.label]] #one-element list, whose the only element is a 6-element list.
#     #print(opp)
#     return opp 

    
# @app.callback(
#     Output('topic', 'value'),
#     [Input('topic', 'options')])
# def set_topic_value(available_options):
#     return available_options[0]['value']









# @app.callback(
#     [
       
#         Output("tsne-lda", "figure"),
#         Output("no-data-alert-lda", "style")],
#     [Input("day_for_LDA", "value")],
# )
# def update_lda_table(day):
#     """ Update LDA table and scatter plot based on precomputed data """
#     data_today = data[data.time == day]
#     lda_scatter_figure = populate_lda_scatter(data_today)
#     return lda_scatter_figure, {"display": "none"}


# @app.callback(
#     [
#         Output("lda-table", "data"),
#         Output("lda-table", "columns"),
#         Output("lda-table-block", "style"),
#         Output("comment-table", "data"),
#         Output("comment-table", "columns"),
#         Output("comment-table-block", "style")],
#     [Input("tsne-lda", "clickData")]
# )
# def filter_table_on_scatter_click(tsne_click):
#     """ TODO """
#     if tsne_click is not None:
#         click_item = str(tsne_click["points"][0]["hovertext"]).split('@')
#         selected_doc_no = click_item[0]
#         selected_press = click_item[1]
#         selected_title = click_item[2]
        
        
#         data_today_clicked = data[data['doc_id'] == int(selected_doc_no)].T
#         data_today_clicked.reset_index(drop = False, inplace = True)
#         data_today_clicked.columns = ['item', 'text']
#         columns_news = [{"name": 'item', "id": 'item'}, {"name": 'text', "id": 'text'}]
#         data_lda_table = data_today_clicked.to_dict("records")
        
        
#         comment_today_clicked = data_comment[data_comment['doc_id'] == int(selected_doc_no)].iloc[:,3:8]
#         comment_today_clicked.columns = ['댓글', '좋아요', '싫어요', '작성시간', '답글']
#         if len(comment_today_clicked) == 0:
#             comment_today_clicked = comment_today_clicked.append(pd.DataFrame(['댓글 없음', '','','',''], columns = ['댓글', '좋아요', '싫어요', '작성시간', '답글']), ignore_index = True)
        
#         columns_comment = [{"name": i, "id": i} for i in comment_today_clicked.columns]
#         comment_table = comment_today_clicked.to_dict("records")

#         return (data_lda_table, columns_news,  {"display": "block"} , comment_table, columns_comment, {"display": "block"})
#     else:
#         return ( [], [], {"display": "none"} , [], [], {"display": "none"})
        



# #PIE
# @app.callback(
#     [Output("topic_for_pie", "options")],
#     [Input("day_for_pie", "value")]
# )
# def set_topic_options(selected_day):
#     today_data = data_topic[ (data_topic.time == selected_day) ]
#     #print('today_data', today_data.label)
#     opp = [[{'label': '전체', 'value' : -1}] + [ {"label": '{}번째 주제:{}'.format(i, today_data[today_data.label == i].top3.item()), "value": i} for i in today_data.label]] #one-element list, whose the only element is a 6-element list.
#     #print(opp)
#     return opp 

# @app.callback(
#     Output('topic_for_pie', 'value'),
#     [Input('topic_for_pie', 'options')])
# def set_topic_value(available_options):
#     return available_options[0]['value']


# @app.callback(
#     Output("PIE", "figure"),
#     [ Input("day_for_pie", "value"),
#     Input("topic_for_pie", "value")]
# )
# def update_pie_plot(selected_day, selected_topic):
#     """ Callback to rerender pie plot """
#     if selected_topic == -1:
#         data_today_sent = data_sent_timeseries[data_sent_timeseries.time == selected_day]
#         sent_values = list(data_today_sent.iloc[0,1:-1])
#     else:
#         data_today = data[(data.time == selected_day) & (data.label == selected_topic)]
#         #print(data_today)
#         pos = len(data_today[data_today.sent_score > 0])
#         neu = len(data_today[data_today.sent_score == 0])
#         neg = len(data_today[data_today.sent_score < 0])
#         sent_values = [pos, neu, neg]
    
#     fig = go.Figure()
#     #print(sent_values)
#     fig.add_trace(
#         go.Pie(labels = ['긍정','중립','부정'], values = sent_values))
#     #print(fig)
#     return fig



if __name__ == '__main__': #이게 callback보다 앞에 와야 callback이 디버깅됨
    app.run_server()

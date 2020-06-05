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
data = work.merge('./NN')
data_topic = work.merge('./LDAs')



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


all_days = np.sort(data.time.unique())
wordcloud_dropdown_day = dcc.Dropdown(id = "day", options = [ {"label": YMD, "value": YMD} for YMD in all_days ], value = all_days[0])
wordcloud_dropdown_topic = dcc.Dropdown(id = "topic", options = [{'label': 0, 'value':0}], value = 0) 
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
            dbc.Row(),
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

#5. 시계열 그래프
fig5 = go.Figure()

df1 = pd.read_csv('D:/crawling/finance-charts-apple.csv')

fig5.add_trace(
   
    #go.Bar(x=freq["x"][0:10],y=freq["Country"][0:10], marker=dict(color="crimson"), showlegend=False),
    go.Scatter(
    x = df1['Date'],
    y = df1['mavg']
)
)

fig5.add_trace(
  
    #go.Bar(x=freq["x"][0:10],y=freq["Country"][0:10], marker=dict(color="crimson"), showlegend=False),
    go.Scatter(
    x = df1['Date'],
    y = df1['AAPL.High']
)
)

fig5.update_xaxes(
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

fig5.update_layout( title='지난 1년간 육군 관련 보도 감성 그래프(더미 데이터)',
font=dict(family="NanumBarunGothic", size=16)
)


BODY = dbc.Container(
    [
        
        dbc.Card(WORDCLOUD_PLOTS),
        dbc.Row([dbc.Col([dbc.Card(LDA_PLOTS)])], style={"marginTop": 50}),
    ],
    className="mt-12",
)

f_app = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server = f_app)

app.layout = html.Div(children=[NAVBAR, BODY, dcc.Graph(figure=fig5)])


if __name__ == '__main__':
    
    app.run_server(debug=True, dev_tools_hot_reload = True)



################################################################################
#CALLBACKS

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
    plot_data = eval(data_topic[(data_topic.time == selected_day) & (data_topic.topic == topic_no)].iloc[0,0])

    
    
    wordcloud, frequency_figure, treemap = plotly_wordcloud(dict(plot_data))
    alert_style = {"display": "none"}
    if (wordcloud == {}) or (frequency_figure == {}) or (treemap == {}):
        alert_style = {"display": "block"}
    print("redrawing bank-wordcloud...done")
    return (wordcloud, frequency_figure, treemap, alert_style)


@app.callback(
    [Output("topic", "options"),
     Output("topic", "value")],
    [Input("day", "value")]
)
def set_topic_options(selected_day):
    today_data = data_topic[ (data_topic.time == selected_day) ]
    options_for_today = [ {"label": '{}번째 주제'.format(i), "value": i} for i in today_data.topic]
    return options_for_today, 0




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
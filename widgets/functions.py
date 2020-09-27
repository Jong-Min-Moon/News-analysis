import pandas as pd
import dash_table as dt
import sqlite3
def generate_Top10_Table(selected_day):
    con = sqlite3.connect('./rokanews.db')
    df = pd.read_sql('SELECT title, num FROM pagerank WHERE time_written = "{}"'.format(selected_day), con)[:10]
    df = pd.concat([pd.Series(list(range(1,len(df)+1))), df], axis=1)
    df.columns = [' ', '주제', '기사 갯수']
    con.close()

    return_table = dt.DataTable(
        id = 'table',
        style_cell={
            'padding': '15px',
            'width': 'auto',
            'textAlign': 'center'
        },
        style_cell_conditional=[
            {
                'if': {'row_index': 'even'},
                'backgroundColor': '#f9f9f9'
            }
        ],
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows")
    
    )
    return return_table
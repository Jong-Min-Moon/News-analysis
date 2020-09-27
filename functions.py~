import pandas as pd
import dash_table as dt

def generate_Top10_Table(selected_day):
    con = sqlite3.connect('./rokanews.db')
    df= pd.read_sql('SELECT * FROM pagerank WHERE time = {}'.format(selected_day), con)
    con.close()

    return dt.DataTable(
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
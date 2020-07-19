import pandas as pd
import dash_table as dt

def generate_table(df):
    data = {
       '' : list(range(1,10+1)),
       'b' : [2,3,4,5],
       'c' : [3,4,5,1],

    }

    df = pd.DataFrame(
        data=data
    )

    
    return dt.DataTable(
        id='table',
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
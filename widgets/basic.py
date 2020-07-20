import dash_bootstrap_components as dbc







def bodymaker(content_list):
    #위젯(cardheader/cardbody로 된 리스트)들을 리스트로 넣어주면 BODY를 만들어 주는 함수
    card_list = [ dbc.Card( content_list[0] ) ]

    for i in range(1,len(content_list)):
        card_list.append(
            dbc.Row( [ dbc.Col( [dbc.Card( content_list[i] )] ) ], style = {"marginTop": 50} ),
        )

    return dbc.Container( card_list, className="mt-12")
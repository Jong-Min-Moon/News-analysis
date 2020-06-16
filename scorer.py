import pandas as pd
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic



news = pd.read_csv( 'sent_drop_test.csv' )
news_titles = news[['press', 'title', 'time']]
df = pd.DataFrame({'a': ['Mary', 'Jim'],
                   'b': [100, 200],
                   'c': ['a', 'b']})

form_class = uic.loadUiType("uiui.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        
        self.article_getter = {'num_article' : 20, 'pos_neg' : 1}
        self.lineEdit.returnPressed.connect(self.lineEditChanged)

        self.pushButton.clicked.connect(self.get_articles)
        
        #긍정/부정 체크 버튼
        self.radioButton.setChecked(True)
        self.radioButton.clicked.connect(self.radioButtonClicked)
        self.radioButton_2.clicked.connect(self.radioButtonClicked)

        #점수 매기기 시작 버튼
        self.pushButton_2.clicked.connect(self.start_scoring)

        #분류 버튼
        self.pushButton_3.clicked.connect(self.score_pos)
        self.pushButton_4.clicked.connect(self.score_neg)
        self.pushButton_5.clicked.connect(self.score_neu)
        self.pushButton_6.clicked.connect(self.score_pass)
        self.pushButton_7.clicked.connect(self.score_delete)
    def get_articles(self):
        self.temp_news = news[ (news.sent_score * self.article_getter['pos_neg']) > 0]
        print(len(self.temp_news))
        self.temp_news = self.temp_news[['press', 'title', 'time', 'sent_score']]
        QMessageBox.about(self, "message", "기사를 가져왔습니다.")
        for i in range(self.article_getter['num_article']):
            for j in range(3):
                this_item = self.temp_news.iloc[i,j]
                self.tableWidget.setItem(i, j, QTableWidgetItem(this_item))
    
    def lineEditChanged(self):
        self.article_getter['num_article'] = int(self.lineEdit.text())

    #긍정/부정 체크 버튼
    def radioButtonClicked(self):
        if self.radioButton.isChecked():
            self.article_getter['pos_neg'] = 1
            print(self.article_getter['pos_neg'])
        else:
            self.article_getter['pos_neg'] = -1
            print(self.article_getter['pos_neg'])

    #점수 매기기 시작 버튼
    def start_scoring(self):
        self.idx_list = self.temp_news.index.tolist()
        self.idx_now = self.idx_list[0]
        self.order_now = 0
        self.score_result = []
        content_now = '\n'.join( [str(self.order_now), news.loc[self.idx_now, 'title'], news.loc[self.idx_now, 'time'],  news.loc[self.idx_now, 'content']] )
        self.textBrowser.setPlainText(content_now)


################################# 분류 버튼 ###########################################
    def score_pos(self):
        self.score_result.append('p')
        print(self.score_result)
        #다음 기사로
        self.order_now += 1
        self.idx_now = self.idx_list[self.order_now]
        content_now = '\n'.join( [str(self.order_now), news.loc[self.idx_now, 'title'], news.loc[self.idx_now, 'time'],  news.loc[self.idx_now, 'content']] )
        self.textBrowser.setPlainText(content_now)

    def score_neg(self):
        self.score_result.append('n')
        print(self.score_result)
        #다음 기사로
        self.order_now += 1
        self.idx_now = self.idx_list[self.order_now]
        content_now = '\n'.join( [str(self.order_now), news.loc[self.idx_now, 'title'], news.loc[self.idx_now, 'time'],  news.loc[self.idx_now, 'content']] )
        self.textBrowser.setPlainText(content_now)
    
    def score_neu(self):
        self.score_result.append('z')
        print(self.score_result)
        #다음 기사로
        self.order_now += 1
        self.idx_now = self.idx_list[self.order_now]
        content_now = '\n'.join( [str(self.order_now), news.loc[self.idx_now, 'title'], news.loc[self.idx_now, 'time'],  news.loc[self.idx_now, 'content']] )
        self.textBrowser.setPlainText(content_now)

    def score_pass(self):
        self.score_result.append('')
        print(self.score_result)
        #다음 기사로
        self.order_now += 1
        self.idx_now = self.idx_list[self.order_now]
        content_now = '\n'.join( [str(self.order_now), news.loc[self.idx_now, 'title'], news.loc[self.idx_now, 'time'],  news.loc[self.idx_now, 'content']] )
        self.textBrowser.setPlainText(content_now)

    def score_delete(self):
        self.score_result.append('d')
        print(self.score_result)
        #다음 기사로
        self.order_now += 1
        self.idx_now = self.idx_list[self.order_now]
        content_now = '\n'.join( [str(self.order_now), news.loc[self.idx_now, 'title'], news.loc[self.idx_now, 'time'],  news.loc[self.idx_now, 'content']] )
        self.textBrowser.setPlainText(content_now)
#################################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
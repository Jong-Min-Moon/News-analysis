import pandas as pd
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sqlite3
import time
con = sqlite3.connect('D:/armynews.db')





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
        self.pushButton_8.clicked.connect(self.update_table)

    def get_articles(self):
        self.news = pd.read_sql('SELECT * FROM news WHERE sent_score * {} > 0 AND label IS NULL LIMIT {}'.format(self.article_getter['pos_neg'], self.article_getter['num_article']), con, index_col = 'idx')
        #self.temp_news = news[ (news.sent_score * ) > 0]
        temp_news = self.news[['press', 'title', 'time', 'sent_score']]
        QMessageBox.about(self, "message", "기사를 가져왔습니다.")

        for i in range(100):
            for j in range(4):
                self.tableWidget.setItem(i, j, QTableWidgetItem(''))
        
        for i in range(self.article_getter['num_article']):
            for j in range(3):
                print(i, j)
                this_item = temp_news.iloc[i,j]
                self.tableWidget.setItem(i, j, QTableWidgetItem(this_item))
    
    def lineEditChanged(self):
        try:
            item_number = int(self.lineEdit.text())
            self.article_getter['num_article'] = int(self.lineEdit.text())
        except:
            QMessageBox.about(self, "message", "정수만 입력하세요.")

            


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
        self.idx_list = self.news.index.tolist()
        self.idx_now = self.idx_list[0]
        self.order_now = 0
        self.score_result = []
        content_now = '\n'.join( [str(self.order_now + 1), self.news.loc[self.idx_now, 'title'], self.news.loc[self.idx_now, 'time'],  self.news.loc[self.idx_now, 'content']] )
        self.textBrowser.setPlainText(content_now)


################################# 분류 버튼 ###########################################
    def score_pos(self):
        if self.order_now >= self.article_getter['num_article']:
            QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
        else:
            self.score_result.append('p')
            print(self.score_result)
            #다음 기사로
            self.order_now += 1
            if self.order_now >= self.article_getter['num_article']:
                QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
            else:
                self.idx_now = self.idx_list[self.order_now]
                content_now = '\n'.join( [str(self.order_now + 1), self.news.loc[self.idx_now, 'title'], self.news.loc[self.idx_now, 'time'],  self.news.loc[self.idx_now, 'content']] )
                self.textBrowser.setPlainText(content_now)

    def score_neg(self):
        if self.order_now >= self.article_getter['num_article'] :
            QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
        else:
            self.score_result.append('n')
            print(self.score_result)
            #다음 기사로
            self.order_now += 1
            if self.order_now >= self.article_getter['num_article']:
                QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
            else:
                self.idx_now = self.idx_list[self.order_now]
                content_now = '\n'.join( [str(self.order_now + 1), self.news.loc[self.idx_now, 'title'], self.news.loc[self.idx_now, 'time'],  self.news.loc[self.idx_now, 'content']] )
                self.textBrowser.setPlainText(content_now)
    
    def score_neu(self):
        if self.order_now >= self.article_getter['num_article'] :
            QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
        else:
            self.score_result.append('z')
            print(self.score_result)
            #다음 기사로
            self.order_now += 1
            if self.order_now >= self.article_getter['num_article']:
                QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
            else:
                self.idx_now = self.idx_list[self.order_now]
                content_now = '\n'.join( [str(self.order_now + 1), self.news.loc[self.idx_now, 'title'], self.news.loc[self.idx_now, 'time'],  self.news.loc[self.idx_now, 'content']] )
                self.textBrowser.setPlainText(content_now)

    def score_pass(self):
        if self.order_now >= self.article_getter['num_article']:
            QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
        else:
            self.score_result.append('NULL')
            print(self.score_result)
            #다음 기사로
            self.order_now += 1
            if self.order_now >= self.article_getter['num_article']:
                QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
            else:
                self.idx_now = self.idx_list[self.order_now]
                content_now = '\n'.join( [str(self.order_now + 1), self.news.loc[self.idx_now, 'title'], self.news.loc[self.idx_now, 'time'],  self.news.loc[self.idx_now, 'content']] )
                self.textBrowser.setPlainText(content_now)

    def score_delete(self):
        if self.order_now >= self.article_getter['num_article']:
            QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
        else:
            self.score_result.append('d')
            print(self.score_result)
            #다음 기사로
            self.order_now += 1
            if self.order_now >= self.article_getter['num_article']:
                QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
            else:
                self.idx_now = self.idx_list[self.order_now]
                content_now = '\n'.join( [str(self.order_now + 1), self.news.loc[self.idx_now, 'title'], self.news.loc[self.idx_now, 'time'],  self.news.loc[self.idx_now, 'content']] )
                self.textBrowser.setPlainText(content_now)

################################# 저장 버튼 ###########################################
    def update_table(self):
        for i in range(len(self.idx_list)):
            # 레코드 갱신
            self.tableWidget.setItem(i, 3, QTableWidgetItem(self.score_result[i]))
            time.sleep(2)
            
            sql_query = "UPDATE news SET label = '{}' WHERE idx = {}".format(self.score_result[i], self.idx_list[i])
            cs = con.execute(sql_query)

            # 변경된 row의 수를 cursor.rowcount로 확인할 수 있다.
            # 전체 내역을 다시 출력하여 확인해본다.
            print(f'{cs.rowcount} rows are updated.')
            con.commit()
#################################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
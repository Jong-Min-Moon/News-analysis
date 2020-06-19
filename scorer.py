import pandas as pd
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sqlite3
import time
import math
con = sqlite3.connect('D:/armynews.db')





form_class = uic.loadUiType("uiui.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.Can_I_score = 0
        self.Can_I_start = 0

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
        self.news = pd.read_sql('SELECT * FROM news WHERE sent_score * {} > 0 AND label IS NULL ORDER BY sent_score * {} DESC LIMIT {}'.format(self.article_getter['pos_neg'], self.article_getter['pos_neg'], self.article_getter['num_article']), con, index_col = 'idx')
        
        temp_news = self.news[['press', 'title', 'time', 'sent_score']]
        QMessageBox.about(self, "message", "기사를 가져왔습니다.")

        for i in range(100):
            for j in range(4):
                self.tableWidget.setItem(i, j, QTableWidgetItem(''))
        
            

        for i in range(self.article_getter['num_article']):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(temp_news.index[i])))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(str(round(temp_news.iloc[i,3],3))))
            for j in range(3):
                print(i, j)
                this_item = temp_news.iloc[i,j]
                self.tableWidget.setItem(i, j, QTableWidgetItem(this_item))
    
    def lineEditChanged(self):
        try:
            item_number = int(self.lineEdit.text())
            self.article_getter['num_article'] = int(self.lineEdit.text())
            self.Can_I_start = 1
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
        if self.Can_I_start == 1:
            self.Can_I_score = 1
            self.idx_list = self.news.index.tolist()
            self.idx_now = self.idx_list[0]
            self.order_now = 0
            self.score_result = []
            content_now = '\n'.join( ['인덱스:' + str(self.idx_now), str(self.order_now + 1) + '번째 기사', self.news.loc[self.idx_now, 'title'], self.news.loc[self.idx_now, 'time'],  self.news.loc[self.idx_now, 'content']] )
            self.textBrowser.setPlainText(content_now)
        else:
            QMessageBox.about(self, "message", "'기사 가져오기'를 먼저 수행하세요.")


################################# 분류 버튼 ###########################################
    def score_pos(self):
        if self.Can_I_score == 1:
            if self.order_now >= self.article_getter['num_article']:
                QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
            else:
                self.score_result.append(1)
                print(self.score_result)
                #다음 기사로
                self.order_now += 1
                if self.order_now >= self.article_getter['num_article']:
                    QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
                else:
                    self.idx_now = self.idx_list[self.order_now]
                    content_now = '\n'.join( ['인덱스:' + str(self.idx_now), str(self.order_now + 1) + '번째 기사', self.news.loc[self.idx_now, 'title'], self.news.loc[self.idx_now, 'time'],  self.news.loc[self.idx_now, 'content']] )
                    self.textBrowser.setPlainText(content_now)
        else:
            QMessageBox.about(self, "message", "'점수 매기기 시작' 버튼을 먼저 눌러주세요.")

    def score_neg(self):
        if self.Can_I_score == 1:
            if self.order_now >= self.article_getter['num_article'] :
                QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
            else:
                self.score_result.append(-1)
                print(self.score_result)
                #다음 기사로
                self.order_now += 1
                if self.order_now >= self.article_getter['num_article']:
                    QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
                else:
                    self.idx_now = self.idx_list[self.order_now]
                    content_now = '\n'.join( ['인덱스:' + str(self.idx_now), str(self.order_now + 1) + '번째 기사', self.news.loc[self.idx_now, 'title'], self.news.loc[self.idx_now, 'time'],  self.news.loc[self.idx_now, 'content']] )
                    self.textBrowser.setPlainText(content_now)
        else:
            QMessageBox.about(self, "message", "'점수 매기기 시작' 버튼을 먼저 눌러주세요.")    
    def score_neu(self):
        if self.Can_I_score == 1:
            if self.order_now >= self.article_getter['num_article'] :
                QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
            else:
                self.score_result.append(0)
                print(self.score_result)
                #다음 기사로
                self.order_now += 1
                if self.order_now >= self.article_getter['num_article']:
                    QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
                else:
                    self.idx_now = self.idx_list[self.order_now]
                    content_now = '\n'.join( ['인덱스:' + str(self.idx_now), str(self.order_now + 1) + '번째 기사', self.news.loc[self.idx_now, 'title'], self.news.loc[self.idx_now, 'time'],  self.news.loc[self.idx_now, 'content']] )
                    self.textBrowser.setPlainText(content_now)
        else:
            QMessageBox.about(self, "message", "'점수 매기기 시작' 버튼을 먼저 눌러주세요.")    

    def score_pass(self):
        if self.Can_I_score == 1:
            if self.order_now >= self.article_getter['num_article']:
                QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
            else:
                self.score_result.append(2)
                print(self.score_result)
                #다음 기사로
                self.order_now += 1
                if self.order_now >= self.article_getter['num_article']:
                    QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
                else:
                    self.idx_now = self.idx_list[self.order_now]
                    content_now = '\n'.join( ['인덱스:' + str(self.idx_now), str(self.order_now + 1) + '번째 기사', self.news.loc[self.idx_now, 'title'], self.news.loc[self.idx_now, 'time'],  self.news.loc[self.idx_now, 'content']] )
                    self.textBrowser.setPlainText(content_now)
        else:
            QMessageBox.about(self, "message", "'점수 매기기 시작' 버튼을 먼저 눌러주세요.")    

    def score_delete(self):
        if self.Can_I_score == 1:
            if self.order_now >= self.article_getter['num_article']:
                QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
            else:
                self.score_result.append(3)
                print(self.score_result)
                #다음 기사로
                self.order_now += 1
                if self.order_now >= self.article_getter['num_article']:
                    QMessageBox.about(self, "message", "모든 기사를 레이블링했습니다.")
                else:
                    self.idx_now = self.idx_list[self.order_now]
                    content_now = '\n'.join( ['인덱스:' + str(self.idx_now), str(self.order_now + 1) + '번째 기사', self.news.loc[self.idx_now, 'title'], self.news.loc[self.idx_now, 'time'],  self.news.loc[self.idx_now, 'content']] )
                    self.textBrowser.setPlainText(content_now)
        else:
            QMessageBox.about(self, "message", "'점수 매기기 시작' 버튼을 먼저 눌러주세요.")    

################################# 저장 버튼 ###########################################
    def update_table(self):
        case_query = ''
        for i in range(len(self.idx_list)):
            self.tableWidget.setItem(i, 5, QTableWidgetItem(str(self.score_result[i])))
            case_query = case_query + " WHEN idx = {} THEN {}".format(self.idx_list[i], self.score_result[i] )
            #sql_query = "UPDATE news SET label = '{}' WHERE idx = {}".format(self.score_result[i], self.idx_list[i])
            #sql_query = "UPDATE news SET label = '{}' WHERE idx = {}".format(, 
        sql_query = 'UPDATE news SET label = CASE{} END WHERE idx in {}'.format( case_query, tuple(self.idx_list) )
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
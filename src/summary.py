# coding: utf-8
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from PyQt5 import QtGui
from pr import *
from data import *
from document import *
import codecs
import json
from lib.util.datatype import AttribDict
from lib.util.db import summary2detail, insertDB, exportDB
import traceback
from copy import deepcopy


class ScanSignals(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(AttribDict)
    targetchanged = pyqtSignal(str, str)
    statuschanged = pyqtSignal(bool)
    error = pyqtSignal(tuple)


class ScanWorker(QRunnable):

    def __init__(self, fn, host):
        QThread.__init__(self)

        self.single_scan_target = AttribDict()
        self.single_scan_target.target = host
        self.single_scan_target.plugin = fn
        # self.single_scan_target.result = {}
        self._status = False   # run status
        self.signals = ScanSignals()

    # @property
    # def status(self):
    #     return self._status
    #
    # @status.setter
    # def status(self, new_status):
    #     if new_status != self._status:
    #         self._status = new_status
    #         self.signals.statuschanged.emit(new_status)

    def run(self):
        self.status = True

        try:
            self.single_scan_target.result = self.single_scan_target.plugin(
                self.single_scan_target.target)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(deepcopy(self.single_scan_target))
        finally:
            self.signals.finished.emit()

            # self.status = False


class Document:
    def __init__(self, n, sentence, summarys):
        self.number = n
        self.text = sentence
        self.summary = summarys


def write(test_dir):
    tests = read_data(test_dir)
    summarys = pr_summ_exact(tests, 3)
    golds, texts = get_golds(tests)  # references

    i = 1
    d = {}
    for text, summ in zip(texts, summarys):
        d["index"] = i
        d["text"] = text.replace(' ', '')
        d["summary"] = summ.replace(' ', '')
        i += 1
        path = '../data/summ.txt'
        with codecs.open(path, 'a', 'utf-8') as f:
            s = json.dumps(d, ensure_ascii=False)
            f.write(s)
            f.write('\n')
    return i

# path = '../data/summ.txt'
def read(path):
    results = []
    for line in codecs.open(path, 'r', 'utf-8'):
        d = json.loads(line)
        i = d['index']
        text = d['text']
        summary = d['summary']
        results.append(Document(i, text, summary))
    return results


current_directory = os.path.dirname(os.path.abspath(__file__))
summ_form, base_class = loadUiType(os.path.join(current_directory, 'mainwindow.ui'))
class MainWindow(QMainWindow, summ_form):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center()) # Center Display
        self._scan_threadpool = QThreadPool()

    @pyqtSlot()
    def on_pushButton_clicked(self):
        """训练集打开文件夹，文件路径显示到lineEdit中"""
        fileName1 = QFileDialog.getExistingDirectory(self, "选取文件夹", "./")
        # fileName1, filetype = QFileDialog.getOpenFileName(self, "选取文件", "./", "All Files (*);;Text Files (*.txt)")
        # 设置文件扩展名过滤,注意用双分号间隔
        if fileName1:
            self.lineEdit.setText(fileName1)
            self.lineEdit.setStyleSheet('color: black')
        else:
            self.lineEdit.setText("None")

    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        """摘要集打开文件，文件路径显示到lineEdit中"""
        fileName1, filetype = QFileDialog.getOpenFileName(self, "选取文件", "./", "All Files (*);;Text Files (*.txt)")
        # 设置文件扩展名过滤,注意用双分号间隔
        if fileName1:
            self.lineEdit_2.setText(fileName1)
            self.lineEdit_2.setStyleSheet('color: black')
        else:
            self.lineEdit_2.setText("None")

    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        """点击开始按钮，开始计时"""
        time = QTime.currentTime()  # 获取当前时间
        time_text = time.toString(Qt.DefaultLocaleLongDate)
        self.lcdNumber.display(time_text)

    @pyqtSlot()
    def on_startButton_clicked(self):
        """开始预测"""
        if self.lineEdit_2.text():
            self.label_2.setText("亲，已经预测过了呐，快去查看吧！")
            self.label_2.setStyleSheet('color: blue')
        else:
            if self.lineEdit.text():
                test_dir = self.lineEdit.text()
                summarywork = ScanWorker(write, test_dir)
                summarywork.signals.result.connect(self.onwriteFinshed)
                self._scan_threadpool.start(summarywork)
            else:
                self.lineEdit.setText("请选择训练集！")
                self.lineEdit.setStyleSheet('color: red')

    def onwriteFinshed(self, results):
        print(results.result)
        if results.result:
            self.label_2.setText("当当当，预测完成喽，快去查看吧！")
            self.label_2.setStyleSheet('color: blue')
        else:
            self.label_2.setText("警告，警告，预测出错！")
            self.label_2.setStyleSheet('color: red')

    @pyqtSlot()
    def on_pushButton_4_clicked(self):
        """展示，文件路径显示到lineEdit中"""
        if self.lineEdit_3.text():
            if self.lineEdit_2.text():
                path = self.lineEdit_2.text()
                summarywork = ScanWorker(read, path)
                summarywork.signals.result.connect(self.onSummaryFinished)
                self._scan_threadpool.start(summarywork)
            else:
                self.lineEdit_2.setText("请选择正确的摘要集!")
                self.lineEdit_2.setStyleSheet('color: red')
                self.textBrowser.setText('')
                self.textBrowser_2.setText('')
        else:
            self.lineEdit_3.setText("请输入正确的ID！")
            self.lineEdit_3.setStyleSheet('color: red')
            self.textBrowser.setText('')
            self.textBrowser_2.setText('')

    def onSummaryFinished(self, results):
        number = self.lineEdit_3.text()
        print(results)

        for doc in results.result:
            if int(number) == int(doc.number):
                text = doc.text.replace(' ', '')
                summ = doc.summary.replace(' ', '')
                self.textBrowser.setText(text)
                self.textBrowser_2.setText(summ)
                break


if __name__ == "__main__":

    app = QApplication(sys.argv)
    scanform = MainWindow()
    scanform.show()
    sys.exit(app.exec_())

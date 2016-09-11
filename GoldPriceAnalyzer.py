import sys
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=7, height=4, dpi=110):

        self.fig = Figure(figsize=(width, height), dpi=dpi, edgecolor='k', linewidth=1)
        self.axes = self.fig.add_subplot(111)

        # We want the axes cleared every time plot() is called
        self.axes.hold(True)
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

        self.x, self.price_in_list, self.price_out_list = ([], [], [])
        self.update_data()

    def update_data(self):
        conn = sqlite3.connect('goldprice.sqlite')
        cur = conn.cursor()

        cur.execute('SELECT * FROM Gold ORDER BY Date ASC')
        all_fetch = cur.fetchall()

        date_list, self.price_in_list, self.price_out_list = ([], [], [])

        for date, price_out, price_in in all_fetch:
            date_list.append(date)
            self.price_out_list.append(price_out)
            self.price_in_list.append(price_in)

        converted_dates = map(datetime.strptime, date_list, len(date_list) * ['%Y/%m/%d'])
        self.num_date_list = list(converted_dates)

    def get_price_data(self):
        return self.num_date_list, self.price_in_list, self.price_out_list

    def calculate_start_date_index(self, interval):
        start_date = self.num_date_list[-1] + relativedelta(months=-interval)
        while True:
            if start_date in self.num_date_list:
                return self.num_date_list.index(start_date)
            start_date -= relativedelta(days=1)


class GoldPriceCanvas(MplCanvas):
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)
        MplCanvas.setStatusTip(self, '銀行賣出價格')
        self.date, self.price_in_list, self.price_out_list = self.get_price_data()
        self.update_figure(1, 12)

    def update_figure(self, canvas_price_out, interval):
        start_date_index = self.calculate_start_date_index(interval)
        self.axes.clear()
        if canvas_price_out:
            self.axes.plot(self.date[start_date_index:], self.price_out_list[start_date_index:], 'r', color='#B99A1D')
            self.axes.patch.set_facecolor('#E3F0FD')
            self.fig.set_facecolor('#CBD7E6')
        else:
            self.axes.plot(self.date[start_date_index:], self.price_in_list[start_date_index:], 'r', color='#FF53D5')
            self.axes.patch.set_facecolor('#FFECFF')
            self.fig.set_facecolor('#FFC8FF')
        self.draw()


class AppWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.init_ui()

        self.main_widget = QtGui.QWidget(self)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.layout = QtGui.QVBoxLayout(self.main_widget)
        self.price_canvas = 1
        self.canvas_interval = 12
        self.gold_price_canvas = GoldPriceCanvas(self.main_widget)
        self.layout.addWidget(self.gold_price_canvas)

        priceInAction = QtGui.QAction('&銀行買入', self)
        priceInAction.setStatusTip("更改顯示的價格為銀行買入價格")
        priceInAction.triggered.connect(self.change_canvas_price_in)

        priceOutAction = QtGui.QAction('&銀行賣出', self)
        priceOutAction.setStatusTip("更改顯示的價格為銀行賣出價格")
        priceOutAction.triggered.connect(self.change_canvas_price_out)

        intervalAction3 = QtGui.QAction('&最近3個月', self)
        intervalAction3.setStatusTip("更改顯示期間為最近的3個月")
        intervalAction3.triggered.connect(self.update_figure_interval3)

        intervalAction6 = QtGui.QAction('&最近6個月', self)
        intervalAction6.setStatusTip("更改顯示期間為最近的6個月")
        intervalAction6.triggered.connect(self.update_figure_interval6)

        intervalAction12 = QtGui.QAction('&最近1年', self)
        intervalAction12.setStatusTip("更改顯示期間為最近的1年")
        intervalAction12.triggered.connect(self.update_figure_interval12)

        self.statusBar()

        mainMenu = self.menuBar()

        priceMenu = mainMenu.addMenu('&價格顯示')
        priceMenu.addAction(priceInAction)
        priceMenu.addAction(priceOutAction)

        settingMenu = mainMenu.addMenu('&顯示期間')
        settingMenu.addAction(intervalAction3)
        settingMenu.addAction(intervalAction6)
        settingMenu.addAction(intervalAction12)

    def init_ui(self):
        self.setWindowTitle("Gold Price Analyzer")
        self.setWindowIcon(QtGui.QIcon('png/gold.png'))

    def update_figure_interval3(self):
        self.canvas_interval = 3
        self.gold_price_canvas.update_figure(self.price_canvas, self.canvas_interval)

    def update_figure_interval6(self):
        self.canvas_interval = 6
        self.gold_price_canvas.update_figure(self.price_canvas, self.canvas_interval)

    def update_figure_interval12(self):
        self.canvas_interval = 12
        self.gold_price_canvas.update_figure(self.price_canvas, self.canvas_interval)

    def change_canvas_price_in(self):
        self.price_canvas = 0
        self.gold_price_canvas.setStatusTip('銀行買入價格')
        self.gold_price_canvas.update_figure(self.price_canvas, self.canvas_interval)

    def change_canvas_price_out(self):
        self.price_canvas = 1
        self.gold_price_canvas.setStatusTip('銀行賣出價格')
        self.gold_price_canvas.update_figure(self.price_canvas, self.canvas_interval)


def main():
    app = QtGui.QApplication(sys.argv)
    app_window = AppWindow()
    app_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

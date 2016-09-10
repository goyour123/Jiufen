import sys
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=7, height=4, dpi=110, axix_bg_color='#FFC8FF', status_tip='Figure Canvas'):

        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#FFECFF', edgecolor='k', linewidth=1)
        self.axes = fig.add_subplot(111, axisbg=axix_bg_color)

        # We want the axes cleared every time plot() is called
        self.axes.hold(True)

        FigureCanvasQTAgg.__init__(self, fig)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)
        FigureCanvasQTAgg.setStatusTip(self, status_tip)

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


class GoldPriceInCanvas(MplCanvas):
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)
        self.date, self.price_in_list, _ = self.get_price_data()
        self.update_figure(12)

    def update_figure(self, interval):
        start_date_index = self.calculate_start_date_index(interval)
        self.axes.clear()
        self.axes.plot(self.date[start_date_index:], self.price_in_list[start_date_index:], 'r')
        self.draw()


class GoldPriceOutCanvas(MplCanvas):
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)
        self.date, _, self.price_out_list = self.get_price_data()
        self.update_figure(12)

    def update_figure(self, interval):
        start_date_index = self.calculate_start_date_index(interval)
        self.axes.clear()
        self.axes.plot(self.date[start_date_index:], self.price_out_list[start_date_index:], 'r')
        self.draw()


class AppWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.init_ui()

        self.main_widget = QtGui.QWidget(self)

        self.layout = QtGui.QVBoxLayout(self.main_widget)
        self.gpic = GoldPriceInCanvas(self.main_widget, axix_bg_color='#FFC8FF', status_tip='銀行買入價格')
        self.gpoc = GoldPriceOutCanvas(self.main_widget, axix_bg_color='#E4F5FC', status_tip='銀行賣出價格')
        self.layout.addWidget(self.gpic)
        self.layout.addWidget(self.gpoc)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

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
        settingMenu = mainMenu.addMenu('&顯示期間')
        settingMenu.addAction(intervalAction3)
        settingMenu.addAction(intervalAction6)
        settingMenu.addAction(intervalAction12)

    def init_ui(self):
        self.setWindowTitle("Gold Price Analyzer")
        #self.setToolTip('This is a <b>QWidget</b> widget')
        self.setWindowIcon(QtGui.QIcon('png/gold.png'))

    def update_figure_interval3(self):
        self.gpic.update_figure(3)
        self.gpoc.update_figure(3)

    def update_figure_interval6(self):
        self.gpic.update_figure(6)
        self.gpoc.update_figure(6)

    def update_figure_interval12(self):
        self.gpic.update_figure(12)
        self.gpoc.update_figure(12)


def main():
    app = QtGui.QApplication(sys.argv)
    app_window = AppWindow()
    app_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

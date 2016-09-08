import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=7, height=4, dpi=100, axix_bg_color='#FFC8FF', interval = 30):

        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#FFECFF', edgecolor='k', linewidth=1)
        self.axes = fig.add_subplot(111, axisbg=axix_bg_color)

        # We want the axes cleared every time plot() is called
        self.axes.hold(True)

        FigureCanvasQTAgg.__init__(self, fig)
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


class GoldPriceInCanvas(MplCanvas):
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)
        self.date, self.price_in_list, _ = self.get_price_data()
        self.axes.plot(self.date, self.price_in_list, 'r')

    def update_figure(self, date_start):
        self.axes.clear()
        self.axes.plot(self.date[-date_start:], self.price_in_list[-date_start:], 'r')
        self.draw()


class GoldPriceOutCanvas(MplCanvas):
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)
        self.date, _, self.price_out_list = self.get_price_data()
        self.axes.plot(self.date, self.price_out_list, 'r')

    def update_figure(self, date_start):
        self.axes.clear()
        self.axes.plot(self.date[-date_start:], self.price_out_list[-date_start:], 'r')
        self.draw()


class AppWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.init_ui()

        self.main_widget = QtGui.QWidget(self)

        self.layout = QtGui.QVBoxLayout(self.main_widget)
        self.gpic = GoldPriceInCanvas(self.main_widget, axix_bg_color='#FFC8FF')
        self.gpoc = GoldPriceOutCanvas(self.main_widget, axix_bg_color='#E4F5FC')
        self.layout.addWidget(self.gpic)
        self.layout.addWidget(self.gpoc)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        intervalAction180 = QtGui.QAction('&最近180天', self)
        intervalAction180.setStatusTip("更改顯示期間為最近的180天")
        intervalAction180.triggered.connect(self.update_figure_interval180)

        intervalAction360 = QtGui.QAction('&最近360天', self)
        intervalAction360.setStatusTip("更改顯示期間為最近的360天")
        intervalAction360.triggered.connect(self.update_figure_interval360)
        self.statusBar()

        mainMenu = self.menuBar()
        settingMenu = mainMenu.addMenu('&顯示期間')
        settingMenu.addAction(intervalAction180)
        settingMenu.addAction(intervalAction360)

    def init_ui(self):
        self.setWindowTitle("Gold Price Analyzer")
        self.setToolTip('This is a <b>QWidget</b> widget')
        self.setWindowIcon(QtGui.QIcon('png/gold.png'))

    def update_figure_interval180(self):
        self.gpic.update_figure(180)
        self.gpoc.update_figure(180)

    def update_figure_interval360(self):
        self.gpic.update_figure(360)
        self.gpoc.update_figure(360)


def main():
    app = QtGui.QApplication(sys.argv)
    app_window = AppWindow()
    app_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

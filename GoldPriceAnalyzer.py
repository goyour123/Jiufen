import sys
import sqlite3
from datetime import datetime
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=8, height=6, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(True)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

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
        self.x = list(converted_dates)

    def GetPriceData(self):
        return self.x, self.price_in_list, self.price_out_list


class GoldPriceInCanvas(MplCanvas):
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)
        self.update_figure()

    def update_figure(self):
        x, price_in_list, price_out_list = self.GetPriceData()
        self.axes.plot(x, price_in_list, 'r')
        self.draw()


class GoldPriceOutCanvas(MplCanvas):
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)
        self.update_figure()

    def update_figure(self):
        x, price_in_list, price_out_list = self.GetPriceData()
        self.axes.plot(x, price_out_list, 'r')
        self.draw()


class AppWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.init_ui()
        self.main_widget = QtGui.QWidget(self)

        layout = QtGui.QVBoxLayout(self.main_widget)
        gpic = GoldPriceInCanvas(self.main_widget, width=7, height=4, dpi=100)
        gpoc = GoldPriceOutCanvas(self.main_widget, width=7, height=4, dpi=100)
        layout.addWidget(gpic)
        layout.addWidget(gpoc)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def init_ui(self):
        self.setToolTip('This is a <b>QWidget</b> widget')


def main():
    app = QtGui.QApplication(sys.argv)
    app_window = AppWindow()
    app_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

import sys
# import os
import glob
import json
import numpy as np
from copy import deepcopy as dc
# from matplotlib.backends.backend_qtagg import FigureCanvasAgg
# from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets, QtCore, QtGui


# from matplotlib.figure import Figure


class ApplicationWindow(QtWidgets.QWidget):

    def __init__(self, directory):
        super().__init__()
        self.left = 20
        self.top = 50
        self.width = 1500
        self.height = 1000
        self.datalist = []
        self.newdatalist = []
        self.mousheaders = ['project_dir', 'proposal_code', 'total_time', 'mous_uid', 'n_ebs', 'n_spw', 'n_targets',
                            'pipeline_dir', 'casa_version', 'pipeline_version', 'pipeline_recipe', 'eb_list',
                            'target_list', 'ephem_science', 'spw_list', 'virtualspw_list', 'bands', 'image_list',
                            'n_images']
        self.ebheaders = ['solarsystem_calibrators', 'flux_calibrators', 'bandpass_calibrators', 'phase_calibrators',
                          'polarization_calibrators', 'check_sources', 'target_list', 'ephemeris_targets',
                          'n_ant', 'L80', 'n_scan']
        self.spwheaders = ['spw_freq', 'spw_width', 'spw_nchan', 'chan_width_freq', 'chan_width_vel', 'nbin_online']
        self.imageheaders = ['target', 'spw', 'type', 'median_rms', 'median_mad', 'median_max', 'median_snr',
                             'max_snr', 'im_maxidx']
        self.mousheadsel = []
        self.ebheadsel = []
        self.spwheadsel = []
        self.imageheadsel = []
        self.table = QtWidgets.QGroupBox('Table of data')
        self.nrows_label = QtWidgets.QLabel(self)
        self.resetbutton = QtWidgets.QPushButton('Reset table', self)
        self.message = QtWidgets.QLabel(self)
        self.tableview = QtWidgets.QTableView()
        self.columntabs = QtWidgets.QTabWidget()
        self.dataselect = QtWidgets.QGroupBox('Select data')
        self.criterion1 = QtWidgets.QLineEdit()
        self.criterion2 = QtWidgets.QComboBox()
        self.criterion3 = QtWidgets.QLineEdit()
        self.criterion4 = QtWidgets.QLabel(self)
        self.dataselectbutton = QtWidgets.QPushButton('Apply Criterion', self)
        self.mousselect = QtWidgets.QGroupBox('MOUS level columns')
        self.ebselect = QtWidgets.QGroupBox('EB level columns')
        self.spwselect = QtWidgets.QGroupBox('SPW level columns')
        self.imageselect = QtWidgets.QGroupBox('Image level columns')
        self.mousselectlist = QtWidgets.QListWidget()
        self.mousselectbutton = QtWidgets.QPushButton('Apply Selection', self)
        self.spwselectlist = QtWidgets.QListWidget()
        self.spwselectbutton = QtWidgets.QPushButton('Apply Selection', self)
        self.imageselectlist = QtWidgets.QListWidget()
        self.imageselectbutton = QtWidgets.QPushButton('Apply Selection', self)
        self.ebselectlist = QtWidgets.QListWidget()
        self.ebselectbutton = QtWidgets.QPushButton('Apply Selection', self)
        self.directory = directory
        self.loadjsonfiles()
        self.init_ui()
        self.reset_data()

    def loadjsonfiles(self):
        files = glob.glob(self.directory + '/*.json')
        for file in files:
            strct = json.load(open(file, 'r'))
            strct['n_images'] = len(strct['image_list'])
            for image in strct['image_list']:
                strct[image]['median_rms'] = float(np.median(strct[image]['rms']))
                strct[image]['median_mad'] = float(np.median(strct[image]['mad'])) * 1.4826
                strct[image]['median_max'] = float(np.median(strct[image]['max']))
                snr = np.array(strct[image]['max']) / np.array(strct[image]['rms'])
                strct[image]['median_snr'] = float(np.median(snr))
                strct[image]['max_snr'] = float(np.max(snr))
            self.datalist.append(strct)
        self.newdatalist = dc(self.datalist)

    def init_ui(self):
        self.setWindowTitle(self.directory)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.get_table_layout()
        self.get_columnselect_layout()
        self.get_dataselect_layout()
        main_layout = QtWidgets.QGridLayout()
        main_layout.addWidget(self.table, 0, 0, 2, 2)
        main_layout.addWidget(self.columntabs, 0, 2, 1, 1)
        main_layout.addWidget(self.dataselect, 1, 2, 1, 1)
        main_layout.setColumnStretch(0, 10)
        main_layout.setRowStretch(0, 8)
        self.setLayout(main_layout)

    def get_dataselect_layout(self):
        self.criterion1.setPlaceholderText("Enter parameter name")
        self.criterion2.addItems(['==', '!=', '>=', '<=', 'contains'])
        self.criterion3.setPlaceholderText("Enter value")
        self.dataselectbutton.clicked.connect(self.apply_criterion)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.criterion1)
        layout.addWidget(self.criterion2)
        layout.addWidget(self.criterion3)
        layout.addWidget(self.criterion4)
        layout.addWidget(self.dataselectbutton)
        self.dataselect.setLayout(layout)

    def get_columnselect_layout(self):
        self.columntabs.addTab(self.mousselect, "MOUS Level")
        self.columntabs.addTab(self.ebselect, "EB Level")
        self.columntabs.addTab(self.spwselect, "SPW Level")
        self.columntabs.addTab(self.imageselect, "IMAGE Level")
        zipped = zip([self.mousselect, self.ebselect, self.spwselect, self.imageselect],
                     [self.mousselectlist, self.ebselectlist, self.spwselectlist, self.imageselectlist],
                     [self.mousselectbutton, self.ebselectbutton, self.spwselectbutton, self.imageselectbutton],
                     [self.mousheaders, self.ebheaders, self.spwheaders, self.imageheaders])
        for select, selectlist, selectbutton, headers in zipped:
            selectlist.addItems(headers)
            selectlist.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            selectbutton.clicked.connect(self.update_table)
            layout = QtWidgets.QGridLayout()
            layout.addWidget(selectlist, 0, 0, 8, 1)
            layout.addWidget(selectbutton, 8, 0, 1, 1)
            select.setLayout(layout)

    def get_table_layout(self):
        self.resetbutton.clicked.connect(self.reset_data)
        self.message.setText('Table is showing show per MOUS entries')
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.tableview, 0, 0, 3, 3)
        layout.addWidget(self.nrows_label, 3, 0, 1, 1)
        layout.addWidget(self.resetbutton, 3, 1, 1, 1)
        layout.addWidget(self.message, 3, 2, 1, 1)
        self.table.setLayout(layout)

    def update_table(self):
        if ((len(self.ebselectlist.selectedItems()) > 0 and len(self.spwselectlist.selectedItems()) > 0) or
                (len(self.ebselectlist.selectedItems()) > 0 and len(self.imageselectlist.selectedItems()) > 0) or
                (len(self.spwselectlist.selectedItems()) > 0 and len(self.imageselectlist.selectedItems()) > 0)):
            self.message.setText('Cannot select columns from EB, SPW and IMAGE level at the same time')
            return
        self.mousheadsel = [x.text() for x in self.mousselectlist.selectedItems()]
        if len(self.ebselectlist.selectedItems()) > 0:
            self.message.setText('Table is showing per EB entries')
            self.ebheadsel = [x.text() for x in self.ebselectlist.selectedItems()]
            self.update_perxtable('n_ebs', self.ebheadsel, 'eb_list')
        elif len(self.spwselectlist.selectedItems()) > 0:
            self.message.setText('Table is showing per SPW entries')
            self.spwheadsel = [x.text() for x in self.spwselectlist.selectedItems()]
            self.update_perxtable('n_spw', self.spwheadsel, 'spw_list')
        elif len(self.imageselectlist.selectedItems()) > 0:
            self.message.setText('Table is showing per IMAGE entries')
            self.imageheadsel = [x.text() for x in self.imageselectlist.selectedItems()]
            self.update_perxtable('n_images', self.imageheadsel, 'image_list')
        else:
            self.message.setText('Table is showing per MOUS entries')
            self.update_moustable()

    def update_moustable(self):
        self.nrows_label.setText('Number of rows: {}'.format(len(self.newdatalist)))
        if len(self.newdatalist) == 0:
            model = QtGui.QStandardItemModel()
        else:
            model = QtGui.QStandardItemModel(len(self.newdatalist), len(self.mousheadsel))
            model.setHorizontalHeaderLabels([x + ' (' + str(type(self.newdatalist[0][x]))[8:-2] + ')'
                                             for x in self.mousheadsel])
            for idx1, x in enumerate(self.newdatalist):
                for idx2, y in enumerate(self.mousheadsel):
                    newitem = QtGui.QStandardItem()
                    newitem.setData(str(x[y]), QtCore.Qt.DisplayRole)
                    model.setItem(idx1, idx2, newitem)
        self.update_tableview(model)

    def update_perxtable(self, n_x, n_xheadsel, x_list):
        rowlength = np.sum([x[n_x] for x in self.newdatalist])
        columnlength = len(n_xheadsel) + len(self.mousheadsel)
        if n_x == 'n_spw':
            firstx = self.newdatalist[0]['spw' + str(self.newdatalist[0][x_list][0])]
        else:
            firstx = self.newdatalist[0][self.newdatalist[0][x_list][0]]
        headers = ([x + ' (' + str(type(self.newdatalist[0][x]))[8:-2] + ')' for x in self.mousheadsel] +
                   [x + ' (' + str(type(firstx[x]))[8:-2] + ')' for x in n_xheadsel])
        # headers = self.mousheadsel + n_xheadsel
        model = QtGui.QStandardItemModel(rowlength, columnlength)
        model.setHorizontalHeaderLabels(headers)
        self.nrows_label.setText('Number of rows: {}'.format(rowlength))
        rownumber = 0
        for idx1, x in enumerate(self.newdatalist):
            for idx2, y in enumerate(x[x_list]):
                if n_x == 'n_spw':
                    y = 'spw{}'.format(y)
                for idx3, z1 in enumerate(self.mousheadsel):
                    newitem = QtGui.QStandardItem()
                    newitem.setData(str(x[z1]), QtCore.Qt.DisplayRole)
                    model.setItem(rownumber, idx3, newitem)
                for idx4, z2 in enumerate(n_xheadsel):
                    newitem = QtGui.QStandardItem()
                    newitem.setData(str(x[y][z2]), QtCore.Qt.DisplayRole)
                    model.setItem(rownumber, len(self.mousheadsel) + idx4, newitem)
                rownumber += 1
        self.update_tableview(model)

    def update_tableview(self, model):
        proxy = QtCore.QSortFilterProxyModel()
        proxy.setSourceModel(model)
        self.tableview.setModel(proxy)
        self.tableview.resizeColumnsToContents()
        self.tableview.horizontalHeader().setStretchLastSection(True)
        self.tableview.setSortingEnabled(True)

    def apply_criterion(self):
        if self.criterion1.text() in self.mousheaders:
            self.criterion4.setText('found header in MOUS')
            self.apply_mouscriterion()
        elif self.criterion1.text() in self.ebheaders:
            self.criterion4.setText('found header in EB')
            self.apply_xciterion('n_ebs', 'eb_list')
        elif self.criterion1.text() in self.spwheaders:
            self.criterion4.setText('found header in SPW')
            self.apply_xciterion('n_spw', 'spw_list')
        elif self.criterion1.text() in self.imageheaders:
            self.criterion4.setText('found header in IMAGE')
            self.apply_xciterion('n_images', 'image_list')
        else:
            self.criterion4.setText('{} Not a valid parameter name'.format(self.criterion1.text()))
            self.criterion1.setText('')

    def apply_mouscriterion(self):
        try:
            crit = type(self.newdatalist[0][self.criterion1.text()])(self.criterion3.text())
        except ValueError:
            self.criterion4.setText('Inconsistent type for {}'.format(self.criterion1))
            return
        criterion = {'==': [x for x in self.newdatalist if x[self.criterion1.text()] == crit],
                     '!=': [x for x in self.newdatalist if x[self.criterion1.text()] != crit],
                     '>=': [x for x in self.newdatalist if x[self.criterion1.text()] >= crit],
                     '<=': [x for x in self.newdatalist if x[self.criterion1.text()] <= crit],
                     'contains': [x for x in self.newdatalist if str(crit) in str(x[self.criterion1.text()])]}
        self.newdatalist = criterion[self.criterion2.currentText()]
        self.update_table()

    def apply_xciterion(self, n_x, x_list):
        try:
            row = self.newdatalist[0]
            if n_x == 'n_spw':
                crit = type(row['spw{}'.format(row[x_list][0])][self.criterion1.text()])(self.criterion3.text())
            else:
                crit = type(row[row[x_list][0]][self.criterion1.text()])(self.criterion3.text())
        except ValueError:
            self.criterion4.setText('Inconsistent type for {}'.format(self.criterion1))
            return
        projects = [x for x in self.newdatalist]
        for x in projects:
            ebs = [eb for eb in x[x_list]]
            for y in ebs:
                if n_x == 'n_spw':
                    ly = 'spw{}'.format(y)
                else:
                    ly = y
                criterion = {'==': x[ly][self.criterion1.text()] == crit, '!=': x[ly][self.criterion1.text()] != crit,
                             '>=': x[ly][self.criterion1.text()] >= crit, '<=': x[ly][self.criterion1.text()] <= crit,
                             'contains': str(crit) in str(x[ly][self.criterion1.text()])}
                if not criterion[self.criterion2.currentText()]:
                    del x[ly]
                    x[x_list].remove(y)
                    x[n_x] -= 1
            if not x[x_list]:
                self.newdatalist.remove(x)
        self.update_table()

    def reset_data(self):
        self.newdatalist = dc(self.datalist)
        self.mousheadsel = []
        self.ebheadsel = []
        self.spwheadsel = []
        self.imageheadsel = []
        self.mousselectlist.selectAll()
        self.ebselectlist.reset()
        self.spwselectlist.reset()
        self.imageselectlist.reset()
        self.update_table()


def main():
    if len(sys.argv) == 1:
        print('cfgui: taking current directory as input')
        qapp = QtWidgets.QApplication(['1'])
        # appw = ApplicationWindow(os.getcwd())
        appw = ApplicationWindow('/Users/mneelema/PLWG/TestData/CF/Benchmark2023Json')  # for testing puproses
    else:
        qapp = QtWidgets.QApplication(['1'])
        appw = ApplicationWindow(sys.argv[1])
    appw.show()
    # appw.activateWindow()
    # appw.raise_()
    sys.exit(qapp.exec())


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# coding: utf-8
#
# EasyGUIng - A GUI building tool for your mathematic model
# Copyright (C) 2022  s-quirin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__Name__ = 'EasyGUIng'
__Comment__ = 'A GUI building tool for your mathematic model'
__Author__ = 's-quirin'
__Version__ = '0.0.1'
__Date__ = '2022-09-12'
__License__ = 'LGPL-3.0-or-later'
__Source__ = 'https://github.com/s-quirin/EasyGUIng'

# Preferences
NUM_OF_DATAPOINTS = 101    # default number of data points to plot
MIN_EDIT_WIDTH = 100    # minimum width for line edit
SPACING = 12    # spacing between description box and calc/plot box

# Load external mathematic model as module in subfolder
MODEL_FOLDER = 'model'

"""Init"""
# Get all model file paths (.py files in MODEL_FOLDER)
import os
import sys
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # running in an executable bundle
    DIRECTORY = os.path.dirname(sys.executable)    # directory of executable
    # bugfixes and improvements for executables:
    import matplotlib.backends.backend_pdf    # make the 'Save the figure -> pdf' work
else:
    # running in a normal Python process
    DIRECTORY = os.path.dirname(os.path.abspath(__file__))    # script directory
g_modeldir = os.path.join(DIRECTORY, MODEL_FOLDER)
g_modelpaths = []
for (root,dirs,files) in os.walk(g_modeldir):
    for f_ in files:
        if os.path.splitext(f_)[1] == '.py':
            g_modelpaths.append(os.path.join(root,f_))

# Dynamic module import
from importlib.machinery import SourceFileLoader

# GUI
from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from PySide6 import QtSvgWidgets as qts
from PySide6 import QtWidgets as qtw    # only PySide6-Essentials are used
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
# https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html

# Physical quantities
import pint
ureg = pint.UnitRegistry()
ureg.setup_matplotlib()    # https://pint.readthedocs.io/en/stable/plotting.html
ureg.default_format = '~P'    # f'{u:~P}' pint short pretty
Q_ = ureg.Quantity

# globals
g_num_of_datapoints = NUM_OF_DATAPOINTS
g_library_infos = ['Qt ' + qtc.QLibraryInfo.version().toString(),
    'Matplotlib ' + mpl.__version__,
    'Pint ' + pint.__version__]

class MainWindow(qtw.QMainWindow):
    """GUI Window"""
    def __init__(self):
        super().__init__()
        # self.setLocale(qtc.QLocale.German)    # decimal seperators are English!
        self.setWindowTitle(__Name__ + ' ' + __Version__)
        self.setCentralWidget(MainWidget(self))

class MainWidget(qtw.QTabWidget):
    """GUI with module pages as tabs"""
    def __init__(self, parent):
        super().__init__(parent)

        # About button next to TabBar
        btn = qtw.QPushButton('?', toolTip='Über')
        btn.clicked.connect(self.on_pushButton_about)
        self.setCornerWidget(btn)

        # Import each model as a module and show as tab
        for p_ in g_modelpaths:
            name = os.path.splitext(os.path.basename(p_))[0]    # filename
            model = SourceFileLoader(name, p_).load_module()
            self.addTab(PageWidget(model, name), name)
        if not g_modelpaths:
            msg = 'No models were found. Check \n' + g_modeldir + '\ndirectory for .py files.'
            print(msg)
            qtw.QMessageBox.critical(parent, 'Error', msg)
        
    def on_pushButton_about(self):
        """Open window with program information"""
        table = (
            ('<h2>'+__Name__+'</h2>', 'v' + __Version__ + ', ' + __Date__),
            tuple(),
            (__Comment__, ),
            tuple(),
            ('Autor(en):', '<i>' + __Author__ + '</i>'),
            ('Lizenz:', __License__),
            ('Quelltext:', __Source__),
            ('Bibliotheken:', '<br>'.join(g_library_infos))
            )
        # table in html representation
        text = ''
        for row in table:
            style, colspan = '', ''
            if not text:
                style = ' style="vertical-align:bottom"'    # first row
            text += '<tr>'
            for col in row:
                if len(row) == 1:
                    colspan = ' colspan="2"'
                text += '<td' + style + colspan + '>' + col + '</td>'
            text += '</tr>'
        qtw.QMessageBox.about(self, 'Über', '<table>' + text + '</table>')

class PageWidget(qtw.QWidget):
    """A tab in the MainWidget containing all about the model"""
    def __init__(self, model, name):
        super().__init__()
        
        # Get vars from model
        self.model = model
        self.c, self.inputNames, qtys = {}, {}, {}
        for k_, v_ in model.c.items():
            self.c[k_] = Q_(v_[0], v_[-1])
        for k_, v_ in model.input.items():
            # input['x'] = ('name', (min value, ..., max value), 'unit')
            self.inputNames[k_] = str(v_[0])
            if type(v_[1]) is not tuple:
                qtys[k_] = [Q_(v_[1], v_[-1])]    # a single entry is not a tuple
            else:
                qtys[k_] = [Q_(val, v_[-1]) for val in v_[1]]
        self.outputNames = model.output
        if type(self.outputNames) is not tuple:
            self.outputNames = (self.outputNames,)    # tuple with one item
        self.output = str(self.outputNames[0])
        self.plotX = str(model.plotX)

        # Description
        descBoxLayout = qtw.QVBoxLayout()
        
        headLayout = qtw.QHBoxLayout()
        label = qtw.QLabel('<h2>' + str(model.title) + '</h2>')
        headLayout.addWidget(label)    # title
        text = 'v' + str(model.version) + ' <i>' + str(model.author) + '</i>'
        label = qtw.QLabel(text)
        label.setAlignment(qtc.Qt.AlignRight | qtc.Qt.AlignVCenter)
        headLayout.addWidget(label)    # version, author

        descLayout = qtw.QHBoxLayout()
        label = qtw.QTextBrowser()
        label.setMarkdown(str(model.description))
        label.setStyleSheet('QTextBrowser {border: 1px solid lightgrey}')
        descLayout.addWidget(label)    # description
        file = os.path.join(g_modeldir, name)
        if os.path.exists(file + '.svg'):
            image = qts.QSvgWidget(file + '.svg')
            image.renderer().setAspectRatioMode(qtc.Qt.KeepAspectRatio)
            descLayout.addWidget(image)
        else:
            pixmap = qtg.QPixmap(file)    # loader guesses the image file format
            if not pixmap.isNull():
                image = qtw.QLabel()
                image.setPixmap(pixmap)
                descLayout.addWidget(image)

        descBoxLayout.addLayout(headLayout)
        descBoxLayout.addLayout(descLayout)

        # Input/Output
        calcBox = qtw.QGroupBox('Rechner')
        calcBoxLayout = qtw.QFormLayout(calcBox)
        self.calcInputs = {}
        for k_, v_ in qtys.items():
            mean = (v_[0] + v_[-1]) / 2    # also works with single entry
            ed = qtw.QLineEdit(f'{mean}', toolTip=k_)
            ed.setMinimumWidth(MIN_EDIT_WIDTH)
            ed.editingFinished.connect(self.on_calcEdit_finished)
            self.calcInputs[k_] = ed
            calcBoxLayout.addRow(self.inputNames[k_], ed)    # label: 'name'
        
        line = qtw.QFrame(frameShape=qtw.QFrame.HLine)
        line.setStyleSheet('QFrame {color: lightgrey}')
        calcBoxLayout.addRow(line)

        outputLineLabel = qtw.QLabel('=')
        if len(self.outputNames) == 1:
            outputCombo = qtw.QLabel(self.output, toolTip='Ausgabewert')
        else:
            outputCombo = qtw.QComboBox(toolTip='Ausgabewert')
            outputCombo.addItems(self.outputNames)
            outputCombo.setCurrentText(self.output)
            outputCombo.currentIndexChanged.connect(self.on_outputCombo_changed)
        self.outputLine = qtw.QLineEdit(readOnly=True)
        self.outputLine.setMinimumWidth(MIN_EDIT_WIDTH)
        self.plotCalc = qtw.QCheckBox(tristate=True)
        self.plotCalc.setToolTip('Markiere und beschrifte den berechneten Wert')
        self.plotCalc.stateChanged.connect(self.on_plotCalc_stateChanged)
        
        calcLayout = qtw.QHBoxLayout()
        calcLayout.addWidget(outputLineLabel)
        calcLayout.addWidget(outputCombo)
        calcLayout.addWidget(self.outputLine)
        calcLayout.addWidget(self.plotCalc)
        calcBoxLayout.addRow(calcLayout)

        plotBox = qtw.QGroupBox('Diagramm')
        plotBoxLayout = qtw.QFormLayout(plotBox)
        self.plotInputs = {}
        for k_ in qtys:
            text = '; '.join([f'{q_}' for q_ in qtys[k_]])
            ed = qtw.QLineEdit(text, toolTip=k_)
            ed.setPlaceholderText(text)
            ed.setClearButtonEnabled(True)
            ed.setMinimumWidth(MIN_EDIT_WIDTH)
            ed.editingFinished.connect(self.on_plotEdit_finished)
            ed.returnPressed.connect(self.on_plotEdit_returnPressed)
            self.plotInputs[k_] = ed
            plotBoxLayout.addRow(self.inputNames[k_], ed)    # label: 'name'
        
        line = qtw.QFrame(frameShape=qtw.QFrame.HLine)
        line.setStyleSheet('QFrame {color: lightgrey}')  
        plotBoxLayout.addRow(line)

        self.plotXCombo = qtw.QComboBox(toolTip='Laufvariable')
        self.plotXCombo.addItems(self.inputNames.values())
        self.plotXCombo.setCurrentText(self.inputNames[self.plotX])
        self.plotXCombo.currentIndexChanged.connect(self.on_plotXCombo_changed)
        plotNumOfPts = qtw.QSpinBox(toolTip='Datenpunkte', minimum=2, maximum=1001)
        plotNumOfPts.setValue(g_num_of_datapoints)
        plotNumOfPts.setKeyboardTracking(False)    # do not emit signals while typing
        plotNumOfPts.valueChanged.connect(self.on_pointNum_valueChanged)
        plotNumOfPtsLabel = qtw.QLabel('Punkte')
        self.plotMin = qtw.QCheckBox('Min.', tristate=True)
        self.plotMin.setToolTip('Markiere und beschrifte das erste Minimum')
        self.plotMax = qtw.QCheckBox('Max.', tristate=True)
        self.plotMax.setToolTip('Markiere und beschrifte das erste Maximum')
        icon = self.style().standardIcon(qtw.QStyle.SP_BrowserReload)
        plotBtn = qtw.QPushButton(icon, '', toolTip='Zeichne')
        plotBtn.setDefault(True)
        plotBtn.clicked.connect(self.on_plotBtn_clicked)
        
        plotLayout = qtw.QHBoxLayout()
        plotLayout.addWidget(self.plotXCombo)
        plotLayout.addWidget(plotNumOfPts)
        plotLayout.addWidget(plotNumOfPtsLabel)
        plotLayout.addWidget(self.plotMin)
        plotLayout.addWidget(self.plotMax)
        plotLayout.addWidget(plotBtn)
        plotBoxLayout.addRow(plotLayout)

        self.calc()
        self.outputPlot = ModelPlot(self)
        self.outputPlot.setMinimumHeight(250)

        # sublayout
        sublayout = qtw.QHBoxLayout()
        sublayout.addWidget(calcBox)
        sublayout.addWidget(plotBox)

        # main layout
        layout = qtw.QVBoxLayout(self)
        layout.addLayout(descBoxLayout)
        layout.addSpacing(SPACING)
        layout.addLayout(sublayout)
        layout.addWidget(self.outputPlot)

    def calc(self):
        qty = {}
        for k_ in self.calcInputs:
            qty[k_] = Q_(self.calcInputs[k_].text())
        y = self.calc_series(None, qty)
        self.calcPoint = (qty , y)    # with all possible x values
        self.outputLine.setText(f'{y:.9g~P}')

    def on_calcEdit_finished(self):
        self.calc()
        self.on_plotCalc_stateChanged(self.plotCalc.checkState())

    def on_outputCombo_changed(self, index):
        self.output = self.outputNames[index]
        self.calc()
        self.on_plotBtn_clicked()

    def on_plotCalc_stateChanged(self, state):
        self.outputPlot.markCalculation(state)    # does not replot lines
        self.outputPlot.ax.figure.canvas.draw()

    def on_plotEdit_finished(self):
        ed = self.sender()
        if not ed.text():
            ed.setText(ed.placeholderText())    # fill with default values
    
    def on_plotEdit_returnPressed(self):
        self.on_plotBtn_clicked()

    def on_plotXCombo_changed(self, index):
        self.plotX = list(self.inputNames.keys())[index]

    def on_pointNum_valueChanged(self, i):
        global g_num_of_datapoints
        g_num_of_datapoints = i

    def on_plotBtn_clicked(self):
        self.outputPlot.plot()
    
    def calc_series(self, x, qty):
        """Pass a normalized data series (control variable x, parameters) to the model"""
        qty = qty.copy()    # changes are only for normalized calculation
        for k_ in qty:
            qty[k_] = qty[k_].to_base_units()
        parameter = (self.c, qty, self.output)
        
        if x is None:
            return self.model.calculate(*parameter)
        else:
            y = []
            for x_ in x.to_base_units():
                qty[self.plotX] = x_
                y.append(self.model.calculate(*parameter))
            return Q_.from_list(y)

class ModelPlot(qtw.QWidget):
    """The plot part of the model's GUI"""
    def __init__(self, parent):
        super().__init__(parent)

        layout = qtw.QVBoxLayout(self)
        px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        # figsize: Figure dimension (width, height) in inches
        canvas = FigureCanvas(plt.figure(figsize=(600*px, 400*px)))
        
        # https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        layout.addWidget(NavigationToolbar(canvas, self))
        layout.addWidget(canvas)

        self.overlay = []    # annotations to remove
        self.ax = canvas.figure.subplots()
        self.plot()

        # For the cursor to remain responsive you must keep a reference to it.
        # Set useblit=True on most backends for enhanced performance.
        self.cursor = mpl.widgets.Cursor(self.ax, useblit=True, color='grey', linewidth=0.5)

    def plot(self):
        self.ax.clear()    # clear old plots
        parent = self.parent()
        
        self.legendKeys = []
        family, qty = {}, {}
        for k_ in parent.plotInputs:
            texts = parent.plotInputs[k_].text().split(';')    # split always returns a list
            texts = [s_.strip() for s_ in texts]    # remove leading and trailing spaces
            if k_ == parent.plotX:
                x = Q_.from_list(linspace(Q_(texts[0]), Q_(texts[-1])))
            elif len(set(texts)) == 1:
                qty[k_] = Q_(texts[0])    # k_ not containing different values
            else:
                family[k_] = texts
                self.legendKeys.append(k_)

        numOfPlots = 1
        if family:
            numOfPlots = min([len(v_) for v_ in family.values()])    # shortest family
        for n_ in range(numOfPlots):
            for f_ in family:
                qty[f_] = Q_(family[f_][n_])
            self.ax.plot(x, parent.calc_series(x, qty), '.-',
                            label=self.legendText(qty), fillstyle='none')
        if family:
            self.ax.legend()
        
        self.markExtremum((parent.plotMin.checkState(), parent.plotMax.checkState()))
        self.markCalculation(parent.plotCalc.checkState())
        # fits plot within figure cleanly and allows to modify borders afterwards
        self.ax.figure.tight_layout()
        self.ax.figure.canvas.draw()

    def legendText(self, dictionary):
        texts = [f'{v_}' for k_, v_ in dictionary.items() if k_ in self.legendKeys]
        return ', '.join(texts)
    
    def markExtremum(self, markMinMax):
        if not any(markMinMax):
            return
        align = ('top', 'bottom')    # verticalalignment of min and max label
        for line in self.ax.lines:
            y = list(line.get_ydata().magnitude)    # numpy array of quantities to list
            extremum = (min(y), max(y))
            yindex = []    # line.set_markevery(yindex)
            for n_ in range(2):
                if not markMinMax[n_]:
                    continue
                yindex.append(y.index(extremum[n_]))
                # Note: index() only returns the first occurrence
                point = line.get_xydata()[yindex[-1]]
                line.set_markevery(yindex)
                if markMinMax[n_] == qtc.Qt.Checked:
                    self.labelPoint(point, align[n_])

    def markCalculation(self, mark):
        if self.ax.lines[-1].get_gid() == 'calc':
            self.ax.lines[-1].remove()    # remove old markers
            self.ax.legend()    # update legend
        if self.overlay:
            self.overlay.remove()    # remove old annotation
            self.overlay = []
        if not mark:
            return
        parent = self.parent()
        xs, y = parent.calcPoint    # with all possible x values
        x = xs[parent.plotX]
        self.ax.plot(x, y, 'x', color='red',
            label=self.legendText(xs), gid='calc')    # gid: custom id
        self.ax.legend()    # update legend
        if mark == qtc.Qt.Checked:
            self.overlay = self.labelPoint((x.magnitude, y.magnitude), 'center')
    
    def labelPoint(self, point, align):
        """Annotate point's location"""
        point_str = [f'{p_:g}' for p_ in point]
        text = '(' + point_str[0] + ', ' + point_str[1] + ')'
        return self.ax.annotate(text, xy=point,  xycoords='data',
                    xytext=point, textcoords='data',
                    horizontalalignment='center', verticalalignment=align,
                    )

def linspace(start, stop):
    """Pure python linspace implementation with num > 1, endpoint=True"""
    step = (stop - start) / (g_num_of_datapoints - 1)
    return [start + step * n_ for n_ in range(g_num_of_datapoints)]

app = qtw.QApplication()
window = MainWindow()
window.show()
app.exec()
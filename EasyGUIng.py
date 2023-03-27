#!/usr/bin/env python
# coding: utf-8
#
# EasyGUIng - A GUI building tool for your mathematic model
# Copyright (C) 2022-2023  s-quirin
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
__Version__ = '0.0.2'
__Date__ = '2023-03-24'
__License__ = 'LGPL-3.0-or-later'
__Source__ = 'https://github.com/s-quirin/EasyGUIng'

# Preferences
NUM_OF_DATAPOINTS = 101    # default number of data points to plot
MIN_EDIT_WIDTH = 100    # minimum width for line edit
MAX_IMAGE_HEIGHT = 256    # maximum height for images in px
SPACING = 12    # spacing between description box and calc/plot box

# Load external mathematic model as module in subfolder
MODEL_FOLDER = 'model'

"""Init"""
# Get all model file paths (.py files in MODEL_FOLDER)
import sys
from pathlib import Path
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # running in an executable bundle
    DIRECTORY = Path(sys.executable).parent    # directory of executable
    # BUG: bugfixes and improvements for executables:
    import matplotlib.backends.backend_pdf    # make the 'Save the figure -> pdf' work
else:
    # running in a normal Python process
    DIRECTORY = Path(__file__).parent    # script directory
g_modeldir = Path(DIRECTORY, MODEL_FOLDER)
g_modelpath_gen = g_modeldir.glob('*.py')   # is generator (from .glob) -> use only once

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
import numpy as np

# Physical quantities
import pint
ureg = pint.UnitRegistry()
ureg.setup_matplotlib()    # https://pint.readthedocs.io/en/stable/plotting.html
ureg.default_format = '~P'    # f'{u:~P}' pint short pretty
Q_ = ureg.Quantity

# globals
g_library_infos = ['Qt ' + qtc.QLibraryInfo.version().toString(),
    'Matplotlib ' + mpl.__version__,
    'Pint ' + pint.__version__]

class MainWindow(qtw.QMainWindow):
    """GUI Window"""
    def __init__(self):
        super().__init__()
        # self.setLocale(qtc.QLocale.German)    # decimal seperators are English!
        self.setWindowTitle(__Name__ + ' ' + __Version__)
        self.setCentralWidget(MainWidget())

class MainWidget(qtw.QTabWidget):
    """GUI with module pages as tabs"""
    def __init__(self):
        super().__init__()

        # Save and About button next to TabBar
        icon = self.style().standardIcon(qtw.QStyle.SP_DialogSaveButton)
        saveBtn = qtw.QPushButton(icon, '', toolTip='Daten exportieren')
        saveBtn.clicked.connect(self.on_saveBtn_clicked)
        saveBtn.setEnabled(False)
        aboutBtn = qtw.QPushButton('?', toolTip='Über')
        aboutBtn.setFixedSize(saveBtn.sizeHint())
        aboutBtn.clicked.connect(self.on_aboutBtn_clicked)
        
        box = qtw.QWidget()
        boxLayout = qtw.QHBoxLayout(box)
        boxLayout.addWidget(saveBtn)
        boxLayout.addWidget(aboutBtn)
        boxLayout.setContentsMargins(0, 0, 0, 0)
        self.setCornerWidget(box)

        # Import each model as a module and show as tab
        for p_ in g_modelpath_gen:
            name = p_.stem    # filename without extension
            if name[:2] == 'f_':
                # skip helper functions
                continue
            model = SourceFileLoader(name, str(p_)).load_module()
            self.addTab(PageWidget(model, name), name)
        if self.count() == 0:
            error(self, 'No models were found.')
            msg = f' No models found in\n {g_modeldir} \n Check directory for .py files.'
            self.addTab(qtw.QLabel(msg), 'Error')
            return
        self.existingPlots = [False] * self.count()
        self.on_tab_changed(self.currentIndex())    # fill the first tab
        self.currentChanged.connect(self.on_tab_changed)
        saveBtn.setEnabled(True)
        self.show()    # BUG: sometimes doesn't work on startup without this

    def on_tab_changed(self, index):
        if not self.existingPlots[index]:
            self.widget(index).calc()    # do point calculation on current tab
            self.widget(index).outputPlot.plot()    # do the plot on current tab
            self.existingPlots[index] = True

    def on_saveBtn_clicked(self):
        """Export calculated data to .csv file"""
        fileFilter = ('CSV (Tab-separated) (*.csv)','Text (Tab-separated) (*.txt)',
            'CSV (Comma-separated) (*.csv)')
        path, selectedFilter = qtw.QFileDialog.getSaveFileName(self,
            'Daten exportieren', str(DIRECTORY), ';;'.join(fileFilter))
        if not path:
            return
        delimiter = '\t' if selectedFilter in fileFilter[:2] else ','    # Tab- or Comma-separated
        # get data
        widget = self.currentWidget()
        plots = widget.outputPlot.plots
        input = np.array([widget.inputNames[k_] for k_ in plots[0].qty])
        data = plots[0].x.magnitude
        unit = [str(plots[0].x.units)]
        for p_ in plots:
            input = np.vstack((input, np.array([str(v_) for v_ in p_.qty.values()])))
            data = np.vstack((data, p_.result.magnitude))
            unit.append(str(p_.result.units))
        input = input.transpose()
        header = '\n'.join([delimiter.join(i_) for i_ in input.tolist()])
        header += '\n' + delimiter.join(unit)
        # save in double precision
        np.savetxt(path, data.transpose(), fmt='%.14e',
                   header=header, delimiter=delimiter, encoding='utf-8')

    def on_aboutBtn_clicked(self):
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
        qtw.QMessageBox.about(self, 'Über', htmlTable(table))

class PageWidget(qtw.QWidget):
    """A tab in the MainWidget containing all about the model"""
    class ValidModel():
        def __init__(self, model, name):
            self.name = name
            
            # Optional
            self.title = str(getattr(model, 'title', name))
            self.description = str(getattr(model, 'description', ''))
            self.author = str(getattr(model, 'author', ''))
            self.version = str(getattr(model, 'version', ''))
            self.option = getattr(model, 'option', {})
            self.option['output'] = self.option.get('output', '')    # key required

            # Required
            self.input = getattr(model, 'input')
            self.plotX = str(getattr(model, 'plotX'))
            self.calculate = getattr(model, 'calculate')
            for k_, v_ in self.option.items():
                if not v_ or type(v_) is not tuple:
                    self.option[k_] = (str(v_),)    # tuple with one item
                else:
                    self.option[k_] = tuple([str(i_) for i_ in v_])         

    def __init__(self,  model, name):
        super().__init__()
        model = self.ValidModel(model, name)    # check model integrity
        self.model = model
        
        # Get vars from model
        self.inputNames, qtys, self.inputForOption, self.option = {}, {}, {}, {}
        for k_, v_ in model.input.items():
            # input['x'] = ('name', (min value, ..., max value), 'unit', output)
            self.inputNames[k_] = str(v_[0])
            if type(v_[1]) is not tuple:
                qtys[k_] = [Q_(v_[1], v_[2])]    # a single entry is not a tuple
            else:
                qtys[k_] = [Q_(val, v_[2]) for val in v_[1]]
            if len(v_) > 3:
                if type(v_[3]) is tuple:
                    self.inputForOption[k_] = v_[3]
                else:
                    self.inputForOption[k_] = (v_[3],)    # tuple with one item
        for k_ in model.option:
            self.option[k_] = model.option[k_][0]
        self.plotX = model.plotX
        self.calcModel = model.calculate

        # Description
        descBoxLayout = qtw.QVBoxLayout()
        
        headLayout = qtw.QHBoxLayout()
        label = qtw.QLabel('<h2>' + model.title + '</h2>')
        headLayout.addWidget(label)    # title
        label = qtw.QLabel('v' + model.version + ' <i>' + model.author + '</i>')
        label.setAlignment(qtc.Qt.AlignRight | qtc.Qt.AlignVCenter)
        headLayout.addWidget(label)    # version, author

        descLayout = qtw.QHBoxLayout()
        label = qtw.QTextBrowser()
        label.setMarkdown(model.description)
        label.setStyleSheet('QTextBrowser {border: 1px solid lightgrey}')
        descLayout.addWidget(label)    # description
        self.image = None
        self.getImage()    # try to load an image
        if self.image:
            descLayout.addWidget(self.image)

        descBoxLayout.addLayout(headLayout)
        descBoxLayout.addLayout(descLayout)

        # Input/Output
        for k_, v_ in model.option.items():
            if k_ != 'output' and len(v_) > 1:
                box = qtw.QComboBox(toolTip=k_)
                box.addItems(v_)
                box.currentTextChanged.connect(self.on_optionCombos_changed)
                descBoxLayout.addWidget(box)

        calcBox = qtw.QGroupBox('Rechner')
        self.calcBoxLayout = qtw.QFormLayout(calcBox)
        self.calcInputs = {}
        for k_, v_ in qtys.items():
            mean = (v_[0] + v_[-1]) / 2    # also works with single entry
            ed = qtw.QLineEdit(f'{mean}', toolTip=k_)
            ed.setMinimumWidth(MIN_EDIT_WIDTH)
            ed.editingFinished.connect(self.on_calcEdit_finished)
            self.calcInputs[k_] = ed
            self.calcBoxLayout.addRow(self.inputNames[k_], ed)    # label: 'name'
        
        line = qtw.QFrame(frameShape=qtw.QFrame.HLine)
        line.setStyleSheet('QFrame {color: lightgrey}')
        self.calcBoxLayout.addRow(line)

        outputLineLabel = qtw.QLabel('=')
        if len(model.option['output']) == 1:
            outputCombo = qtw.QLabel(model.option['output'][0], toolTip='output')
        else:
            outputCombo = qtw.QComboBox(toolTip='output')
            outputCombo.addItems(model.option['output'])
            outputCombo.currentTextChanged.connect(self.on_optionCombos_changed)
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
        self.calcBoxLayout.addRow(calcLayout)

        plotBox = qtw.QGroupBox('Diagramm')
        self.plotBoxLayout = qtw.QFormLayout(plotBox)
        self.plotInputs = {}
        for k_ in qtys:
            text = '; '.join([f'{q_}' for q_ in qtys[k_]])    # input delimiter
            ed = qtw.QLineEdit(text, toolTip=k_)
            ed.setPlaceholderText(text)
            ed.setClearButtonEnabled(True)
            ed.setMinimumWidth(MIN_EDIT_WIDTH)
            ed.editingFinished.connect(self.on_plotEdit_finished)
            ed.returnPressed.connect(self.on_plotEdit_returnPressed)
            self.plotInputs[k_] = ed
            self.plotBoxLayout.addRow(self.inputNames[k_], ed)    # label: 'name'
        
        line = qtw.QFrame(frameShape=qtw.QFrame.HLine)
        line.setStyleSheet('QFrame {color: lightgrey}')  
        self.plotBoxLayout.addRow(line)

        self.plotXCombo = qtw.QComboBox(toolTip='Laufvariable')
        self.plotXCombo.addItems(self.inputNames.values())
        self.plotXCombo.setCurrentText(self.inputNames[self.plotX])
        self.plotXCombo.currentIndexChanged.connect(self.on_plotXCombo_changed)
        self.plotNumOfPts = qtw.QSpinBox(toolTip='Datenpunkte', minimum=2, maximum=1001)
        self.plotNumOfPts.setValue(NUM_OF_DATAPOINTS)
        self.plotNumOfPts.setKeyboardTracking(False)    # do not emit signals while typing
        self.plotNumOfPts.valueChanged.connect(self.plot_updatePending)
        plotNumOfPtsLabel = qtw.QLabel('Punkte')
        self.plotMin = qtw.QCheckBox('Min.', tristate=True)
        self.plotMin.setToolTip('Markiere und beschrifte das erste Minimum')
        self.plotMin.stateChanged.connect(self.plot_updatePending)
        self.plotMax = qtw.QCheckBox('Max.', tristate=True)
        self.plotMax.setToolTip('Markiere und beschrifte das erste Maximum')
        self.plotMax.stateChanged.connect(self.plot_updatePending)
        
        # Input/Output: Plot
        self.plotBtn_icons = (self.style().standardIcon(qtw.QStyle.SP_BrowserReload),
                              self.style().standardIcon(qtw.QStyle.SP_BrowserStop))
        self.plotBtn = qtw.QPushButton(self.plotBtn_icons[0], '', toolTip='Zeichne')
        self.plotBtn.setDefault(True)
        self.plotBtn.clicked.connect(self.on_plotBtn_clicked)
        
        plotStateOkay = qtw.QLabel('✔', styleSheet='QLabel {color: green;}')
        plotStateChgd = qtw.QLabel(' !', styleSheet='QLabel {color: DarkOrange; font-weight:bold;}')
        svg_str = '''
        <svg version="1.1" xmlns="http://www.w3.org/2000/svg"
        width="8px" height="16px" viewBox="0 0 8 16">
        <rect width="100%" height="100%" fill="none" />
        <circle cx="4" cy="4" r="4" fill="DarkOrange">
            <animateTransform attributeName="transform" dur="1s"
            type="translate" values="0 0; 0 16; 0 0" repeatCount="indefinite"/>
        </circle>
        </svg>
        '''
        plotStateBusy = qts.QSvgWidget()
        plotStateBusy.renderer().load(bytearray(svg_str, encoding='utf-8'))
        plotStateBusy.renderer().setAspectRatioMode(qtc.Qt.KeepAspectRatio)
        plotStateBusy.setFixedSize(plotStateOkay.sizeHint())

        self.plotState = qtw.QStackedWidget()
        self.plotState.addWidget(plotStateOkay)
        self.plotState.addWidget(plotStateBusy)
        self.plotState.addWidget(plotStateChgd)    # index: 2
        self.plotState.setSizePolicy(qtw.QSizePolicy.Preferred, qtw.QSizePolicy.Fixed)

        plotLayout = qtw.QHBoxLayout()
        plotLayout.addWidget(self.plotXCombo)
        plotLayout.addWidget(self.plotNumOfPts)
        plotLayout.addWidget(plotNumOfPtsLabel)
        plotLayout.addWidget(self.plotMin)
        plotLayout.addWidget(self.plotMax)
        plotLayout.addWidget(self.plotBtn)
        plotLayout.addWidget(self.plotState)
        self.plotBoxLayout.addRow(plotLayout)

        self.update_rowVisibility()
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

    def plot_isBusy(self, isBusy):
        i_ = int(isBusy==True)    # bool to int
        self.plotBtn.setEnabled(not isBusy)
        self.plotBtn.setIcon(self.plotBtn_icons[i_])
        self.plotState.setCurrentIndex(i_)

    def plot_updatePending(self):
        self.plotState.setCurrentIndex(2)    # set QStackedWidget
    
    def calc(self):
        qty = {}
        for k_, v_ in self.calcInputs.items():
            qty[k_] = Q_(v_.text())
        y = self.calc_series(None, qty, self.option)
        y = y.item()    # possible 1d ndarray to Python scalar
        self.calcPoint = (qty , y)    # with all possible x values
        self.outputLine.setText(f'{y:.9g~P}')

    def getImage(self):
        """Get image corresponding to model.name and optional numbering from option"""
        validNums = []
        # get image file names (exclude the .py files which end with 'y')
        for f_ in g_modeldir.glob(self.model.name + '*[!y]'):
            numFromFile = f_.stem.replace(self.model.name, '')
            num = ''
            for i_ in range(len(numFromFile)):
                # get active option index (indexing of dict)
                index = list(self.model.option.values())[i_].index(list(self.option.values())[i_])
                if numFromFile[i_] in ('0', str(index+1)):
                    num += numFromFile[i_]
                else:
                    break
            validNums.append(num)
        num = max(validNums, key=len) if validNums else ''    # get most specific numbering
        
        # get file or return
        file = Path(g_modeldir, self.model.name + num)
        svgAvailable = Path(file,'.svg').exists()
        pixmap = qtg.QPixmap(file)    # loader guesses the image file format
        if not svgAvailable and pixmap.isNull():
            return
        
        if not self.image:
            # create image widget if necessary
            self.image = qts.QSvgWidget() if svgAvailable else qtw.QLabel()
        if svgAvailable:
            self.image.load(file + '.svg')
            self.image.renderer().setAspectRatioMode(qtc.Qt.KeepAspectRatio)
        else:
            pixmap.setDevicePixelRatio(self.devicePixelRatioF())    # use high-DPI displays
            if pixmap.height() > MAX_IMAGE_HEIGHT:
                pixmap = pixmap.scaledToHeight(MAX_IMAGE_HEIGHT, qtc.Qt.SmoothTransformation)
            self.image.setPixmap(pixmap)

    def update_rowVisibility(self):
        self.inputRelevance = {}
        for k_, v_ in self.inputForOption.items():
            # at least one common element
            self.inputRelevance[k_] = bool( set(self.option.values()) & set(v_) )
        listOfinputKey = list(self.inputNames.keys())
        for k_, v_ in self.inputRelevance.items():
            i_ = listOfinputKey.index(k_)
            self.calcBoxLayout.setRowVisible(i_, v_)
            self.plotBoxLayout.setRowVisible(i_, v_)
            if not v_ and self.plotXCombo.currentIndex() == i_:
                self.plotXCombo.setCurrentIndex(-1)    # reset to no item set
            self.plotXCombo.model().item(i_).setEnabled(v_)

    def on_calcEdit_finished(self):
        self.calc()
        self.on_plotCalc_stateChanged(self.plotCalc.checkState())

    def on_optionCombos_changed(self, text):
        k_ = self.sender().toolTip()
        self.option[k_] = text
        self.getImage()
        self.update_rowVisibility()
        self.calc()
        if k_ == 'output':
            self.on_plotBtn_clicked()
        else:
            self.plot_updatePending()

    def on_plotCalc_stateChanged(self, state):
        state = self.plotCalc.checkState()    # BUG of Pyside6: state is int instead of object
        self.outputPlot.markCalculation(state)    # does not replot lines
        self.outputPlot.ax.figure.canvas.draw()

    def on_plotEdit_finished(self):
        ed = self.sender()
        if not ed.text():
            ed.setText(ed.placeholderText())    # fill with default values
        self.plot_updatePending()
    
    def on_plotEdit_returnPressed(self):
        self.on_plotBtn_clicked()

    def on_plotXCombo_changed(self, index):
        self.plotX = list(self.inputNames.keys())[index] if index != -1 else ''
        self.plot_updatePending()

    def on_plotBtn_clicked(self):
        if self.plotX:
            self.outputPlot.plot()
    
    def calc_series(self, x, qty, opt):
        """Pass a normalized data series (control variable x, parameters) to the model"""
        qty = qty.copy()    # changes are only for normalized calculation
        for k_ in qty:
            qty[k_] = qty[k_].to_base_units()
        if x is not None:
            qty[self.plotX] = x.to_base_units()    # pint array using numpy
        return self.calcModel(Q_, qty, opt)

class ModelPlot(qtw.QWidget):
    """The plot part of the model's GUI"""
    
    class PlotData():
        def __init__(self, x, qty, opt):
            self.x = x
            self.qty = qty
            self.opt = opt
            self.result = None
    
    class CalcWorker(qtc.QRunnable):
        """Calculate new PlotData in thread"""
        class Signals(qtc.QObject):
            completed = qtc.Signal()
        
        def __init__(self, ref):
            super().__init__()
            self.ref = ref    # reference ModelPlot object
            self.signals = self.Signals()

        def run(self):
            for p_ in self.ref.plots:
                if p_.result is None:
                    p_.result = self.ref.parent().calc_series(p_.x, p_.qty, p_.opt)
            self.signals.completed.emit()

    def __init__(self, parent):
        super().__init__(parent)

        layout = qtw.QVBoxLayout(self)
        px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        # figsize: Figure dimension (width, height) in inches
        fig = plt.figure(figsize=(600*px, 400*px))
        canvas = FigureCanvas(fig)
        self.ax = canvas.figure.subplots()
        
        # https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        layout.addWidget(NavigationToolbar(canvas, self))
        layout.addWidget(canvas)

        # For the cursor to remain responsive you must keep a reference to it.
        # Set useblit=True on most backends for enhanced performance.
        self.cursor = mpl.widgets.Cursor(self.ax, useblit=True, color='grey', linewidth=0.5)

        self.plots = []    # PlotData
        self.overlay = []    # annotations to remove

    def plot(self):
        """Plot with simple threading for responsive GUI"""
        parent = self.parent()
        parent.plot_isBusy(True)

        self.legendKeys = []
        family, qty = {}, {}
        for k_, v_ in parent.plotInputs.items():
            if not parent.inputRelevance.get(k_, True):
                continue
            # persistent and visible optional inputs (see update_rowVisibility)
            texts = v_.text().split(';')    # input delimiter, split always returns a list
            texts = [s_.strip() for s_ in texts]    # remove leading and trailing spaces
            if k_ == parent.plotX:
                x = np.linspace(Q_(texts[0]), Q_(texts[-1]), parent.plotNumOfPts.value())
            elif len(set(texts)) == 1:
                qty[k_] = Q_(texts[0])    # k_ not containing different values
            else:
                family[k_] = texts
                self.legendKeys.append(k_)

        numOfPlots = 1
        if family:
            numOfPlots = min([len(v_) for v_ in family.values()])    # shortest family

        if numOfPlots <= len(self.plots):
            self.plots = self.plots[:numOfPlots]    # shorten or keep list
        else:
            self.plots.extend([None] * (numOfPlots-len(self.plots)))    # expand list
        opt = parent.option
        for n_, p_ in enumerate(self.plots):
            # update plots if necessary
            for f_ in family:
                qty[f_] = Q_(family[f_][n_])
            same = True if p_ else False
            same = np.equal(p_.opt, opt).all() if same else False    # opt equal
            same = np.equal(p_.qty, qty).all() if same else False    # qty equal
            same = np.equal(p_.x, x).all() if same and len(p_.x)==len(x) else False    # x equal
            # BUG: numpy.array_equal not implemented for pint.util.Quantity
            if not same:
                self.plots[n_] = ModelPlot.PlotData(x, qty.copy(), opt.copy())

        # Threading
        worker = ModelPlot.CalcWorker(self)
        worker.signals.completed.connect(self.plot_post)
        qtc.QThreadPool.globalInstance().start(worker)
        
    def plot_post(self):
        """Continue plot()"""
        parent = self.parent()        
        self.ax.clear()    # clear old plots
        try:
            for p_ in self.plots:
                self.ax.plot(p_.x, p_.result, '-', label=self.legendText(p_.qty))
        except Exception as ex:
            msg = f'Fehler in Modellrückgabe:\n{type(ex).__name__}: {ex}'
            error(self, msg)
        else:
            if self.legendKeys:
                self.ax.legend()
            self.markExtremum((parent.plotMin.checkState(), parent.plotMax.checkState()))
            self.markCalculation(parent.plotCalc.checkState())
            # fits plot within figure cleanly and allows to modify borders afterwards
            self.ax.figure.tight_layout()
        finally:
            self.ax.figure.canvas.draw()
            parent.plot_isBusy(False)
    
    def legendText(self, dictionary):
        texts = [f'{v_}' for k_, v_ in dictionary.items() if k_ in self.legendKeys]
        return ', '.join(texts)
    
    def markExtremum(self, markMinMax):
        gid = 'extrema'    # gid: custom id
        if set(markMinMax) == set([qtc.Qt.Unchecked]):    # all Unchecked
            return
        align = ('top', 'bottom')    # verticalalignment of min and max label
        funcs = (np.argmin, np.argmax)
        numberOfLines = len(self.ax.lines)    # changes with plot of extrema
        for i_ in (0,1):
            if markMinMax[i_] == qtc.Qt.Unchecked:
                continue
            x = y = np.empty(0)
            for n_ in range(numberOfLines):
                yall = self.ax.lines[n_].get_ydata()    # .get_ydata is numpy array of quantities
                index = funcs[i_](yall)    # indices of extrema at first occurrence
                x = np.append(x, self.ax.lines[n_].get_xdata()[index])
                y = np.append(y, yall[index])
                if markMinMax[i_] == qtc.Qt.Checked:
                    self.labelPoint((x[-1].magnitude, y[-1].magnitude), align[i_])
            label = '_' + gid + str(i_)    # label=_ does not show up in legend
            self.ax.plot(x, y, linestyle='', marker=7-i_, color='red', label=label, gid=gid)

    def markCalculation(self, mark):
        gid = 'calc'    # gid: custom id
        # reset marker
        if self.ax.lines[-1].get_gid() == gid:
            self.ax.lines[-1].remove()    # remove old markers
            self.ax.legend()    # update legend
        if self.overlay:
            self.overlay.remove()    # remove old annotation
            self.overlay = []
        if mark == qtc.Qt.Unchecked:
            return
        # set marker
        parent = self.parent()
        xs, y = parent.calcPoint    # with all possible x values
        x = xs[parent.plotX]
        self.ax.plot(x, y, 'x', color='red', label=self.legendText(xs), gid=gid)
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

def htmlTable(table):
    """Convert tuple of tuples for row and column into html representation"""
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
    return '<table>' + text + '</table>'

def error(parent, message):
    print(message)
    qtw.QMessageBox.critical(parent, 'Error', message)

if __name__ == '__main__':
    print('Debug Window')    # TODO: Console window is only for debugging
    app = qtw.QApplication()
    window = MainWindow()
    window.show()
    app.exec() 
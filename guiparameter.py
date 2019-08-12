from PyQt5 import QtGui, QtCore
import sys, os
from PyQt5.QtWidgets import*
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np
import re
from copy import copy

allPortalParameters = {}

class CheckableComboBox(QComboBox):
    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))
        self._changed = False
        self.DisplayRectDelta = QRect(5, 0, 140, 24)
        self.displayText = '<None>'
        self.lastClicked = ''
        self.lastClickedState = False

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
            self.lastClickedState = False
        else:
            item.setCheckState(QtCore.Qt.Checked)
            self.lastClickedState = True
        self._changed = True
        self.updateDisplayText()
        self.repaint()
        self.lastClicked = item.text()


    def getItemsChecked(self):
        itemsChecked = []
        for i in range(self.count()):
            ob = self.model().item(i, 0)
            if ob.checkState() == QtCore.Qt.Checked:
                itemsChecked.append(ob.text())
        return itemsChecked

    def hidePopup(self):
        if not self._changed:
            super(CheckableComboBox, self).hidePopup()
        self._changed = False

    def updateDisplayText(self):
        textRect = QRect().adjusted(self.DisplayRectDelta.left(), self.DisplayRectDelta.top(),
                                    self.DisplayRectDelta.right(), self.DisplayRectDelta.bottom())
        fontMetrics = QFontMetrics(self.font())
        self.displayText = ", ".join(self.getItemsChecked())
        if (fontMetrics.size(QtCore.Qt.TextSingleLine, self.displayText).width() > textRect.width()):
            while ((not self.displayText == '') and fontMetrics.size(QtCore.Qt.TextSingleLine, self.displayText + "...").width() > textRect.width()-10):
                self.displayText = self.displayText[:-1]
            self.displayText += "..."

    def paintEvent(self, e: QtGui.QPaintEvent):
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(QPalette.Text))
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        painter.drawComplexControl(QStyle.CC_ComboBox, option)
        textRect = QRect().adjusted(self.DisplayRectDelta.left(), self.DisplayRectDelta.top(),
                                     self.DisplayRectDelta.right(), self.DisplayRectDelta.bottom())
        painter.drawText(textRect, QtCore.Qt.AlignVCenter, self.displayText)

    def resizeEvent(self, e: QtGui.QResizeEvent):
        self.updateDisplayText()

class WLineEdit(QLineEdit):
    guiValueChanged = pyqtSignal(list)
    def __init__(self, id):
        super(WLineEdit, self).__init__()
        self.editingFinished.connect(lambda: self.guiValueChanged.emit([self.text()]))
        self.id = id + 'Box'
        self.setObjectName(self.id)

    def setGuiValue(self, val, quiet = False):
        val = val[0]
        self.clear()
        if (not (val is None)):
            self.setText(str(val))
            if not quiet:
                self.guiValueChanged.emit([self.text()])

    def wrapToBox(self, holdingGrid):
        self.setAlignment(Qt.AlignCenter)
        self.setWindowTitle(self.id)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        if not (holdingGrid is None):
            holdingGrid.addWidget(self)

    def reset(self, Param):
        self.setGuiValue([str(Param.default)])

class WComboBox(QComboBox):
    guiValueChanged = pyqtSignal(list)
    def __init__(self, id):
        super(WComboBox, self).__init__()
        self.activated.connect(lambda: self.guiValueChanged.emit([self.currentText()]))
        self.id = id + 'Box'
        self.setObjectName(self.id)

    def setGuiValue(self, val, quiet = False):
        val = val[0]
        ind = self.findText(str(val))
        if ind<0:
            ind = 0
            val = self.currentText()
        self.setCurrentIndex(ind)
        if not quiet:
            self.guiValueChanged.emit([str(val)])

    def wrapToBox(self, holdingGrid):
        self.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.setWindowTitle(self.id)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        if not (holdingGrid is None):
            holdingGrid.addWidget(self)

    def reset(self, Param):
        self.clear()
        if not (Param.possibleValues is None):
            for i, item in enumerate(Param.possibleValues):
                self.addItem(str(item))
        self.setGuiValue([Param.default])

class WCheckBox(QCheckBox):
    guiValueChanged = pyqtSignal(list)
    def __init__(self, id):
        super(WCheckBox, self).__init__()
        self.stateChanged.connect(lambda: self.guiValueChanged.emit([self.isChecked()]))
        self.id = id + 'Box'
        self.setObjectName(self.id)

    def setGuiValue(self, val, quiet = False):
        val=val[0]
        if val:
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)
        if not quiet:
            self.guiValueChanged.emit([val])

    def wrapToBox(self, holdingGrid):
        self.setFocusPolicy(Qt.NoFocus)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        if not (holdingGrid is None):
            holdingGrid.addWidget(self)
            holdingGrid.setAlignment(Qt.AlignCenter)

    def reset(self, Param):
        self.setText(Param.name)
        self.setGuiValue([Param.default])

class WCheckedComboBox(CheckableComboBox):
    guiValueChanged = pyqtSignal(list)
    def __init__(self, id):
        super(WCheckedComboBox, self).__init__()
        self.activated.connect(lambda: self.guiValueChanged.emit(self.getItemsChecked()))
        self.id = id + 'Box'
        self.setObjectName(self.id)

    def setGuiValue(self, vals, quiet = False):
        vals = vals[0]
        for i in range(self.count()):
            ob = self.model().item(i, 0)
            if (ob.text() in vals):
                ob.setCheckState(Qt.Checked)
            else:
                ob.setCheckState(Qt.Unchecked)
        if not quiet:
            self.guiValueChanged.emit(vals)

    def wrapToBox(self, holdingGrid):
        self.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.setWindowTitle(self.id)
        if not (holdingGrid is None):
            holdingGrid.addWidget(self)

    def reset(self, Param):
        self.blockSignals(True)
        self.clear()
        if (not (Param.possibleValues is None)):
            for i, item in enumerate(Param.possibleValues):
                self.addItem(item)
                ob = self.model().item(i, 0)
                ob.setCheckState(Qt.Unchecked)
        self.setGuiValue([Param.default])
        self.blockSignals(False)

class WBrowseBox(QPushButton):
    guiValueChanged = pyqtSignal(list)
    browsed = pyqtSignal()
    def __init__(self, id):
        super(WBrowseBox, self).__init__()
        self.clicked.connect(self.onBrowse)
        self.id = id + 'Box'
        self.setObjectName(self.id)
        self.directory = ''

    def setGuiValue(self, val, quiet = False):
        val=val[0]
        if not val or val == '':
            self.setText('Browse...')
        else:
            fld = re.split(r'[\\]+', val)
            self.setText(fld[-1])
        if not quiet:
            self.guiValueChanged.emit([val])

    def wrapToBox(self, holdingGrid):
        if not (holdingGrid is None):
            holdingGrid.addWidget(self)

    def reset(self, Param):
        self.setGuiValue([Param.default])

    def onBrowse(self):
        directory = os.path.normpath(QFileDialog.getExistingDirectory(self))
        if (directory != ''):
            self.setGuiValue([directory])

class GenericPortalParameter(QObject):
    valueChanged = pyqtSignal()
    passToGUI=pyqtSignal(list,bool)
    def __init__(self, id, name, requiredWidgetFun, isMandatory=False, defaultVal=None, datatype = None):
        super().__init__()
        self.mandatory = isMandatory
        self.name = name
        self.id = id
        self.datatype = datatype
        self.default = defaultVal
        self.currentValue = defaultVal
        self.dictsForChildren = dict(dict())
        self.reqWidFun = requiredWidgetFun
        # self.widget = requiredWidgetFun(id)
        self.widget = None
        allPortalParameters[id] = defaultVal

    def initWidget(self):
        self.widget = self.reqWidFun(self.id)
        self.widget.guiValueChanged.connect(self.updateValueFromGUI)
        self.passToGUI.connect(self.widget.setGuiValue)
        self.widget.reset(self)

    def setDependency(self, dependencyFun, dependencyParam = None, *args):
        if (dependencyParam):
            self.valueChanged.connect(lambda: dependencyParam.updateFromExternal(dependencyFun, *args))
        else:
            self.valueChanged.connect(lambda: self.updateFromExternal(dependencyFun, *args))

    def updateFromExternal(self, dependencyFun, *args):
        valueToSet = dependencyFun(self.sender(), self, *args)
        self.setValue(valueToSet)
        self.passToGUI.emit([valueToSet],False)

    def updateValueFromGUI(self, valList):
        pass

    def setValue(self, value, updateGUI = False):
        valueBefore = self.currentValue
        self.currentValue = value
        allPortalParameters[self.id] = value
        if not (valueBefore == self.currentValue):
            self.valueChanged.emit()
        if updateGUI:
            self.passToGUI.emit([self.currentValue], False)

    def resetValue(self, default = None):
        if default:
            self.default = default
        self.setValue(self.default)
        self.passToGUI.emit([self.default],False)

class TextInputPortalParameter(GenericPortalParameter):
    def __init__(self, id, name, isMandatory=False, defaultVal=None, datatype=None, minVal = None, maxVal = None):
        self.minVal = minVal
        self.maxVal = maxVal
        super(TextInputPortalParameter, self).__init__(id, name, WLineEdit, isMandatory, defaultVal, datatype)
        self.initWidget()

    def updateValueFromGUI(self, valList):
        try:
            val = self.datatype(valList[0])
            self.setValue(val)
        except:
            typeExceptMsg()
            self.resetValue()
        if not (self.maxVal is None) and (not (self.minVal is None)):
            if (self.currentValue > self.maxVal) or (self.currentValue < self.minVal):
                valExceptMsg(self)
                self.resetValue()

class BinaryPortalParameter(GenericPortalParameter):
    def __init__(self, id, name, isMandatory=False, defaultVal=False):
        super(BinaryPortalParameter,self).__init__(id, name, WCheckBox, isMandatory, defaultVal, bool)
        self.initWidget()

    def updateValueFromGUI(self, valList):
        self.setValue(bool(valList[0]))

class SingleSelectPortalParameter(GenericPortalParameter):
    def __init__(self, id, name, isMandatory=False , possibleValues = [], defaultVal='', datatype=None):
        super(SingleSelectPortalParameter, self).__init__(id, name, WComboBox, isMandatory, defaultVal, datatype)
        self.possibleValues = possibleValues
        if defaultVal is None:
            self.possibleValues.insert(0,None)
            self.default = possibleValues[0]
            self.currentValue = self.default
        self.initWidget()

    def updateValueFromGUI(self, valList):
        val = valList[0]
        if self.datatype and not (val=='None'):
            val = self.datatype(val)
        self.setValue(val)

class MultiSelectPortalParameter(GenericPortalParameter):
    def __init__(self, id, name, isMandatory=False, possibleValues =[], defaultVal=[], datatype=None, addAllButton = False):
        super(MultiSelectPortalParameter, self).__init__(id, name, WCheckedComboBox, isMandatory, defaultVal, datatype)
        self.possibleValues = possibleValues
        self.addAll = addAllButton
        self.initWidget()

    def updateValueFromGUI(self, valList):
        value = valList
        if self.addAll:
            if '--All--' in valList and not '--All--' in self.currentValue:
                value = self.possibleValues
                self.passToGUI.emit([value], True)
            elif not '--All--' in valList and '--All--' in self.currentValue:
                value = []
                self.passToGUI.emit([value], True)
        if self.datatype:
            value = [self.datatype(val) for val in value]
        self.setValue(value)

class BrowsePortalParameter(GenericPortalParameter):
    def __init__(self, id, name, mode = 'dir', isMandatory=False, defaultVal='', datatype=None):
        super(BrowsePortalParameter, self).__init__(id, name, WBrowseBox, isMandatory, defaultVal, datatype)
        self.mode = mode
        self.initWidget()

    def updateValueFromGUI(self, valList):
        self.setValue(valList[0])

def setParamsForGUI():
    #Common Parameters
    fts_1 = [['FFT','Gabor', 'Haar'], []]
    fts_2 = [['Mama', 'Papa', 'Ya', 'Homyak'], ['Papa', 'Ya']]

    vals_1 = [[1, 2, 3], 2]
    vals_2 = [[4, 5, 6], 6]

    dependencyDict1 = {}
    dependencyDict1[0] = vals_1
    dependencyDict1[100] = vals_1
    dependencyDict1[200] = vals_1
    dependencyDict1[300] = vals_2
    dependencyDict1[400] = vals_2

    dependencyDict2 = {}
    dependencyDict2[2] = fts_1
    dependencyDict2[4] = fts_2
    dependencyDict2[5] = [[],[]]

    FsParam = SingleSelectPortalParameter('Fs', 'Я зависим-1', True, vals_1[0], vals_1[1], datatype=int)
    FeatureMainParam = SingleSelectPortalParameter('FDepPar', 'Главный',True, list(range(0,500,100)), defaultVal=100, datatype=int)
    LowFsParam = TextInputPortalParameter('lowFs', 'Нижняя частота, Гц', True, datatype=float, defaultVal=1.0,
                                 minVal=0.1, maxVal=100)
    HighFsParam = TextInputPortalParameter('lowFs', 'Верхняя частота, Гц', True, datatype=float, defaultVal=3.0,
                                          minVal=0.1, maxVal=100)
    FeatureDepParam = MultiSelectPortalParameter('Ft', 'Я зависим-2', isMandatory=True, defaultVal=fts_1[1],
                                  possibleValues=fts_1[0])
    WsParam = BinaryPortalParameter('Ws', 'Окей?', True, defaultVal=True)
    BrowseParam = BrowsePortalParameter('GenDir', 'Папка эксперимента', 'dir', True)
    SubjParam = MultiSelectPortalParameter('subj', 'Субъекты', True, [], datatype=str, addAllButton=True)
    SessionParam1 = SingleSelectPortalParameter('sess1', 'Train', True, [], datatype=str)
    SessionParam2 = SingleSelectPortalParameter('sess2', 'Test', True,[], datatype=str)
    PortalPCAParam = SingleSelectPortalParameter('PCA', 'Число главных компонент PCA', False, defaultVal=None, possibleValues=list(range(2,100)), datatype=int)
    PortalSmartClassParam = TextInputPortalParameter('ChooseClass', 'Классы на распознавание', True, '', datatype=str)

    PortalParameters = [[BrowseParam, SubjParam, SessionParam1,SessionParam2, LowFsParam, HighFsParam],[FeatureMainParam, FsParam, FeatureDepParam, WsParam, PortalPCAParam, PortalSmartClassParam]]


    # HighFsParam.setDependency(_setSameValue, LowFsParam)
    HighFsParam.setDependency(_setAtMost, LowFsParam)
    LowFsParam.setDependency(_setAtLeast, HighFsParam)
    FeatureMainParam.setDependency(_resetPossibleValues, FsParam, dependencyDict1)
    FsParam.setDependency(_resetPossibleValues, FeatureDepParam, dependencyDict2)
    FsParam.setDependency(_setInactive, FeatureDepParam, [3,6])
    BrowseParam.setDependency(_getSubjectNames, SubjParam)
    SubjParam.setDependency(_getSessionNames, SessionParam1)
    SubjParam.setDependency(_getSessionNames, SessionParam2)
    PortalSmartClassParam.setDependency(_checkChannelsSet)
    return PortalParameters

def typeExceptMsg():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("Некорректный тип данных!")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def txtExceptMsg(txt):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(txt)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def valExceptMsg(Param):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    if not (Param.minVal is None) and not (Param.maxVal is None):
        msg.setText("Параметр {}, должен иметь значения от {} до {}".format(Param.name, Param.minVal, Param.maxVal))
    else:
        msg.setText("Параметр {} имеет некорректное значение".format(Param.name))
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

#####  Dependency functions #####
def _setSameValue(senderParam, acceptParam):
    return senderParam.currentValue

def _setAtLeast(senderParam, acceptParam):
    if senderParam.currentValue > acceptParam.currentValue:
        return senderParam.currentValue
    return acceptParam.currentValue

def _setAtMost(senderParam, acceptParam):
    if senderParam.currentValue < acceptParam.currentValue:
        return senderParam.currentValue
    return acceptParam.currentValue

def _setInactive(senderParam, acceptParam, listOfSenderValues):
    if senderParam.currentValue in listOfSenderValues:
        acceptParam.widget.setEnabled(False)
    else:
        acceptParam.widget.setEnabled(True)
    return acceptParam.default

def _resetPossibleValues(senderParam, acceptParam, dictValues):
    refVal = senderParam.currentValue
    if not refVal in dictValues.keys():
        return acceptParam.currentValue
    acceptParam.possibleValues = dictValues[refVal][0]
    acceptParam.default = dictValues[refVal][1]
    acceptParam.widget.reset(acceptParam)
    return acceptParam.default

def _getSessionNames(senderParam, acceptParam):
    foldnames = copy(senderParam.currentValue)
    if '--All--' in foldnames:
        foldnames.remove('--All--')
    gendir = senderParam.upperDirectory
    globalSessionNames = None
    if (not gendir) or (not foldnames) or not (os.path.exists(gendir)):
        globalSessionNames = []
    else:
        for fname in foldnames:
            curSessionNames = [name for name in os.listdir(gendir + '//' + fname) if
                    os.path.isdir(os.path.join(gendir + '//' + fname, name))]
            if globalSessionNames is None:
                globalSessionNames = curSessionNames
            else:
                for sName in globalSessionNames:
                    if not sName in curSessionNames:
                        globalSessionNames.remove(sName)
    acceptParam.possibleValues = globalSessionNames
    acceptParam.default = ''
    acceptParam.widget.reset(acceptParam)

def _getSubjectNames(senderParam, acceptParam):
    gendir = senderParam.currentValue
    folds = []
    if not ((gendir is None) or (gendir == '') or not (os.path.exists(gendir))):
        folds = [name for name in os.listdir(gendir) if
                    os.path.isdir(os.path.join(gendir + '//', name))]
    if len(folds)>0:
        acceptParam.possibleValues = folds
        if (acceptParam.addAll):
            acceptParam.possibleValues.insert(0,'--All--')
        acceptParam.default = []
        acceptParam.widget.reset(acceptParam)
        acceptParam.upperDirectory = gendir
        return acceptParam.default
    else:
        acceptParam.possibleValues = []
        acceptParam.default = []
        acceptParam.widget.reset(acceptParam)
        return []

def _checkChannelsSet(senderParam, acceptParam):
    string = senderParam.currentValue
    if (string==''):
        return ''
    strVals = re.split('[,\s;]+', string)
    if (len(strVals)>1):
        try:
            vals = [int(val) for val in strVals]
            if (np.min(np.asarray(vals)))<0:
                txtExceptMsg('Номер класса не может быть меньше 0')
                return ''
        except:
            txtExceptMsg('Введите номера классов через пробел или запятую')
            return ''
        return string
    else:
        txtExceptMsg('Введите номера классов через пробел или запятую')
        return ''

def _checkIcaName(senderParam, acceptParam):
    string = senderParam.currentValue
    if (string[-4:])!='.mat':
        txtExceptMsg('Имя ICA файла должно иметь расширение .mat')
        return ''
    else:
        return string
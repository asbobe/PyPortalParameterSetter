#!/usr/bin/python3
# -*- coding: utf-8 -*-

from guiparameter import *
from PyQt5.QtWidgets import*
from PyQt5.QtGui import *
from PyQt5.QtCore import*

class PortalSetupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.PortalInstanceTrained = False
        self.PortalParameters = setParamsForGUI()
        self.PortalGUIParameters = [self.PortalParameters]
        self.allPortalParameters = dict()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Portal v.0.3')
        self.setWindowIcon(QIcon('Portal.jpg'))
        self.resize(640, 480)
        self.center()

        self.layout = QVBoxLayout()
        self.MainParamTab = QTabWidget(self)
        self.ReaderParamsGrid = QHBoxLayout()
        self.PortalModeGrid = QHBoxLayout()
        self.PortalSmartsGrid = QHBoxLayout()
        self.VGrid = QWidget()
        self.VGrid.layout = QVBoxLayout()
        self.MainParamTab.addTab(self.VGrid, "Main Parameters")

        self.addParamGroup(self.PortalParameters, self.ReaderParamsGrid, self.VGrid, 'Parameters')

        self.VGrid.layout.addStretch()
        self.VGrid.layout.setAlignment(Qt.AlignCenter)
        self.VGrid.setLayout(self.VGrid.layout)

        self.layout.addWidget(self.MainParamTab)
        self.setLayout(self.layout)

    def addParamGroup(self, ParamGroup, ParamGrid, parentGrid, headText):
        label = QLabel(self)
        label.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        label.setText(headText)
        label.setAlignment(Qt.AlignCenter)
        parentGrid.layout.addWidget(label)
        for ParamList in ParamGroup:
            if not (type(ParamList) is list):
                ParamList = list([ParamList])
            smallGrid = QVBoxLayout()
            for Param in ParamList:
                self.addSomeBox(Param, smallGrid)
                smallGrid.addStretch()
            ParamGrid.addLayout(smallGrid)
            ParamGrid.addStretch()
            parentGrid.layout.addLayout(ParamGrid)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def addSomeBox(self, Param, smallGrid):
        if not isinstance(Param.widget, QCheckBox):
            label = QLabel(self)
            label.setText(Param.name)
            label.setAlignment(Qt.AlignCenter)
            label.setObjectName(Param.id + 'Label')
            smallGrid.addWidget(label)
        Param.widget.wrapToBox(smallGrid)
        smallGrid.setObjectName(Param.id)

class MasterWorker(QObject):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.guiWindow = PortalSetupWindow()
        self.guiWindow.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    master = MasterWorker(app)
    sys.exit(app.exec_())


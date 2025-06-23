# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'monitor_page.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(800, 600)
        self.mainLayout = QVBoxLayout(Form)
        self.mainLayout.setSpacing(10)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(10, 10, 10, 10)
        self.titleLabel = QLabel(Form)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.mainLayout.addWidget(self.titleLabel)

        self.controlFrame = QFrame(Form)
        self.controlFrame.setObjectName(u"controlFrame")
        self.controlFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.controlFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.controlLayout = QHBoxLayout(self.controlFrame)
        self.controlLayout.setObjectName(u"controlLayout")
        self.statusLabel = QLabel(self.controlFrame)
        self.statusLabel.setObjectName(u"statusLabel")

        self.controlLayout.addWidget(self.statusLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.controlLayout.addItem(self.horizontalSpacer)

        self.refreshButton = QPushButton(self.controlFrame)
        self.refreshButton.setObjectName(u"refreshButton")
        self.refreshButton.setMinimumSize(QSize(80, 30))

        self.controlLayout.addWidget(self.refreshButton)


        self.mainLayout.addWidget(self.controlFrame)

        self.deviceScrollArea = QScrollArea(Form)
        self.deviceScrollArea.setObjectName(u"deviceScrollArea")
        self.deviceScrollArea.setWidgetResizable(True)
        self.deviceContainer = QWidget()
        self.deviceContainer.setObjectName(u"deviceContainer")
        self.deviceContainer.setGeometry(QRect(0, 0, 778, 464))
        self.deviceLayout = QVBoxLayout(self.deviceContainer)
        self.deviceLayout.setSpacing(10)
        self.deviceLayout.setObjectName(u"deviceLayout")
        self.deviceLayout.setContentsMargins(10, 10, 10, 10)
        self.deviceSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.deviceLayout.addItem(self.deviceSpacer)

        self.deviceScrollArea.setWidget(self.deviceContainer)

        self.mainLayout.addWidget(self.deviceScrollArea)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Device Monitor", None))
        self.titleLabel.setStyleSheet(QCoreApplication.translate("Form", u"QLabel {\n"
"    font-size: 18px;\n"
"    font-weight: bold;\n"
"    color: #333;\n"
"    padding: 10px;\n"
"}", None))
        self.titleLabel.setText(QCoreApplication.translate("Form", u"Device Monitor", None))
        self.statusLabel.setText(QCoreApplication.translate("Form", u"Connected Devices: 0", None))
        self.refreshButton.setText(QCoreApplication.translate("Form", u"Refresh", None))
        self.deviceScrollArea.setStyleSheet(QCoreApplication.translate("Form", u"QScrollArea {\n"
"    border: 1px solid #ccc;\n"
"    border-radius: 5px;\n"
"    background-color: #f9f9f9;\n"
"}", None))
    # retranslateUi


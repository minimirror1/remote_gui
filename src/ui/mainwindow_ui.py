# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget,
    QStatusBar, QVBoxLayout, QWidget)
import _icons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(962, 700)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.leftMenuSubContainer = QWidget(self.centralwidget)
        self.leftMenuSubContainer.setObjectName(u"leftMenuSubContainer")
        self.leftMenuSubContainer.setMinimumSize(QSize(200, 0))
        self.leftMenuSubContainer.setMaximumSize(QSize(200, 16777215))
        self.verticalLayout = QVBoxLayout(self.leftMenuSubContainer)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalWidget = QWidget(self.leftMenuSubContainer)
        self.horizontalWidget.setObjectName(u"horizontalWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalWidget.sizePolicy().hasHeightForWidth())
        self.horizontalWidget.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.menuButton = QPushButton(self.horizontalWidget)
        self.menuButton.setObjectName(u"menuButton")
        self.menuButton.setMinimumSize(QSize(50, 0))
        self.menuButton.setMaximumSize(QSize(50, 16777215))
        icon = QIcon()
        icon.addFile(u":/feather/icons/feather/align-justify.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.menuButton.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.menuButton)


        self.verticalLayout.addWidget(self.horizontalWidget)

        self.verticalFrame = QFrame(self.leftMenuSubContainer)
        self.verticalFrame.setObjectName(u"verticalFrame")
        self.verticalFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.verticalFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.verticalFrame)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.HomeButton = QPushButton(self.verticalFrame)
        self.HomeButton.setObjectName(u"HomeButton")

        self.verticalLayout_7.addWidget(self.HomeButton)

        self.PlayButton = QPushButton(self.verticalFrame)
        self.PlayButton.setObjectName(u"PlayButton")

        self.verticalLayout_7.addWidget(self.PlayButton)

        self.jogButton = QPushButton(self.verticalFrame)
        self.jogButton.setObjectName(u"jogButton")

        self.verticalLayout_7.addWidget(self.jogButton)


        self.verticalLayout.addWidget(self.verticalFrame)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.verticalFrame_2 = QFrame(self.leftMenuSubContainer)
        self.verticalFrame_2.setObjectName(u"verticalFrame_2")
        self.verticalFrame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.verticalLayout_8 = QVBoxLayout(self.verticalFrame_2)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.SettingButton = QPushButton(self.verticalFrame_2)
        self.SettingButton.setObjectName(u"SettingButton")

        self.verticalLayout_8.addWidget(self.SettingButton)

        self.HelpButton = QPushButton(self.verticalFrame_2)
        self.HelpButton.setObjectName(u"HelpButton")

        self.verticalLayout_8.addWidget(self.HelpButton)


        self.verticalLayout.addWidget(self.verticalFrame_2)


        self.horizontalLayout.addWidget(self.leftMenuSubContainer)

        self.mainBodyContainer = QWidget(self.centralwidget)
        self.mainBodyContainer.setObjectName(u"mainBodyContainer")
        self.verticalLayout_3 = QVBoxLayout(self.mainBodyContainer)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.headerContainer = QWidget(self.mainBodyContainer)
        self.headerContainer.setObjectName(u"headerContainer")
        self.headerContainer.setMinimumSize(QSize(0, 0))
        self.headerContainer.setMaximumSize(QSize(16777215, 30))
        self.horizontalLayout_3 = QHBoxLayout(self.headerContainer)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.tempFrame = QFrame(self.headerContainer)
        self.tempFrame.setObjectName(u"tempFrame")
        self.horizontalLayout_6 = QHBoxLayout(self.tempFrame)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")

        self.horizontalLayout_3.addWidget(self.tempFrame)

        self.windowBtnFrame = QFrame(self.headerContainer)
        self.windowBtnFrame.setObjectName(u"windowBtnFrame")
        self.windowBtnFrame.setMaximumSize(QSize(100, 16777215))
        self.windowBtnFrame.setStyleSheet(u"")
        self.horizontalLayout_5 = QHBoxLayout(self.windowBtnFrame)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.minimizeBtn = QPushButton(self.windowBtnFrame)
        self.minimizeBtn.setObjectName(u"minimizeBtn")
        icon1 = QIcon()
        icon1.addFile(u":/feather/icons/feather/window_minimize.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.minimizeBtn.setIcon(icon1)

        self.horizontalLayout_5.addWidget(self.minimizeBtn)

        self.restoreBtn = QPushButton(self.windowBtnFrame)
        self.restoreBtn.setObjectName(u"restoreBtn")
        icon2 = QIcon()
        icon2.addFile(u":/feather/icons/feather/window_undock.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.restoreBtn.setIcon(icon2)

        self.horizontalLayout_5.addWidget(self.restoreBtn)

        self.closeBtn = QPushButton(self.windowBtnFrame)
        self.closeBtn.setObjectName(u"closeBtn")
        icon3 = QIcon()
        icon3.addFile(u":/feather/icons/feather/x.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closeBtn.setIcon(icon3)

        self.horizontalLayout_5.addWidget(self.closeBtn)


        self.horizontalLayout_3.addWidget(self.windowBtnFrame)


        self.verticalLayout_3.addWidget(self.headerContainer)

        self.frame = QFrame(self.mainBodyContainer)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 50))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(2, 2, 2, 2)
        self.mainPage = QStackedWidget(self.frame)
        self.mainPage.setObjectName(u"mainPage")
        self.mainPage.setMinimumSize(QSize(0, 0))
        self.mainPage.setFrameShape(QFrame.Shape.StyledPanel)
        self.JogPage = QWidget()
        self.JogPage.setObjectName(u"JogPage")
        self.pushButton_3 = QPushButton(self.JogPage)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(310, 160, 75, 24))
        self.mainPage.addWidget(self.JogPage)
        self.PlayPage = QWidget()
        self.PlayPage.setObjectName(u"PlayPage")
        self.pushButton_2 = QPushButton(self.PlayPage)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(300, 150, 75, 24))
        self.mainPage.addWidget(self.PlayPage)
        self.HomePage = QWidget()
        self.HomePage.setObjectName(u"HomePage")
        self.pushButton = QPushButton(self.HomePage)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(310, 150, 75, 24))
        self.mainPage.addWidget(self.HomePage)

        self.horizontalLayout_7.addWidget(self.mainPage)


        self.verticalLayout_3.addWidget(self.frame)


        self.horizontalLayout.addWidget(self.mainBodyContainer)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.mainPage.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.menuButton.setText("")
        self.HomeButton.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.PlayButton.setText(QCoreApplication.translate("MainWindow", u"Play", None))
        self.jogButton.setText(QCoreApplication.translate("MainWindow", u"Jog", None))
        self.SettingButton.setText(QCoreApplication.translate("MainWindow", u"Setting", None))
        self.HelpButton.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.minimizeBtn.setText("")
        self.restoreBtn.setText("")
        self.closeBtn.setText("")
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"1", None))
    # retranslateUi


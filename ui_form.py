# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QSizePolicy,
    QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(800, 600)
        self.minusButton = QPushButton(Widget)
        self.minusButton.setObjectName(u"minusButton")
        self.minusButton.setGeometry(QRect(500, 380, 75, 24))
        self.plusButton = QPushButton(Widget)
        self.plusButton.setObjectName(u"plusButton")
        self.plusButton.setGeometry(QRect(500, 320, 75, 24))
        self.label = QLabel(Widget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(400, 340, 48, 16))

        # 현재 값을 저장할 변수 초기화
        self.current_value = 0
        self.label.setText(QCoreApplication.translate("Widget", str(self.current_value), None))
        
        # 버튼 시그널 연결
        self.plusButton.clicked.connect(self.increment_value)
        self.minusButton.clicked.connect(self.decrement_value)

        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.minusButton.setText(QCoreApplication.translate("Widget", u"-", None))
        self.plusButton.setText(QCoreApplication.translate("Widget", u"+", None))
        self.label.setText(QCoreApplication.translate("Widget", u"TextLabel", None))
    # retranslateUi
    def update_label_value(self, value):
        self.label.setText(QCoreApplication.translate("Widget", str(value), None))

    def increment_value(self):
        self.current_value += 1
        self.update_label_value(self.current_value)
    
    def decrement_value(self):
        self.current_value -= 1
        self.update_label_value(self.current_value)

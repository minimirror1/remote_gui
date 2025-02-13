# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'jog_page.ui'
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
    QPushButton, QSizePolicy, QSpinBox, QVBoxLayout,
    QWidget)
import _icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1070, 587)
        self.verticalLayout_5 = QVBoxLayout(Form)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widget = QWidget(self.frame_2)
        self.widget.setObjectName(u"widget")
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_3 = QLabel(self.widget)
        self.label_3.setObjectName(u"label_3")
        font = QFont()
        font.setPointSize(20)
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label_3)

        self.spinBox = QSpinBox(self.widget)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setMinimumSize(QSize(0, 0))
        self.spinBox.setFont(font)

        self.verticalLayout.addWidget(self.spinBox)


        self.horizontalLayout.addWidget(self.widget)

        self.widget_2 = QWidget(self.frame_2)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout_2 = QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_4 = QLabel(self.widget_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_4)

        self.spinBox_2 = QSpinBox(self.widget_2)
        self.spinBox_2.setObjectName(u"spinBox_2")
        self.spinBox_2.setFont(font)

        self.verticalLayout_2.addWidget(self.spinBox_2)


        self.horizontalLayout.addWidget(self.widget_2)

        self.widget_3 = QWidget(self.frame_2)
        self.widget_3.setObjectName(u"widget_3")
        self.verticalLayout_3 = QVBoxLayout(self.widget_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_5 = QLabel(self.widget_3)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font)
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_5)

        self.spinBox_3 = QSpinBox(self.widget_3)
        self.spinBox_3.setObjectName(u"spinBox_3")
        font1 = QFont()
        font1.setPointSize(20)
        font1.setBold(False)
        self.spinBox_3.setFont(font1)

        self.verticalLayout_3.addWidget(self.spinBox_3)


        self.horizontalLayout.addWidget(self.widget_3)


        self.verticalLayout_4.addWidget(self.frame_2)

        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.ccwButton = QPushButton(self.frame_3)
        self.ccwButton.setObjectName(u"ccwButton")
        self.ccwButton.setMinimumSize(QSize(100, 150))
        self.ccwButton.setStyleSheet(u"")
        self.ccwButton.setIconSize(QSize(100, 100))
        self.ccwButton.setCheckable(False)

        self.horizontalLayout_2.addWidget(self.ccwButton)

        self.sensor_main_led_ind = QLabel(self.frame_3)
        self.sensor_main_led_ind.setObjectName(u"sensor_main_led_ind")
        self.sensor_main_led_ind.setMaximumSize(QSize(200, 200))
        self.sensor_main_led_ind.setPixmap(QPixmap(u":/font_awesome_solid/icons/user/jog_sen_main_off.png"))
        self.sensor_main_led_ind.setScaledContents(False)
        self.sensor_main_led_ind.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_2.addWidget(self.sensor_main_led_ind)

        self.sensor_sub_led_ind = QLabel(self.frame_3)
        self.sensor_sub_led_ind.setObjectName(u"sensor_sub_led_ind")
        self.sensor_sub_led_ind.setMaximumSize(QSize(200, 200))
        self.sensor_sub_led_ind.setPixmap(QPixmap(u":/font_awesome_solid/icons/user/jog_sen_sub_off.png"))
        self.sensor_sub_led_ind.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_2.addWidget(self.sensor_sub_led_ind)

        self.cwButton = QPushButton(self.frame_3)
        self.cwButton.setObjectName(u"cwButton")
        self.cwButton.setMinimumSize(QSize(100, 150))
        self.cwButton.setStyleSheet(u"")
        self.cwButton.setIconSize(QSize(100, 100))

        self.horizontalLayout_2.addWidget(self.cwButton)


        self.verticalLayout_4.addWidget(self.frame_3)


        self.verticalLayout_5.addWidget(self.frame)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"ID", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"SUB ID", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"SPEED(value)", None))
        self.ccwButton.setText("")
        self.sensor_main_led_ind.setText("")
        self.sensor_sub_led_ind.setText("")
        self.cwButton.setText("")
    # retranslateUi


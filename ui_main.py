# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect, QSize, Qt,
                            QTime, QUrl)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
                           QFontDatabase, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette,
                           QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QLabel,
                               QMainWindow, QProgressBar, QSizePolicy, QWidget)

import images


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(421, 396)
        icon = QIcon()
        icon.addFile(u":/newPrefix/scramp_fish.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setDockNestingEnabled(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label_ch_mode = QLabel(self.centralwidget)
        self.label_ch_mode.setObjectName(u"label_ch_mode")
        self.label_ch_mode.setGeometry(QRect(40, 180, 201, 61))
        font = QFont()
        font.setPointSize(16)
        self.label_ch_mode.setFont(font)
        self.radio_rapid_charge = QCheckBox(self.centralwidget)
        self.radio_rapid_charge.setObjectName(u"radio_rapid_charge")
        self.radio_rapid_charge.setGeometry(QRect(250, 190, 141, 31))
        font1 = QFont()
        font1.setPointSize(12)
        self.radio_rapid_charge.setFont(font1)
        self.label_co_mode = QLabel(self.centralwidget)
        self.label_co_mode.setObjectName(u"label_co_mode")
        self.label_co_mode.setGeometry(QRect(40, 300, 131, 61))
        self.label_co_mode.setFont(font)
        self.radio_slow_charge = QCheckBox(self.centralwidget)
        self.radio_slow_charge.setObjectName(u"radio_slow_charge")
        self.radio_slow_charge.setGeometry(QRect(250, 220, 141, 31))
        self.radio_slow_charge.setFont(font1)
        self.progressbar_battery = QProgressBar(self.centralwidget)
        self.progressbar_battery.setObjectName(u"progressbar_battery")
        self.progressbar_battery.setGeometry(QRect(230, 70, 151, 31))
        self.progressbar_battery.setValue(0)
        self.label_current_status = QLabel(self.centralwidget)
        self.label_current_status.setObjectName(u"label_current_status")
        self.label_current_status.setGeometry(QRect(230, 40, 151, 21))
        self.label_current_status.setFont(font1)
        self.label_current_status.setAlignment(Qt.AlignCenter)
        self.label_status = QLabel(self.centralwidget)
        self.label_status.setObjectName(u"label_status")
        self.label_status.setGeometry(QRect(40, 30, 91, 61))
        self.label_status.setFont(font)
        self.label_remaining = QLabel(self.centralwidget)
        self.label_remaining.setObjectName(u"label_remaining")
        self.label_remaining.setGeometry(QRect(210, 110, 191, 20))
        font2 = QFont()
        font2.setPointSize(10)
        self.label_remaining.setFont(font2)
        self.label_remaining.setAlignment(Qt.AlignCenter)
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(20, 20, 381, 131))
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(20, 170, 381, 101))
        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(20, 290, 381, 81))
        self.button_conservation = QCheckBox(self.centralwidget)
        self.button_conservation.setObjectName(u"button_conservation")
        self.button_conservation.setGeometry(QRect(250, 315, 121, 31))
        self.button_conservation.setFont(font1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.groupBox_3.raise_()
        self.groupBox.raise_()
        self.groupBox_2.raise_()
        self.radio_slow_charge.raise_()
        self.label_ch_mode.raise_()
        self.radio_rapid_charge.raise_()
        self.label_co_mode.raise_()
        self.progressbar_battery.raise_()
        self.label_current_status.raise_()
        self.label_status.raise_()
        self.label_remaining.raise_()
        self.button_conservation.raise_()

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Scramp-fish", None))
        self.label_ch_mode.setText(QCoreApplication.translate("MainWindow", u"Charging mode", None))
        self.radio_rapid_charge.setText(QCoreApplication.translate("MainWindow", u"Rapid charge", None))
        self.label_co_mode.setText(QCoreApplication.translate("MainWindow", u"Conservation", None))
        self.radio_slow_charge.setText(QCoreApplication.translate("MainWindow", u"Slow charge", None))
        self.label_current_status.setText(QCoreApplication.translate("MainWindow", u"n/a", None))
        self.label_status.setText(QCoreApplication.translate("MainWindow", u"Status", None))
        self.label_remaining.setText("")
        self.groupBox.setTitle("")
        self.groupBox_2.setTitle("")
        self.groupBox_3.setTitle("")
        self.button_conservation.setText(QCoreApplication.translate("MainWindow", u"De/activation", None))
    # retranslateUi


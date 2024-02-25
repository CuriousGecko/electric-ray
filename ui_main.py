# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QLabel,
    QMainWindow, QProgressBar, QSizePolicy, QWidget)
import images

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(421, 402)
        icon = QIcon()
        icon.addFile(u":/img/icon", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        MainWindow.setDockNestingEnabled(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(20, 180, 381, 101))
        self.radio_rapid_charge = QCheckBox(self.groupBox_2)
        self.radio_rapid_charge.setObjectName(u"radio_rapid_charge")
        self.radio_rapid_charge.setGeometry(QRect(230, 20, 141, 31))
        font = QFont()
        font.setPointSize(12)
        self.radio_rapid_charge.setFont(font)
        self.radio_regular_charge = QCheckBox(self.groupBox_2)
        self.radio_regular_charge.setObjectName(u"radio_regular_charge")
        self.radio_regular_charge.setGeometry(QRect(230, 50, 141, 31))
        self.radio_regular_charge.setFont(font)
        self.label_ch_mode = QLabel(self.groupBox_2)
        self.label_ch_mode.setObjectName(u"label_ch_mode")
        self.label_ch_mode.setGeometry(QRect(20, 10, 151, 61))
        font1 = QFont()
        font1.setPointSize(16)
        self.label_ch_mode.setFont(font1)
        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(20, 300, 381, 81))
        self.label_co_mode = QLabel(self.groupBox_3)
        self.label_co_mode.setObjectName(u"label_co_mode")
        self.label_co_mode.setGeometry(QRect(20, 10, 151, 61))
        self.label_co_mode.setFont(font1)
        self.checkbox_conservation = QCheckBox(self.groupBox_3)
        self.checkbox_conservation.setObjectName(u"checkbox_conservation")
        self.checkbox_conservation.setGeometry(QRect(230, 30, 121, 23))
        self.checkbox_conservation.setFont(font)
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setEnabled(True)
        self.groupBox.setGeometry(QRect(21, 20, 381, 141))
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QSize(0, 0))
        self.groupBox.setSizeIncrement(QSize(0, 0))
        self.groupBox.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_status = QLabel(self.groupBox)
        self.label_status.setObjectName(u"label_status")
        self.label_status.setGeometry(QRect(20, 10, 151, 61))
        self.label_status.setFont(font1)
        self.label_charging_status = QLabel(self.groupBox)
        self.label_charging_status.setObjectName(u"label_charging_status")
        self.label_charging_status.setGeometry(QRect(212, 20, 161, 20))
        self.label_charging_status.setMaximumSize(QSize(16777215, 30))
        self.label_charging_status.setFont(font)
        self.label_charging_status.setAlignment(Qt.AlignCenter)
        self.label_message = QLabel(self.groupBox)
        self.label_message.setObjectName(u"label_message")
        self.label_message.setEnabled(True)
        self.label_message.setGeometry(QRect(210, 80, 159, 51))
        sizePolicy.setHeightForWidth(self.label_message.sizePolicy().hasHeightForWidth())
        self.label_message.setSizePolicy(sizePolicy)
        self.label_message.setMinimumSize(QSize(159, 0))
        self.label_message.setMaximumSize(QSize(0, 60))
        self.label_message.setSizeIncrement(QSize(0, 0))
        self.label_message.setBaseSize(QSize(0, 0))
        font2 = QFont()
        font2.setPointSize(10)
        self.label_message.setFont(font2)
        self.label_message.setLayoutDirection(Qt.LeftToRight)
        self.label_message.setAutoFillBackground(False)
        self.label_message.setTextFormat(Qt.AutoText)
        self.label_message.setScaledContents(True)
        self.label_message.setAlignment(Qt.AlignCenter)
        self.label_message.setWordWrap(True)
        self.label_message.setMargin(0)
        self.label_message.setIndent(-1)
        self.progressbar_battery = QProgressBar(self.groupBox)
        self.progressbar_battery.setObjectName(u"progressbar_battery")
        self.progressbar_battery.setGeometry(QRect(210, 50, 161, 30))
        sizePolicy.setHeightForWidth(self.progressbar_battery.sizePolicy().hasHeightForWidth())
        self.progressbar_battery.setSizePolicy(sizePolicy)
        self.progressbar_battery.setMinimumSize(QSize(0, 0))
        self.progressbar_battery.setMaximumSize(QSize(180, 30))
        self.progressbar_battery.setValue(0)
        MainWindow.setCentralWidget(self.centralwidget)
        self.groupBox_3.raise_()
        self.groupBox_2.raise_()
        self.groupBox.raise_()

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Electric ray", None))
        self.groupBox_2.setTitle("")
        self.radio_rapid_charge.setText(QCoreApplication.translate("MainWindow", u"Rapid charge", None))
        self.radio_regular_charge.setText(QCoreApplication.translate("MainWindow", u"Regular charge", None))
        self.label_ch_mode.setText(QCoreApplication.translate("MainWindow", u"Charging mode", None))
        self.groupBox_3.setTitle("")
        self.label_co_mode.setText(QCoreApplication.translate("MainWindow", u"Conservation", None))
        self.checkbox_conservation.setText(QCoreApplication.translate("MainWindow", u"De/activation", None))
        self.groupBox.setTitle("")
        self.label_status.setText(QCoreApplication.translate("MainWindow", u"Battery status", None))
        self.label_charging_status.setText(QCoreApplication.translate("MainWindow", u"n/a", None))
        self.label_message.setText(QCoreApplication.translate("MainWindow", u". . .", None))
    # retranslateUi


# -*- coding: utf-8 -*-
"""
This module is full of dialog code(Are all based on QDialog)
class:
    SetTimeDialog: Let the user enter the time
    WIFIDialog: Let the user enter SSID and password
    resultDialog: Tell the user about the results after performing the task
    RootDialog: UI interface in brush mode

    myDialog: A simple dialog box example
    MainWindow: Used for debugging dialogs
"""
import sys
import socket
import hashlib
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtCore, QtGui, QtWidgets
from tcp_server import SeverThreadForQT
from lan_ewlink_api import *


class SetTimeDialog(QDialog):
    """
    Let the user enter the time
    You can pass in the parameters in the initialization, the dialog box will be displayed,
    if not set all will be displayed as the default value

    function
        __init__: The UI that depicts the dialog box
              _________________ X
             | ( )ON   ( )OFF   |
             | min：————— |
             | sec：————— |
             | ( )+0.5s ( )0s   |
             --------------------
        rbclicked:
    """

    def __init__(self, parent=None, **reserved_vrg):
        super(SetTimeDialog, self).__init__(parent)
        if "min" in reserved_vrg:
            min = str(reserved_vrg["min"])
            sec = str(reserved_vrg["sec"])
            pulse = reserved_vrg["pulse"]
            sec_sta = reserved_vrg["sec_sta"]
        else:
            min = "59"
            sec = "59"
            sec_sta = True
            pulse = True
        # Sets the title and size of the dialog box
        self.setWindowTitle('Inching Settings')
        self.resize(200, 200)
        # Set the window to modal, and the user can only return to the main
        # interface after closing the popover
        self.setWindowModality(Qt.ApplicationModal)
        # Table layout used to layout QLabel and QLineEdit and QSpinBox
        grid = QGridLayout()
        self.rb01 = QRadioButton('Inching ON', self)
        self.rb02 = QRadioButton('Inching OFF', self)
        self.bg0 = QButtonGroup(self)
        self.bg0.addButton(self.rb01, 11)
        self.bg0.addButton(self.rb02, 12)
        if pulse:
            self.rb01.setChecked(True)
            self.set_sta = True
        else:
            self.rb02.setChecked(True)
            self.set_sta = False

        self.bg0.buttonClicked.connect(self.rbclicked)
        grid.addWidget(self.rb01, 0, 0, 1, 1)
        grid.addWidget(self.rb02, 0, 1, 1, 1)

        grid.addWidget(QLabel(u'mins(number)', parent=self), 1, 0, 1, 1)
        self.minute = QLineEdit(parent=self)
        self.minute.setText(min)
        grid.addWidget(self.minute, 1, 1, 1, 1)
        grid.addWidget(QLabel(u'sces(number)', parent=self), 2, 0, 1, 1)
        self.second = QLineEdit(parent=self)
        self.second.setText(sec)
        grid.addWidget(self.second, 2, 1, 1, 1)

        self.rb11 = QRadioButton('+0.5s', self)
        self.rb12 = QRadioButton('+0s', self)
        self.bg1 = QButtonGroup(self)
        self.bg1.addButton(self.rb11, 21)
        self.bg1.addButton(self.rb12, 22)
        grid.addWidget(self.rb11, 3, 0, 1, 1)
        grid.addWidget(self.rb12, 3, 1, 1, 1)
        if sec_sta:
            self.rb11.setChecked(True)
            self.second_point = True
        else:
            self.rb12.setChecked(True)
            self.second_point = False
        self.bg1.buttonClicked.connect(self.rbclicked)

        grid.addWidget(
            QLabel(
                u'Inching duration range is 0:0.5 ~ 59:59.5\n with the interval of 0.5 sec.',
                parent=self),
            4,
            0,
            2,
            2)
        # Create ButtonBox, and the user confirms and cancels
        buttonbox = QDialogButtonBox(parent=self)
        buttonbox.setOrientation(Qt.Horizontal)  # Set to horizontal
        buttonbox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)  # Ok and cancel two buttons
        # Connect the signal to the slot
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)
        # Vertical layout, layout tables and buttons
        layout = QVBoxLayout()
        # Add the table layout you created earlier
        layout.addLayout(grid)
        # Put a space object to beautify the layout
        spacer_item = QSpacerItem(
            20, 48, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer_item)
        # ButtonBox
        layout.addWidget(buttonbox)
        self.setLayout(layout)

    def rbclicked(self):
        """
        Process radio check boxes
        :return:
        """
        print("sender")
        if self.bg0.checkedId() == 11:
            print("11")
            self.set_sta = True
        elif self.bg0.checkedId() == 12:
            print("12")
            self.set_sta = False
        else:
            # self.info1 = False
            pass
        if self.bg1.checkedId() == 21:
            print("21")
            self.second_point = True
        elif self.bg1.checkedId() == 22:
            print("22")
            self.second_point = False
        else:
            self.second_point = False

    def minute(self):
        """
        View the number of minutes the user entered
        :return:str
        """
        return self.minute.text()

    def second(self):
        """
        View the number of seconds the user entered
        :return: str
        """
        return self.second.text()

    def all_time(self):
        """
        Calculate all times entered by the user
        :return: int (Number of milliseconds)
        """
        input_min = self.minute.text()
        input_sec = self.second.text()
        if (input_sec.isdigit())and(input_min.isdigit()):
            min = int(input_min)
            sec = int(input_sec)
            print(min, sec)
            all_time = min * 60000 + sec * 1000
            if self.second_point:
                all_time += 500
            if not (499 < all_time < 3600000):
                all_time = 0
        else:
            return 0
        return all_time


class WIFIDialog(QDialog):
    """
    Let the user enter the SSID and password for wifi
    """

    def __init__(self, parent=None):
        super(WIFIDialog, self).__init__(parent)
        # Sets the title and size of the dialog box
        self.setWindowTitle('Connect to a new WIFI')
        self.resize(200, 100)
        # Set the window to modal, and the user can only close the main
        # interface after closing the popover
        self.setWindowModality(Qt.ApplicationModal)
        # Table layout used to layout QLabel and QLineEdit and QSpinBox
        grid = QGridLayout()
        grid.addWidget(QLabel(u'SSID', parent=self), 0, 0, 1, 1)
        self.SSIDName = QLineEdit(parent=self)
        self.SSIDName.setText("SSID")
        grid.addWidget(self.SSIDName, 0, 1, 1, 1)
        grid.addWidget(QLabel(u'password', parent=self), 1, 0, 1, 1)
        self.WIFIpassword = QLineEdit(parent=self)
        self.WIFIpassword.setText("password")
        grid.addWidget(self.WIFIpassword, 1, 1, 1, 1)
        grid.addWidget(
            QLabel(
                u'Please enter the SSID and password of the new wifi your device will connect.After connected,\n the '
                u'device will no longer be on this LAN and info in the list will be refreshed in 5 mins.',
                parent=self),
            2,
            0,
            2,
            2)
        # Create ButtonBox, and the user confirms and cancels
        buttonbox = QDialogButtonBox(parent=self)
        buttonbox.setOrientation(Qt.Horizontal)
        buttonbox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)
        # Vertical layout, layout tables and buttons
        layout = QVBoxLayout()
        # Add the table layout you created earlier
        layout.addLayout(grid)
        # Put a space object to beautify the layout
        spacer = QSpacerItem(
            20, 48, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        # ButtonBox
        layout.addWidget(buttonbox)
        self.setLayout(layout)

    def name(self):
        """
        :return: (str)SSID of user input
        """
        return self.SSIDName.text()

    def password(self):
        """
        :return:(str)WIFI password of user input
        """
        return self.WIFIpassword.text()


class resultDialog(QDialog):
    """
    Result dialog box, Used to display the results after execution
    __init__(**info)
            info{id: successful/failure}

    """

    def __init__(self, parent=None, **info):
        super(resultDialog, self).__init__(parent)
        print("后：%s" % str(info["info"]))
        all_info = info["info"]
        self.setWindowTitle('result')
        self.resize(200, 100)
        self.setWindowModality(Qt.ApplicationModal)
        grid = QGridLayout()
        num = 0
        for x in all_info.keys():
            sub_name = QLabel(parent=self)
            sub_name.setText(x)
            grid.addWidget(sub_name, num, 0, 1, 1)
            sub_ret = QLabel(parent=self)
            data = all_info[x]
            if data['error'] == 0:
                sub_ret.setText("succeed")
            else:
                sub_ret.setText("error")
            grid.addWidget(sub_ret, num, 1, 1, 1)
            sub_info = QLabel(parent=self)
            sub_info.setText(str(all_info[x]))
            grid.addWidget(sub_info, num, 2, 2, 1)
            num += 1
        buttonbox = QDialogButtonBox(parent=self)
        buttonbox.setOrientation(Qt.Horizontal)
        buttonbox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)
        layout = QVBoxLayout()
        layout.addLayout(grid)
        spacerItem = QSpacerItem(
            20, 48, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacerItem)
        layout.addWidget(buttonbox)
        self.setLayout(layout)


class myDialog(QDialog):
    """
    An example of a dialog box
    """

    def __init__(self, parent=None):
        super(myDialog, self).__init__(parent)
        # Sets the title and size of the dialog box
        self.setWindowTitle('myDialog')
        self.resize(200, 100)
        # Set the window to modal, and the user can only close the main
        # interface after closing the popover
        self.setWindowModality(Qt.ApplicationModal)
        # Table layout used to layout QLabel and QLineEdit and QSpinBox
        grid = QGridLayout()
        grid.addWidget(QLabel(u'SSID', parent=self), 0, 0, 1, 1)
        self.SSIDName = QLineEdit(parent=self)
        self.SSIDName.setText("wifi")
        grid.addWidget(self.SSIDName, 0, 1, 1, 1)
        grid.addWidget(QLabel(u'password', parent=self), 1, 0, 1, 1)
        self.WIFIpassword = QLineEdit(parent=self)
        self.WIFIpassword.setText("password")
        grid.addWidget(self.WIFIpassword, 1, 1, 1, 1)
        grid.addWidget(QLabel(u'password', parent=self), 2, 0, 2, 2)
        # Create ButtonBox, and the user confirms and cancels
        buttonbox = QDialogButtonBox(parent=self)
        buttonbox.setOrientation(Qt.Horizontal)
        buttonbox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)
        # Vertical layout, layout tables and buttons
        layout = QVBoxLayout()
        # Add the table layout you created earlier
        layout.addLayout(grid)
        # Put a space object to beautify the layout
        spacerItem = QSpacerItem(
            20, 48, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacerItem)
        # ButtonBox
        layout.addWidget(buttonbox)
        self.setLayout(layout)

    def name(self):
        return self.SSIDName.text()

    def password(self):
        return self.WIFIpassword.text()


class RootDialog(QDialog):
    """
    Root main interface window( All device information)
    1.Create server thread(Wait for the device to get the data)
    2.Send the unlock command to the device
    """

    def __init__(self, parent=None, **ccs):
        super(RootDialog, self).__init__(parent)
        self.file_flg = False
        self.dev_flg = False
        print(str(ccs))
        if "b" not in ccs:
            self.all_sub = []
        else:
            self.all_sub = ccs["b"]
        # Sets the title and size of the dialog box
        self.setWindowTitle('Root')
        self.resize(445, 302)
        # Set the window to modal, and the user can only close the main
        # interface after closing the popover
        self.setWindowModality(Qt.ApplicationModal)
        # Table layout used to layout QLabel and QLineEdit and QSpinBox
        self.gridLayoutWidget = QtWidgets.QWidget(self)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 1, 431, 291))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_firmware = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_firmware.setObjectName("lineEdit_firmware")
        self.gridLayout.addWidget(self.lineEdit_firmware, 1, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pB_OK = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pB_OK.setObjectName("pB_OK")
        self.horizontalLayout.addWidget(self.pB_OK)
        self.pB_Cencel = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pB_Cencel.setObjectName("pB_Cencel")
        self.horizontalLayout.addWidget(self.pB_Cencel)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 1, 1, 2)
        self.root_progressBar = QtWidgets.QProgressBar(self.gridLayoutWidget)
        self.root_progressBar.setProperty("value", 0)
        self.root_progressBar.setObjectName("root_progressBar")
        self.gridLayout.addWidget(self.root_progressBar, 6, 1, 1, 2)
        self.pB_import_firmware = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pB_import_firmware.setObjectName("pB_import_firmware")
        self.gridLayout.addWidget(self.pB_import_firmware, 1, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 6, 0, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 4, 1, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.pB_get_device = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pB_get_device.setObjectName("pB_get_device")
        self.gridLayout.addWidget(self.pB_get_device, 2, 2, 1, 1)
        self.cBox_Dev = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.cBox_Dev.setObjectName("cBox_Dev")
        self.gridLayout.addWidget(self.cBox_Dev, 2, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_5.setFont(font)
        self.label_5.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 3)
        self.retranslateUi()
        self.fresh_box()
        # Connect the signal to the slot
        self.cBox_Dev.currentIndexChanged.connect(self.select_port)
        self.pB_get_device.clicked.connect(self.fresh_box)
        self.pB_import_firmware.clicked.connect(self.choose_img)
        self.pB_OK.clicked.connect(self.start_root)
        self.pB_Cencel.clicked.connect(self.reject)

    def retranslateUi(self):
        self.setWindowTitle(QtWidgets.QApplication.translate(
            "Dialog", "DIY Flash Firmware TOOL", None, -1))
        self.pB_OK.setText(
            QtWidgets.QApplication.translate(
                "Dialog", "OK", None, -1))
        self.pB_Cencel.setText(
            QtWidgets.QApplication.translate(
                "Dialog", "Cancel", None, -1))
        self.pB_import_firmware.setText(
            QtWidgets.QApplication.translate(
                "Dialog", "Import firmware", None, -1))
        self.label_3.setText(
            QtWidgets.QApplication.translate(
                "Dialog", " Warning ", None, -1))
        self.label.setText(
            QtWidgets.QApplication.translate(
                "Dialog", "Firmware", None, -1))
        self.label_4.setText(
            QtWidgets.QApplication.translate(
                "Dialog", "Progress", None, -1))
        self.textBrowser.setHtml(
            QtWidgets.QApplication.translate(
                "Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">Flashing firmware will void your warranty.By clicking \'OK\',you accept voiding the warranty on this device. To avoid bricking, do not power off,restart the device,disconnect it from network, restart LAN router, change IP or port on your PC or close this program during installation. </span></p></body></html>", None, -1))
        self.label_2.setText(
            QtWidgets.QApplication.translate(
                "Dialog", "Device", None, -1))
        self.pB_get_device.setText(
            QtWidgets.QApplication.translate(
                "Dialog", "Flash device list", None, -1))
        self.label_5.setText(
            QtWidgets.QApplication.translate(
                "Dialog", "DIY Flash Firmware TOOL", None, -1))

    def fresh_box(self):
        """
        Refresh device options
        :return: None
        """
        self.dev_flg = False
        self.cBox_Dev.clear()
        print(self.all_sub)
        if len(self.all_sub) <= 0:
            QMessageBox.critical(
                "Unable to find device, please exit retry", 10000)
            print("Unable to find device, please exit retry")
        else:
            for x in self.all_sub:
                self.cBox_Dev.addItems([x])

    def check_port(self):
        """
        Test which ports are available[80, 1080, 8888, 6666, 9999]
        :return: (int)Available ports
        """
        port_number = [80, 1080, 8888, 6666, 9999]
        for index in port_number:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', index))
            sock.close()
            if result == 0:
                print("Port %d is open" % index)
            else:
                print("Port %d is not open" % index)
                return index
        return 0

    def choose_img(self):
        """
        Select the firmware
                Select the firmware, copy the user's firmware to the current working directory,
                and calculate the SHA256 value of the file, and verify whether the file is Dout,
                and the firmware size is less than 608k,
                and whether it is a ".bin "file
        :return:
        """
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFilter(QDir.Files)
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            imgfile = filenames[0]
            self.lineEdit_firmware.clear()
            # whether it is a ".bin "file
            if ".bin" not in imgfile:
                QMessageBox.information(
                    self,
                    "ERROR",
                    "The firmware selected is not a bin file",
                    QMessageBox.Yes,
                    QMessageBox.Yes)
                return
            #
            if self.get_file_to_work(imgfile):
                try:
                    with open("itead.bin", 'rb') as file_obj:
                        self.img = file_obj.read()
                        print(type(self.img))
                        print(len(self.img))
                        sha256 = hashlib.sha256(self.img)
                        self.imgsha256 = sha256.hexdigest()
                        print(self.imgsha256)
                        self.lineEdit_firmware.setText(imgfile)
                        self.file_flg = True
                except BaseException:
                    print("unknown err")
            else:
                QMessageBox.information(
                    self,
                    "ERROR",
                    "Firmware file cannot be greater than 608k; The firmware must be Dout",
                    QMessageBox.Yes,
                    QMessageBox.Yes)

    def get_file_to_work(self, bin_file):
        """
        calculate the SHA256 value of the file, and verify whether the file is Dout,
        and the firmware size is less than 608k,
        """
        try:
            with open(bin_file, 'rb') as file_obj:
                b = bytearray(file_obj.read())
                if (b[2] == 3)and(len(b) < 608000):
                    file_obj.seek(0, 0)
                    img = file_obj.read()
                else:
                    return False
        except BaseException:
            print("unknown err")
            return False
        bin_obj = open("itead.bin", 'wb')
        bin_obj.write(img)
        return True

    def select_port(self):
        """
        Confirm the selected user
        :return:
        """
        id = self.cBox_Dev.currentText()
        if len(id) <= 1:
            return
        self.dev_flg = True
        new = "The currently selected device id is" + id
        QMessageBox.information(
            self,
            "tips",
            new,
            QMessageBox.Yes,
            QMessageBox.Yes)
        self.sub_id = [id]

    def start_root(self):
        # Check if conditions are met
        if not self.file_flg:
            QMessageBox.information(
                self,
                "Insufficient conditions",
                "Missing firmware file！",
                QMessageBox.Yes,
                QMessageBox.Yes)
            return
        if not self.dev_flg:
            QMessageBox.information(
                self,
                "Insufficient conditions",
                "No device selected yet！",
                QMessageBox.Yes,
                QMessageBox.Yes)
            return
        # Create a QT thread to transfer firmware to the device
        myport = self.check_port()
        myaddr = self.get_dev_ip_for_lan()
        # print("Host information：",myname,myaddr,str(myport))
        print("Server initialization complete")
        self.control_server_Thread = SeverThreadForQT(
            server_port=myport, server_ip=myaddr)
        # Lock button
        self.pB_get_device.setDisabled(1)
        self.pB_import_firmware.setDisabled(1)
        self.pB_OK.setDisabled(1)
        self.pB_Cencel.setDisabled(1)
        # Send an unlocked device upgrade
        self.send_unlock(self.sub_id, self.imgsha256, myaddr, myport)

    def get_host_ip(self):
        """
        Query the native IP address
        :return: ip
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except BaseException:
            s.close()
            return self.getText()
        finally:
            s.close()
        return ip

    def get_dev_ip_for_lan(self):
        """
        Query the native IP address
        :return: ip
        """
        try:
            myname = socket.getfqdn(socket.gethostname())
            myaddr = socket.gethostbyname_ex(myname)
            print(myaddr)
            all_adds = myaddr[2]
            print("self.all_sub", self.all_sub)
            sub_info = self.all_sub[self.sub_id[0]]
            sub_ip = sub_info["ip"]
            for x in all_adds:
                print(x)
                if x[:10] in sub_ip[:10]:
                    return x
            return all_adds[0]
        except BaseException:
            return self.get_host_ip()

    def send_unlock(self, sub_id, sha256, sever_ip, sever_port):
        """
        Send the unlock command to the device
        :param sub_id: The device ID number to unlock
        :param sha256: The SHA256 value of the firmware
        :param sever_ip: The IP address of the server
        :param sever_port: Server port
        :return:
        """
        print("unlock SUB：", sub_id)
        dicta = {"info": self.all_sub, "select_name_list": sub_id}
        pass
        dicta["command_num"] = 7
        vrg = {}
        command_vrg = {}
        pass
        command_vrg["sha256sum"] = sha256
        command_vrg["sever_ip"] = sever_ip
        command_vrg["sever_port"] = sever_port
        vrg["command_vrg"] = command_vrg
        dicta["command_vrg"] = vrg
        self.myThread = ThreadForQT(parent=None, **dicta)
        self.myThread.run_test_Thread.connect(self.do_unlock_result)
        self.myThread.start()

    def do_unlock_result(self, result_str):
        """
        To understand the return value of the lock instruction
        :param result_str: Unlock the message sent by the thread
        :return:
        """
        if "END" in result_str:
            # self.ui.pushButton.setDisabled(0)
            return
        result_list = result_str.split("\n")
        print("The return value is received：", result_list)
        if result_list[1] is "0":
            # Perform an
            self.control_server_Thread.ota_state_Thread.connect(
                self.updata_ota)
            self.control_server_Thread.start()
        else:
            # Send unlocking failure (prompt for network connection)(close the
            # server)
            QMessageBox.information(
                self,
                "Send unlock failed",
                "Please check your network connection and retry.！",
                QMessageBox.Yes,
                QMessageBox.Yes)

    def getText(self):
        """
        When the IP address cannot be automatically obtained by the user's computer,
        the IP address will be manually entered by the user to create the server
        :return: str The IP address entered by the user
        """
        text, okPressed = QInputDialog.getText(
            self, "not find ip ", "Your PC ip:", QLineEdit.Normal, "")
        if okPressed and text != '':
            print(text)
            return text

    def updata_ota(self, result_new):
        """
        Process information for server threads
        :param result_new: Message from the server thread
        :return:
        """
        result_vrg = result_new.split("\n")
        print(result_vrg)
        result_num = int(result_vrg[2].split(".")[0])
        if "get" in result_vrg:
            self.root_progressBar.setProperty("value", result_num)
        elif "post" in result_vrg:
            print("The return value is received：", str(result_num))
            self.pB_get_device.setDisabled(0)
            self.pB_import_firmware.setDisabled(0)
            self.pB_OK.setDisabled(0)
            self.pB_Cencel.setDisabled(0)
            if result_num == 0:
                # Prompt upgrade successful
                QMessageBox.information(
                    self,
                    "Data sent successfully",
                    "Please wait for the device to restart.\nDo not power off or restart the device manually, \
                    but you may close this window now. ",
                    QMessageBox.Yes,
                    QMessageBox.Yes)
            elif result_num == 1:
                # Prompt upgrade failed
                QMessageBox.information(
                    self,
                    "error",
                    "Please wait for the device to restart！",
                    QMessageBox.Yes,
                    QMessageBox.Yes)
            elif result_num == 404:
                # Prompt upgrade failed
                QMessageBox.information(
                    self,
                    "error",
                    "Data download error 404！",
                    QMessageBox.Yes,
                    QMessageBox.Yes)
            elif result_num == 406:
                # Prompt upgrade failed
                QMessageBox.information(
                    self,
                    "error",
                    "Upgrade failed！",
                    QMessageBox.Yes,
                    QMessageBox.Yes)
            elif result_num == 409:
                # Prompt upgrade failed
                QMessageBox.information(
                    self,
                    "error",
                    "Data verification failed！",
                    QMessageBox.Yes,
                    QMessageBox.Yes)
            elif result_num == 410:
                # Prompt upgrade failed
                QMessageBox.information(
                    self,
                    "error",
                    "Device error！",
                    QMessageBox.Yes,
                    QMessageBox.Yes)
        elif "ERR" in result_vrg:
            self.pB_Cencel.setDisabled(0)
            QMessageBox.information(
                self,
                "!!!!!!!!!!",
                "Please make sure the connection between the device and your PC is working correctly.\
                (Don\'t power off or restart the device, close the upgrade window, or change the IP \
                or port on your PC)！",
                QMessageBox.Yes,
                QMessageBox.Yes)


class MainWindow(QMainWindow):
    """
    Single-module debugging classes
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # Sets the title and size of the main window
        self.setWindowTitle('The main window')
        self.resize(400, 300)
        # Create button
        self.btn = QPushButton(self)
        self.btn.setText('Popup dialog')
        self.btn.move(50, 50)
        self.btn.clicked.connect(self.show_dialog1)

    def show_dialog1(self):
        all_dev = ["First", "second", "third", "more"]
        self.dialog = RootDialog(b=all_dev)
        self.dialog.show()
        ret = self.dialog.exec_()
        print(ret)
        if ret:
            print(self.dialog.name())
            print(self.dialog.password())
        self.dialog.destroy()

    def show_WIFIDialog(self):
        self.dialog = WIFIDialog()
        self.dialog.show()
        ret = self.dialog.exec_()
        print(ret)
        if ret:
            print(self.dialog.name())
            print(self.dialog.password())
        self.dialog.destroy()

    def show_dialog(self):
        self.dialog = SetTimeDialog()
        self.dialog.show()
        ret = self.dialog.exec_()
        print("ret:", ret)
        if ret:
            print(self.dialog.all_time())
        self.dialog.destroy()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec_())

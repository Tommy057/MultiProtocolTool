from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QSpinBox)
from pysnmp.hlapi import *
from PyQt6.QtCore import QThread, pyqtSignal


class SnmpWorker(QThread):
    result_signal = pyqtSignal(str)

    def __init__(self, ip, port, community, oid):
        super().__init__()
        self.ip = ip
        self.port = port
        self.community = community
        self.oid = oid

    def run(self):
        try:
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(SnmpEngine(),
                       CommunityData(self.community, mpModel=1),  # SNMP v2c
                       UdpTransportTarget((self.ip, self.port), timeout=1, retries=1),
                       ContextData(),
                       ObjectType(ObjectIdentity(self.oid)))
            )

            if errorIndication:
                self.result_signal.emit(f"Error: {errorIndication}")
            elif errorStatus:
                self.result_signal.emit(f"Error Status: {errorStatus.prettyPrint()}")
            else:
                for varBind in varBinds:
                    self.result_signal.emit(f"{varBind[0]} = {varBind[1]}")
        except Exception as e:
            self.result_signal.emit(f"Exception: {str(e)}")


class SnmpTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        cfg_layout = QHBoxLayout()
        self.ip_input = QLineEdit("127.0.0.1")
        self.port_input = QSpinBox()
        self.port_input.setValue(161)
        self.community_input = QLineEdit("public")
        self.oid_input = QLineEdit("1.3.6.1.2.1.1.1.0")  # SysDescr

        btn_get = QPushButton("Get OID")
        btn_get.clicked.connect(self.get_oid)

        cfg_layout.addWidget(QLabel("IP:"))
        cfg_layout.addWidget(self.ip_input)
        cfg_layout.addWidget(QLabel("Port:"))
        cfg_layout.addWidget(self.port_input)
        cfg_layout.addWidget(QLabel("Community:"))
        cfg_layout.addWidget(self.community_input)
        layout.addLayout(cfg_layout)

        oid_layout = QHBoxLayout()
        oid_layout.addWidget(QLabel("OID:"))
        oid_layout.addWidget(self.oid_input)
        oid_layout.addWidget(btn_get)
        layout.addLayout(oid_layout)

        self.log_area = QTextEdit()
        layout.addWidget(self.log_area)
        self.setLayout(layout)

    def get_oid(self):
        ip = self.ip_input.text()
        port = self.port_input.value()
        comm = self.community_input.text()
        oid = self.oid_input.text()

        self.log_area.append(f"Requesting {oid} from {ip}...")
        self.worker = SnmpWorker(ip, port, comm, oid)
        self.worker.result_signal.connect(self.log_area.append)
        self.worker.start()
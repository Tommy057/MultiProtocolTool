from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QSpinBox, QCheckBox)
from PyQt6.QtCore import QTimer, QDateTime
from pymodbus.client import ModbusTcpClient
import threading


class ModbusTab(QWidget):
    def __init__(self):
        super().__init__()
        self.client = None
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.read_registers)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 配置区
        config_layout = QHBoxLayout()
        self.ip_input = QLineEdit("127.0.0.1")
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(502)

        self.btn_connect = QPushButton("连接")
        self.btn_connect.clicked.connect(self.toggle_connect)

        config_layout.addWidget(QLabel("IP:"))
        config_layout.addWidget(self.ip_input)
        config_layout.addWidget(QLabel("Port:"))
        config_layout.addWidget(self.port_input)
        config_layout.addWidget(self.btn_connect)
        layout.addLayout(config_layout)

        # 操作区
        op_layout = QHBoxLayout()
        self.start_addr = QSpinBox()
        self.start_addr.setRange(0, 65535)
        self.count_input = QSpinBox()
        self.count_input.setValue(10)

        btn_read = QPushButton("读取保持寄存器")
        btn_read.clicked.connect(self.read_registers)

        self.write_val = QSpinBox()
        btn_write = QPushButton("写入单个寄存器")
        btn_write.clicked.connect(self.write_register)

        op_layout.addWidget(QLabel("起始地址:"))
        op_layout.addWidget(self.start_addr)
        op_layout.addWidget(QLabel("数量:"))
        op_layout.addWidget(self.count_input)
        op_layout.addWidget(btn_read)
        op_layout.addWidget(QLabel("值:"))
        op_layout.addWidget(self.write_val)
        op_layout.addWidget(btn_write)
        layout.addLayout(op_layout)

        # 轮询控制
        poll_layout = QHBoxLayout()
        self.chk_poll = QCheckBox("启用轮询 (1000ms)")
        self.chk_poll.stateChanged.connect(self.toggle_poll)
        poll_layout.addWidget(self.chk_poll)
        layout.addLayout(poll_layout)

        # 日志区
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(QLabel("日志:"))
        layout.addWidget(self.log_area)

        self.setLayout(layout)

    def log(self, message):
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")
        self.log_area.append(f"[{timestamp}] {message}")

    def toggle_connect(self):
        if self.client and self.client.connected:
            self.client.close()
            self.btn_connect.setText("连接")
            self.log("断开连接")
        else:
            ip = self.ip_input.text()
            port = self.port_input.value()
            try:
                self.client = ModbusTcpClient(ip, port=port)
                if self.client.connect():
                    self.btn_connect.setText("断开")
                    self.log(f"已连接到 {ip}:{port}")
                else:
                    self.log("连接失败")
            except Exception as e:
                self.log(f"连接异常: {str(e)}")

    def read_registers(self):
        if not self.client or not self.client.connected:
            self.log("未连接")
            return

        try:
            addr = self.start_addr.value()
            count = self.count_input.value()
            rr = self.client.read_holding_registers(addr, count)
            if not rr.isError():
                self.log(f"Read Addr {addr}: {rr.registers}")
            else:
                self.log(f"Read Error: {rr}")
        except Exception as e:
            self.log(f"读取异常: {str(e)}")

    def write_register(self):
        if not self.client or not self.client.connected: return
        try:
            addr = self.start_addr.value()
            val = self.write_val.value()
            wr = self.client.write_register(addr, val)
            if not wr.isError():
                self.log(f"Write Addr {addr} = {val} Success")
            else:
                self.log(f"Write Error: {wr}")
        except Exception as e:
            self.log(f"写入异常: {str(e)}")

    def toggle_poll(self, state):
        if state == 2:  # Checked
            self.poll_timer.start(1000)
        else:
            self.poll_timer.stop()
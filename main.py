import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from tabs.modbus_tab import ModbusTab
from tabs.network_tab import NetworkTab
from tabs.http_tab import HttpTab
from tabs.mqtt_tab import MqttTab
from tabs.snmp_tab import SnmpTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多协议综合调测工具 (PyQt6)")
        self.resize(900, 700)

        # 主容器
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 选项卡控件
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # 添加各个协议的 Tab
        self.add_tabs()

    def add_tabs(self):
        self.tabs.addTab(ModbusTab(), "Modbus TCP")
        self.tabs.addTab(NetworkTab(), "TCP/UDP")
        self.tabs.addTab(HttpTab(), "HTTP")
        self.tabs.addTab(MqttTab(), "MQTT")
        self.tabs.addTab(SnmpTab(), "SNMP")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
import socket
import threading
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QComboBox, QSpinBox)
from PyQt6.QtCore import pyqtSignal, QObject, QDateTime


class NetworkWorker(QObject):
    msg_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.sock = None


class NetworkTab(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.listen_thread = None
        self.client_sock = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 配置
        top_layout = QHBoxLayout()
        self.proto_combo = QComboBox()
        self.proto_combo.addItems(["TCP Client", "TCP Server", "UDP"])

        self.ip_input = QLineEdit("127.0.0.1")
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(8080)

        self.btn_start = QPushButton("开始/连接")
        self.btn_start.clicked.connect(self.toggle_network)

        top_layout.addWidget(QLabel("模式:"))
        top_layout.addWidget(self.proto_combo)
        top_layout.addWidget(QLabel("IP:"))
        top_layout.addWidget(self.ip_input)
        top_layout.addWidget(QLabel("Port:"))
        top_layout.addWidget(self.port_input)
        top_layout.addWidget(self.btn_start)
        layout.addLayout(top_layout)

        # 发送区
        send_layout = QHBoxLayout()
        self.msg_input = QLineEdit("Hello World")
        self.btn_send = QPushButton("发送")
        self.btn_send.clicked.connect(self.send_data)
        send_layout.addWidget(self.msg_input)
        send_layout.addWidget(self.btn_send)
        layout.addLayout(send_layout)

        # 日志
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        self.setLayout(layout)

    def log(self, msg):
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.log_area.append(f"[{timestamp}] {msg}")

    def toggle_network(self):
        if self.worker:  # 停止
            self.worker.running = False
            if self.worker.sock:
                try:
                    self.worker.sock.close()
                except:
                    pass
            self.worker = None
            self.btn_start.setText("开始/连接")
            self.log("停止网络服务")
            return

        mode = self.proto_combo.currentText()
        ip = self.ip_input.text()
        port = self.port_input.value()

        self.worker = NetworkWorker()
        self.worker.msg_signal.connect(self.log)

        if mode == "TCP Server":
            self.listen_thread = threading.Thread(target=self.run_tcp_server, args=(ip, port))
            self.listen_thread.daemon = True
            self.listen_thread.start()
            self.btn_start.setText("停止")
        elif mode == "TCP Client":
            self.run_tcp_client(ip, port)
        elif mode == "UDP":
            self.run_udp(ip, port)

    def run_tcp_server(self, ip, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((ip, port))
            s.listen(1)
            self.worker.sock = s
            self.worker.msg_signal.emit(f"TCP Server 监听 {ip}:{port}")

            while self.worker.running:
                try:
                    conn, addr = s.accept()
                    self.worker.msg_signal.emit(f"客户端连接: {addr}")
                    while self.worker.running:
                        data = conn.recv(1024)
                        if not data: break
                        self.worker.msg_signal.emit(f"收到: {data.decode('utf-8', 'ignore')}")
                    conn.close()
                except OSError:
                    break
        except Exception as e:
            self.worker.msg_signal.emit(f"Server Error: {e}")

    def run_tcp_client(self, ip, port):
        try:
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_sock.connect((ip, port))
            self.worker.sock = self.client_sock
            self.log(f"连接到 TCP Server {ip}:{port}")
            self.btn_start.setText("断开")

            # 开启接收线程
            def recv_loop():
                while self.worker and self.worker.running:
                    try:
                        data = self.client_sock.recv(1024)
                        if not data: break
                        self.worker.msg_signal.emit(f"收到: {data.decode('utf-8', 'ignore')}")
                    except:
                        break

            t = threading.Thread(target=recv_loop, daemon=True)
            t.start()

        except Exception as e:
            self.log(f"连接失败: {e}")
            self.worker = None

    def run_udp(self, ip, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind((ip, port))
            self.worker.sock = s
            self.log(f"UDP 绑定 {ip}:{port}")
            self.btn_start.setText("停止")

            def recv_udp():
                while self.worker and self.worker.running:
                    try:
                        data, addr = s.recvfrom(1024)
                        self.worker.msg_signal.emit(f"来自 {addr}: {data.decode('utf-8', 'ignore')}")
                    except OSError:
                        break

            t = threading.Thread(target=recv_udp, daemon=True)
            t.start()
        except Exception as e:
            self.log(f"UDP Error: {e}")
            self.worker = None

    def send_data(self):
        msg = self.msg_input.text().encode('utf-8')
        mode = self.proto_combo.currentText()
        try:
            if mode == "TCP Client" and self.client_sock:
                self.client_sock.send(msg)
                self.log(f"发送: {msg.decode()}")
            elif mode == "UDP" and self.worker and self.worker.sock:
                # UDP需要目标地址，这里简化为发给本机测试，实际应增加目标IP框
                target_ip = self.ip_input.text()  # 这里复用IP框作为目标
                target_port = self.port_input.value()
                # 如果是作为服务端监听，这里发送通常需要指定目标
                # 简化：UDP模式下发送给输入框的地址
                self.worker.sock.sendto(msg, (target_ip, target_port))
                self.log(f"UDP发送至 {target_ip}:{target_port} -> {msg.decode()}")
        except Exception as e:
            self.log(f"发送失败: {e}")
import requests
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QComboBox, QPlainTextEdit)
from PyQt6.QtCore import QThread, pyqtSignal


class RequestThread(QThread):
    result_signal = pyqtSignal(str)

    def __init__(self, method, url, headers, body):
        super().__init__()
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body

    def run(self):
        try:
            if self.method == "GET":
                resp = requests.get(self.url, headers=self.headers, timeout=5)
            else:
                resp = requests.post(self.url, headers=self.headers, data=self.body, timeout=5)

            output = f"Status: {resp.status_code}\nHeaders: {resp.headers}\n\nBody:\n{resp.text}"
            self.result_signal.emit(output)
        except Exception as e:
            self.result_signal.emit(f"Error: {str(e)}")


class HttpTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        url_layout = QHBoxLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST"])
        self.url_input = QLineEdit("http://httpbin.org/get")
        self.btn_send = QPushButton("发送请求")
        self.btn_send.clicked.connect(self.send_request)

        url_layout.addWidget(self.method_combo)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.btn_send)
        layout.addLayout(url_layout)

        layout.addWidget(QLabel("Body (JSON/Text for POST):"))
        self.body_input = QPlainTextEdit()
        self.body_input.setMaximumHeight(100)
        layout.addWidget(self.body_input)

        layout.addWidget(QLabel("响应:"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        self.setLayout(layout)

    def send_request(self):
        method = self.method_combo.currentText()
        url = self.url_input.text()
        body = self.body_input.toPlainText()
        headers = {'User-Agent': 'PyQt-Tool'}

        # 简单判断如果body是json格式
        if method == "POST":
            try:
                json.loads(body)
                headers['Content-Type'] = 'application/json'
            except:
                pass  # Treat as text

        self.log_area.setText("请求中...")
        self.thread = RequestThread(method, url, headers, body)
        self.thread.result_signal.connect(self.log_area.setText)
        self.thread.start()
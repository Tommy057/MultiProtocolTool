import paho.mqtt.client as mqtt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QSpinBox)
from PyQt6.QtCore import pyqtSignal, QObject, QDateTime


class MqttWorker(QObject):
    log_signal = pyqtSignal(str)


class MqttTab(QWidget):
    def __init__(self):
        super().__init__()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.worker = MqttWorker()
        self.worker.log_signal.connect(self.log)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 连接配置
        conn_layout = QHBoxLayout()
        self.broker_input = QLineEdit("broker.emqx.io")
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(1883)
        self.btn_connect = QPushButton("连接")
        self.btn_connect.clicked.connect(self.toggle_connect)

        conn_layout.addWidget(QLabel("Broker:"))
        conn_layout.addWidget(self.broker_input)
        conn_layout.addWidget(QLabel("Port:"))
        conn_layout.addWidget(self.port_input)
        conn_layout.addWidget(self.btn_connect)
        layout.addLayout(conn_layout)

        # 订阅/发布
        sub_layout = QHBoxLayout()
        self.topic_input = QLineEdit("test/topic")
        self.msg_input = QLineEdit("Hello MQTT")
        btn_sub = QPushButton("订阅")
        btn_sub.clicked.connect(self.subscribe)
        btn_pub = QPushButton("发布")
        btn_pub.clicked.connect(self.publish)

        sub_layout.addWidget(QLabel("Topic:"))
        sub_layout.addWidget(self.topic_input)
        sub_layout.addWidget(btn_sub)
        sub_layout.addWidget(QLabel("Msg:"))
        sub_layout.addWidget(self.msg_input)
        sub_layout.addWidget(btn_pub)
        layout.addLayout(sub_layout)

        self.log_area = QTextEdit()
        layout.addWidget(self.log_area)
        self.setLayout(layout)

    def log(self, msg):
        ts = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.log_area.append(f"[{ts}] {msg}")

    def on_connect(self, client, userdata, flags, rc):
        status = "成功" if rc == 0 else f"失败 Code: {rc}"
        self.worker.log_signal.emit(f"连接 {status}")

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
        except:
            payload = str(msg.payload)
        self.worker.log_signal.emit(f"收到 [{msg.topic}]: {payload}")

    def toggle_connect(self):
        if self.client.is_connected():
            self.client.loop_stop()
            self.client.disconnect()
            self.btn_connect.setText("连接")
        else:
            try:
                self.client.connect(self.broker_input.text(), self.port_input.value(), 60)
                self.client.loop_start()
                self.btn_connect.setText("断开")
            except Exception as e:
                self.log(f"连接异常: {e}")

    def subscribe(self):
        topic = self.topic_input.text()
        self.client.subscribe(topic)
        self.log(f"已订阅: {topic}")

    def publish(self):
        topic = self.topic_input.text()
        payload = self.msg_input.text()
        self.client.publish(topic, payload)
        self.log(f"已发布至 {topic}: {payload}")
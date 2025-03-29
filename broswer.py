import sys, os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea, QGridLayout, QToolBar,
    QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QStackedWidget,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import pyqtSignal, QUrl

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

class SoftKeyboard(QWidget):
    keyPressed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QGridLayout()
        keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['-', '_', '.', '/', '\\', ':', ';', '@', '删除', '确定']
        ]

        for row_idx, row in enumerate(keys):
            for col_idx, key in enumerate(row):
                btn = QPushButton(key)
                btn.setFixedSize(40, 40)
                btn.clicked.connect(lambda _, k=key: self.key_pressed(k))
                layout.addWidget(btn, row_idx, col_idx)

        self.setLayout(layout)

    def key_pressed(self, key):
        if key == '删除':
            self.keyPressed.emit('\b')
        elif key == '确定':
            self.keyPressed.emit('\n')
        else:
            self.keyPressed.emit(key)

class AddressPage(QWidget):
    submit = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setFixedSize(560, 170)

        # 顶部栏
        top_layout = QHBoxLayout()
        self.address_bar = QLineEdit()
        self.go_button = QPushButton("访问")
        self.address_bar.setText("example.com")
        top_layout.addWidget(self.address_bar)
        top_layout.addWidget(self.go_button)

        # 软键盘
        scroll = QScrollArea()
        self.keyboard = SoftKeyboard()
        scroll.setWidget(self.keyboard)
        scroll.setWidgetResizable(True)

        layout.addLayout(top_layout)
        layout.addWidget(scroll)
        self.setLayout(layout)

        # 信号连接
        self.go_button.clicked.connect(self.submit_address)
        self.keyboard.keyPressed.connect(self.handle_key)

    def submit_address(self):
        url = self.address_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        self.submit.emit(url)

    def handle_key(self, key):
        if key == '\b':
            self.address_bar.backspace()
        elif key == '\n':
            self.submit_address()
        else:
            self.address_bar.insert(key)

class BrowserPage(QWidget):
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # 工具栏
        toolbar = QToolBar()
        self.back_btn = QPushButton("返回")
        self.nav_back_btn = QPushButton("网页回退")

        toolbar.addWidget(self.back_btn)
        toolbar.addWidget(self.nav_back_btn)

        # 浏览器组件
        self.browser = QWebEngineView()

        layout.addWidget(toolbar)
        layout.addWidget(self.browser)
        self.setLayout(layout)

        # 信号连接
        self.back_btn.clicked.connect(self.back_requested)
        self.nav_back_btn.clicked.connect(self.browser.back)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("旋转浏览器")
        self.setFixedSize(170, 560)

        # 创建页面
        self.address_page = AddressPage()
        self.browser_page = BrowserPage()

        # 设置堆叠窗口
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.address_page)
        self.stacked_widget.addWidget(self.browser_page)

        # 设置图形视图
        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.proxy = QGraphicsProxyWidget()

        self.graphics_view.setFixedSize(self.size())

        self.proxy.setWidget(self.stacked_widget)
        self.proxy.setRotation(-90)
        self.proxy.setTransformOriginPoint(self.proxy.boundingRect().center())

        self.scene.addItem(self.proxy)
        self.graphics_view.setScene(self.scene)
        self.setCentralWidget(self.graphics_view)

        # 信号连接
        self.address_page.submit.connect(self.show_browser)
        self.browser_page.back_requested.connect(self.show_address)

        # 初始化显示地址页面
        self.show_address()

    def show_browser(self, url):
        self.browser_page.browser.setUrl(QUrl(url))
        self.stacked_widget.setCurrentWidget(self.browser_page)

    def show_address(self):
        self.stacked_widget.setCurrentWidget(self.address_page)
        self.address_page.address_bar.setFocus()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec())
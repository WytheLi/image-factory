import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QAction, QFileDialog, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt


class ImageViewer(QMainWindow):
    """
    图片浏览器 - 330x330版本
    带标题描述的图片查看器
    """

    def __init__(self, width=330, height=330):
        super().__init__()

        self.width = width
        self.height = height

        # 设置窗口标题
        self.setWindowTitle("图片浏览器 - 330x330")

        # 创建中央部件和布局
        central_widget = QWidget()
        central_widget.setContentsMargins(0, 0, 0, 0)   # 无内边距
        self.setCentralWidget(central_widget)

        # 使用垂直布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # 设置组件内边距为0
        layout.setSpacing(0)  # 设置组件间距

        # 创建状态描述标签
        self.status_label = QLabel("请选择一张图片")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 9))
        layout.addWidget(self.status_label)

        # 创建固定尺寸的图片显示区域
        self.image_label = QLabel()
        self.image_label.setFixedSize(width, height)  # 固定为330x330大小
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #f0f0f0;
            border: 2px dashed #cccccc;
            border-radius: 5px;
        """)
        layout.addWidget(self.image_label)

        # 创建菜单栏
        self.create_menu()

        # 调整窗口大小以刚好容纳图片区域（加上菜单栏高度）
        menu_height = self.menuBar().sizeHint().height()
        self.setFixedSize(width, height + menu_height)

        # 初始状态
        self.current_image = None

    def create_menu(self):
        # 文件菜单
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")

        # 打开动作
        open_action = QAction("打开图片", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_image(self):
        # 打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        # 更新状态标签
        self.status_label.setText(f"正在加载: {file_path.split('/')[-1]}")

        # 加载图片
        image = QImage(file_path)

        if not image.isNull():
            # 缩放图片以适应固定尺寸的显示区域
            pixmap = QPixmap.fromImage(image)

            # 保持宽高比缩放
            scaled_pixmap = pixmap.scaled(
                self.width, self.height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.image_label.setPixmap(scaled_pixmap)
            self.status_label.setText(f"已加载: {file_path.split('/')[-1]}")
        else:
            # 清空图片并显示错误信息
            self.image_label.clear()
            self.status_label.setText("无法加载图片")
            self.image_label.setText("图片加载失败")
            self.image_label.setStyleSheet("""
                background-color: #f0f0f0;
                border: 2px dashed #ff0000;
                color: red;
                font: bold 12px;
            """)


if __name__ == "__main__":
    # 确保高DPI屏幕适配
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())

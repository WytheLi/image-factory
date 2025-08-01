import cv2
import numpy as np
import pyautogui
import time
from PIL import ImageGrab


class VisionAutoClicker:
    def __init__(self, match_threshold=0.8, click_delay=0.5):
        """
        视觉自动化点击器
        :param match_threshold: 默认图像匹配阈值 (0-1)
        :param click_delay: 默认点击前延迟(秒)
        """
        self.match_threshold = match_threshold
        self.click_delay = click_delay
        self.last_detected_position = None  # 最后检测到的位置缓存

    def capture_screen(self):
        """捕获当前屏幕并转换为OpenCV格式"""
        screenshot = ImageGrab.grab()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def locate_image(self, template_path, threshold=None):
        """
        在屏幕上定位目标图像
        :param template_path: 模板图片路径
        :param threshold: 匹配阈值 (0-1)，默认使用初始化值
        :return: 匹配区域的中心坐标 (x, y)，未找到返回None
        """
        # 使用类默认阈值
        if threshold is None:
            threshold = self.match_threshold

        # 读取模板图像
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            raise FileNotFoundError(f"模板图片未找到: {template_path}")

        # 获取屏幕截图
        screen = self.capture_screen()

        # 模板匹配
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 检查匹配结果
        if max_val < threshold:
            self.last_detected_position = None
            return None

        # 计算中心坐标
        height, width = template.shape[:2]
        top_left = max_loc
        center_x = top_left[0] + width // 2
        center_y = top_left[1] + height // 2

        self.last_detected_position = (center_x, center_y)
        return center_x, center_y

    def click_target_image(self, template_path=None, threshold=None, delay=None, position=None):
        """
        点击屏幕上的目标
        :param template_path: 模板图片路径 (与position二选一)
        :param threshold: 匹配阈值
        :param delay: 点击前延迟(秒)
        :param position: 直接指定点击位置 (x, y)
        :return: 成功点击返回True，否则False
        """
        # 设置延迟
        wait_time = delay if delay is not None else self.click_delay

        # 直接点击模式
        if position is not None:
            time.sleep(wait_time)
            pyautogui.click(position[0], position[1])
            print(f"点击指定位置: {position}")
            return True

        # 模板匹配模式
        if template_path is None:
            raise ValueError("必须提供template_path或position参数")

        target_position = self.locate_image(template_path, threshold)

        if target_position:
            print(f"定位到目标，坐标: {target_position}")
            time.sleep(wait_time)
            pyautogui.click(target_position[0], target_position[1])
            print("点击操作完成")
            return True

        print("未找到目标图像")
        return False

    def repeat_last_click(self, delay=None):
        """重复点击上一次定位到的位置"""
        if self.last_detected_position is None:
            print("没有可用的位置缓存")
            return False
        return self.click_target_image(position=self.last_detected_position, delay=delay)


if __name__ == "__main__":
    # 初始化点击器
    automator = VisionAutoClicker(match_threshold=0.85, click_delay=1.0)

    # 通过图像定位并点击
    automator.click_target_image("submit_button.png")

    # 直接点击指定坐标
    automator.click_target_image(position=(150, 250))

    # 重复上次点击
    automator.repeat_last_click()

    # 自定义参数点击
    automator.click_target_image("special_icon.png", threshold=0.9, delay=2.0)
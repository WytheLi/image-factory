import argparse
import time

from config import config
from utils.clicker import VisionAutoClicker
from utils.image_analyzer import ImageAnalyzer
from utils.image_processing import NineGridSplitter


def main():
    parser = argparse.ArgumentParser(description='图片验证工具')
    parser.add_argument('--image', required=True, help='9宫格图片')
    parser.add_argument('--question', required=True, help='验证问题')
    parser.add_argument('--scale', default=1.0, help='图片缩放比例')    # 原图和弹窗显示图片缩放比例

    args = parser.parse_args()

    # 分割图片
    splitter = NineGridSplitter(
        image_path=args.image,  # 替换为你的图片路径
        output_folder="split_pictures",  # 输出文件夹
        grid_size=3  # 3×3九宫格
    )
    splitter.split()

    # 大模型对图片进行分析
    analyzer = ImageAnalyzer(config.DASHSCOPE_API_KEY)
    for i in range(1, 10):
        row = (i - 1) // 3
        col = (i - 1) % 3
        analyzer.analyze_image(f"split_pictures/grid_{row}{col}.jpg")

    result = analyzer.analyze_descriptions(args.question)
    print(f"分析结果：{result}")

    time.sleep(3)
    for n in result.split(","):
        # 初始化点击器
        automator = VisionAutoClicker(match_threshold=0.85, click_delay=1.0)

        # 通过图像定位并点击
        if n.isdigit() and int(n) > 0:
            n = int(n)
            row = (n - 1) // 3
            col = (n -1 ) % 3
            automator.click_target_image(f"split_pictures/grid_{row}{col}.jpg")


if __name__ == "__main__":
    main()

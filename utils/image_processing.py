import base64
import io
import os

from PIL import Image

from config import config


def image_to_base64(image_path, max_size=1024):
    """
    将图片转换为Base64编码字符串，并自动调整大小

    :param image_path: 图片路径
    :param max_size: 最大尺寸（长宽中较大的一边）
    :return: Base64编码的字符串
    """
    # 打开图片并调整大小
    img = Image.open(image_path)

    # 计算调整比例
    width, height = img.size
    if max(width, height) > max_size:
        ratio = max_size / max(width, height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)

    # 转换为Base64
    buffered = io.BytesIO()
    img_format = "JPEG" if image_path.lower().endswith('.jpg') else "PNG"
    img.save(buffered, format=img_format)
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return f"data:image/{img_format.lower()};base64,{img_base64}"


class NineGridSplitter:
    """
    九宫格图片分割工具类

    功能：
    1. 将图片分割成3×3的九宫格
    2. 提供预览图生成功能
    3. 支持重新组合验证分割结果

    示例用法：
        splitter = NineGridSplitter("input.jpg", "output_folder")
        splitter.split()  # 分割图片
        splitter.create_preview()  # 创建预览图
        splitter.recombine()  # 重新组合验证
    """

    def __init__(self, image_path, output_folder="output_grids", grid_size=3):
        """
        初始化分割器

        :param image_path: 输入图片路径xz
        :param output_folder: 输出文件夹路径
        :param grid_size: 网格尺寸 (默认3×3)
        """
        self.image_path = image_path
        self.output_folder = output_folder
        self.grid_size = grid_size

        # 打开原始图片
        self.original_img = Image.open(image_path)
        self.width, self.height = self.original_img.size

        # 计算单元格尺寸
        self.cell_width = self.width // self.grid_size
        self.cell_height = self.height // self.grid_size

        # 确保尺寸能被整除
        self.width = self.cell_width * self.grid_size
        self.height = self.cell_height * self.grid_size

        # 调整图片尺寸
        if self.original_img.size != (self.width, self.height):
            self.original_img = self.original_img.resize((self.width, self.height))
            print(f"图片已调整为 {self.width}x{self.height} 像素")

        # 创建输出文件夹
        os.makedirs(self.output_folder, exist_ok=True)

        # 存储分割后的单元格
        self.grid_cells = []

    def split(self, save_individual=True):
        """
        分割图片为九宫格

        :param save_individual: 是否保存单独的单元格图片
        :return: 单元格列表
        """
        self.grid_cells = []

        for row in range(self.grid_size):
            row_cells = []
            for col in range(self.grid_size):
                # 计算边界
                left = col * self.cell_width
                upper = row * self.cell_height
                right = left + self.cell_width
                lower = upper + self.cell_height

                # 裁剪单元格
                cell = self.original_img.crop((left, upper, right, lower))
                row_cells.append(cell)

                # 保存单独的单元格图片
                if save_individual:
                    filename = os.path.join(self.output_folder, f"grid_{row}{col}.jpg")
                    cell.save(filename)

            self.grid_cells.append(row_cells)

        print(f"图片已成功分割为 {self.grid_size}x{self.grid_size} 的网格")
        return self.grid_cells

    def create_preview(self, line_color=(0, 0, 0), line_width=2, background=(220, 220, 220)):
        """
        创建九宫格预览图（带网格线）

        :param line_color: 网格线颜色 (RGB)
        :param line_width: 网格线宽度 (像素)
        :param background: 背景颜色 (RGB)
        :return: 预览图路径
        """
        # 创建稍大的画布用于显示网格线
        preview_width = self.width + (self.grid_size + 1) * line_width
        preview_height = self.height + (self.grid_size + 1) * line_width
        preview = Image.new('RGB', (preview_width, preview_height), color=background)

        # 粘贴原始图片
        preview.paste(self.original_img, (line_width, line_width))

        # 绘制网格线
        for i in range(1, self.grid_size):
            # 垂直线
            x_pos = line_width + i * self.cell_width + (i - 1) * line_width
            preview.paste(
                line_color,
                (x_pos, line_width, x_pos + line_width, line_width + self.height)
            )

            # 水平线
            y_pos = line_width + i * self.cell_height + (i - 1) * line_width
            preview.paste(
                line_color,
                (line_width, y_pos, line_width + self.width, y_pos + line_width)
            )

        # 保存预览图
        preview_path = os.path.join(self.output_folder, "9grid_preview.jpg")
        preview.save(preview_path)
        print(f"九宫格预览图已保存至: {preview_path}")
        return preview_path

    def recombine(self, output_name="recombined_image.jpg"):
        """
        将分割后的图片重新组合成一张大图

        :param output_name: 输出文件名
        :return: 重组后的图片路径
        """
        # 确保已经分割过图片
        if not self.grid_cells:
            self.split(save_individual=False)

        # 创建空白画布
        recombined = Image.new('RGB', (self.width, self.height))

        # 按顺序组合图片
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = self.grid_cells[row][col]
                recombined.paste(cell, (col * self.cell_width, row * self.cell_height))

        # 保存重组图
        recombined_path = os.path.join(self.output_folder, output_name)
        recombined.save(recombined_path)

        print(f"重组后的图片已保存至: {recombined_path}")
        return recombined_path

    def get_grid_cell(self, row, col):
        """
        获取指定位置的单元格图片

        :param row: 行索引 (0-based)
        :param col: 列索引 (0-based)
        :return: PIL Image 对象
        """
        if not self.grid_cells:
            self.split(save_individual=False)

        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return self.grid_cells[row][col]
        else:
            raise IndexError("无效的行列索引")

    def save_grid_cell(self, row, col, filename=None):
        """
        保存指定位置的单元格图片

        :param row: 行索引
        :param col: 列索引
        :param filename: 自定义文件名 (默认 grid_rowcol.jpg)
        """
        cell = self.get_grid_cell(row, col)
        if not filename:
            filename = f"grid_{row}{col}.jpg"
        filepath = os.path.join(self.output_folder, filename)
        cell.save(filepath)
        print(f"单元格 ({row}, {col}) 已保存至: {filepath}")
        return filepath


if __name__ == "__main__":
    image_path = os.path.join(config.BASE_PATH, "resources/img/material/2_哪些事物或者动物能在公园里看到.png")

    splitter = NineGridSplitter(
        image_path=image_path,  # 替换为你的图片路径
        output_folder="9grid_output",  # 输出文件夹
        grid_size=3  # 3×3九宫格
    )

    # 分割图片
    splitter.split()

    # 创建预览图
    splitter.create_preview(
        line_color=(255, 0, 0),  # 红色网格线
        line_width=3,  # 3像素宽
        background=(240, 240, 240)  # 浅灰色背景
    )

    # 重新组合验证
    splitter.recombine()

    # 获取并保存特定单元格
    splitter.save_grid_cell(1, 1, "center_cell.jpg")

    print("九宫格分割操作完成！请查看输出文件夹。")

from openai import OpenAI

from config import config
from utils.image_processing import image_to_base64


class ImageAnalyzer:
    """多图片分析工具类"""

    def __init__(self, api_key: str):
        """
        初始化分析器

        :param api_key: 阿里云DashScope API密钥
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.image_descriptions = []

    def analyze_image(self, image_path: str, question: str = "图中描绘的是什么?"):
        """
        https://help.aliyun.com/zh/model-studio/vision

        :param image_path: 图片路径
        :param question: 分析问题
        :return:
        """
        image_base64 = image_to_base64(image_path)

        completion = self.client.chat.completions.create(
            model="qwen-vl-max-latest",
            # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/models
            messages=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "你是一个专业的图像分析助手，请准确描述图片内容。"}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_base64
                            },
                        },
                        {"type": "text", "text": question},
                    ],
                },
            ],
        )
        if completion.choices and completion.choices[0].message.content:
            result = completion.choices[0].message.content
            # 存储描述结果
            self.image_descriptions.append(result)
            return result

    def analyze_descriptions(self, question: str):
        """
        基于图片描述信息，给出问题的正解

        :param question:
        :return:
        """
        # 构建比较请求
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "你是一个专业的分析助手，需要基于多张图片的描述进行比较分析。"}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"以下是多张图片的分析描述，请根据这些描述回答（回答的结果为：4,5，表示第四张、第五张的意思；若没有匹配的结果返回0）：{question}\n\n"}
                ],
            }
        ]

        # 添加所有图片描述
        for i, desc in enumerate(self.image_descriptions):
            messages[1]["content"].append({
                "type": "text",
                "text": f"图片{i + 1}描述: {desc}\n"
            })

        try:
            completion = self.client.chat.completions.create(
                model="qwen-vl-max-latest",
                messages=messages,
                max_tokens=800,
                temperature=0.3,
            )

            if completion.choices and completion.choices[0].message.content:
                return completion.choices[0].message.content
            return "比较分析未收到有效响应"

        except Exception as e:
            return f"比较分析失败: {str(e)}"


if __name__ == '__main__':
    analyzer = ImageAnalyzer(config.DASHSCOPE_API_KEY)

    analyzer.analyze_image("deduplicator/9grid_output/grid_00.jpg")
    analyzer.analyze_image("deduplicator/9grid_output/grid_01.jpg")
    analyzer.analyze_image("deduplicator/9grid_output/grid_02.jpg")
    analyzer.analyze_image("deduplicator/9grid_output/grid_10.jpg")
    analyzer.analyze_image("deduplicator/9grid_output/grid_11.jpg")
    analyzer.analyze_image("deduplicator/9grid_output/grid_12.jpg")
    analyzer.analyze_image("deduplicator/9grid_output/grid_20.jpg")
    analyzer.analyze_image("deduplicator/9grid_output/grid_21.jpg")
    analyzer.analyze_image("deduplicator/9grid_output/grid_22.jpg")

    print(analyzer.analyze_descriptions("哪些事物或者动物能在公园里看到"))

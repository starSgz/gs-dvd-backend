from qrcode.main import QRCode
from io import BytesIO
from PIL import Image
import base64
import os
# from fake_useragent import UserAgent #pip install fake_useragent


class QRCodeLogin:

    def get_qrcode(self):
        """
        获取二维码地址
        :return:
        """
        raise NotImplemented

    def listen_qrcode(self,token, blocking=False):
        """
        监听响应接口
        :return:
        """
        raise NotImplemented

    def verify_login(self,cookies):
        """
        检测cookies是否有效
        :return:
        """
        raise NotImplemented

    @classmethod
    def bash64_qrcode(cls, img):
        """
        将图像转换为base64格式
        :param img: 支持以下类型：
                   - 字符串(str): base64编码字符串、图像文件路径、或生成二维码的文本内容
                   - BytesIO对象: 内存中的图像数据
                   - PIL.Image对象: PIL图像对象
        :return: base64编码的字符串
        """
        pil_image = None

        # 类型1: 处理字符串类型（可能是base64或文件路径）
        if isinstance(img, str):
            # 尝试判断是否为base64字符串
            img_data = img
            # 移除可能的data URI前缀
            if img_data.startswith('data:image'):
                img_data = img_data.split(',', 1)[1] if ',' in img_data else img_data

            # 尝试解码验证是否为base64
            try:
                base64.b64decode(img_data, validate=True)
                # 如果成功解码，说明是有效的base64字符串，直接返回
                return img_data
            except Exception:
                # 解码失败，尝试作为文件路径处理
                if os.path.exists(img):
                    pil_image = Image.open(img)
                else:
                    # 既不是base64也不是文件路径，将字符串作为内容生成二维码
                    qr = QRCode(
                        version=5,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(img)
                    qr.make(fit=True)
                    pil_image = qr.make_image(fill_color="black")

        # 类型2: 处理BytesIO对象
        elif isinstance(img, BytesIO):
            pil_image = Image.open(img)

        # 类型3: 处理PIL.Image对象
        elif isinstance(img, Image.Image):
            pil_image = img

        # 不支持的类型
        else:
            raise TypeError(f"不支持的输入类型: {type(img)}。仅支持文件路径、base64字符串、BytesIO或PIL.Image对象")

        # 统一转换为base64
        if pil_image:
            buffer = BytesIO()
            pil_image.save(buffer, format='PNG')
            img_bytes = buffer.getvalue()
            base64_str = base64.b64encode(img_bytes).decode('utf-8')
            return base64_str

        raise RuntimeError("图像处理失败")

    @classmethod
    def show_qrcode(cls, img):
        """
        制作或显示二维码
        :param img: 字符串URL 或 IO对象(BytesIO/PIL.Image)
        """
        if isinstance(img, str):
            # 传入字符串，生成二维码
            qr = QRCode(
                version=5,
                box_size=10,
                border=4,
            )
            qr.add_data(img)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black")
            qr_img.show()
        elif isinstance(img, BytesIO):
            # 传入BytesIO对象，转换为图片并展示
            qr_img = Image.open(img)
            qr_img.show()
        elif isinstance(img, Image.Image):
            # 传入PIL Image对象，直接展示
            img.show()
        else:
            raise TypeError("参数必须是字符串URL或IO图片对象")

    def get_stores(self,cookies):
        """
        获取店铺名称
        """
        pass



if __name__ == '__main__':
    # Qrcode.show_qrcode("https://aka.ms/PSWindows")
    print(QRCodeLogin.bash64_qrcode("https://aka.ms/PSWindows"))
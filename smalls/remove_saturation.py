import cv2
import sys
import os

"""
从命令行读取图片文件路径
用opencv读取图片
转为hsv
将s设置为0
转为rgb
保存图片为basename_saturation_removed.extName
"""


def remove_saturation(image_path):
    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"无法读取图片: {image_path}")

    # 转换为HSV色彩空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 将饱和度通道设置为0
    hsv[:, :, 1] = 0

    # 转换回RGB色彩空间
    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # 构造新的文件名
    base_name, ext_name = os.path.splitext(image_path)
    new_filename = f"{base_name}_saturation_removed{ext_name}"

    # 保存图片
    cv2.imwrite(new_filename, rgb)
    print(f"图片已保存为: {new_filename}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python remove_saturation.py <图片路径>")
        sys.exit(1)

    image_path = sys.argv[1]
    remove_saturation(image_path)

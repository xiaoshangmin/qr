# -*- coding: utf-8 -*-

from PIL import Image
import os


def draw_qrcode(abspath, qrmatrix):
    # 每个黑色点要画的大小:unit_len的平方 2x2=4个像素点
    unit_len = 3
    # 画的起始位置
    x = y = 3*unit_len
    # 创建一个底色为白色的图片 底色可以修改
    pic = Image.new('RGB', [(len(qrmatrix)+6)*unit_len]*2, (255, 255, 255))
    # 从上往下画
    for line in qrmatrix:
        for module in line:
            if module:
                draw_a_black_unit(pic, x, y, unit_len)
            x += unit_len
        x, y = 3*unit_len, y+unit_len

    saving = os.path.join(abspath, 'qrcode.png')
    pic.save(saving)
    return saving

# 画黑色的点（可画其他颜色）


def draw_a_black_unit(p, x, y, ul):
    for i in range(ul):
        for j in range(ul):
            p.putpixel((x+i, y+j), (0, 0, 0))

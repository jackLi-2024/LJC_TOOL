#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from reportlab.graphics.shapes import Path
from reportlab.lib import colors
from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Group, Drawing, scale


class ReportLabPen(BasePen):
    """A pen for drawing onto a reportlab.graphics.shapes.Path object."""

    def __init__(self, glyphSet, path=None):
        BasePen.__init__(self, glyphSet)
        if path is None:
            path = Path()
        self.path = path

    def _moveTo(self, p):
        (x, y) = p
        self.path.moveTo(x, y)

    def _lineTo(self, p):
        (x, y) = p
        self.path.lineTo(x, y)

    def _curveToOne(self, p1, p2, p3):
        (x1, y1) = p1
        (x2, y2) = p2
        (x3, y3) = p3
        self.path.curveTo(x1, y1, x2, y2, x3, y3)

    def _closePath(self):
        self.path.closePath()


class TtfToImage():

    def __init__(self, fontName, imagePath, fmt="png"):
        """

        :param fontName: ttf文件名
        :param imagePath: 转存图片路径
        :param fmt: 图片格式/png/jpg
        """
        self.fontName = fontName
        self.imagePath = imagePath
        self.fmt = fmt
        os.makedirs(imagePath, exist_ok=True)

    def key(self, data):
        """
        对保存的文件名称做处理，一般情况下，ttf文件的实际值为unicode码
        :param data: 处理的数据
        :return:
        """
        try:
            return chr(int(data))
        except:
            return

    def draw(self, dx=5, dy=300, auto_width=500, auto_height=500):
        """
        绘图操作
        :param dx: 图片绘图位置
        :param dy:  图片绘图位置
        :param auto_width: 自适应图片宽度（调节字体）
        :param auto_height: 自适应图片高度（调节字体）
        :return:
        """

        def reverse_dict(data: dict):
            out = {}
            for k, v in data.items():
                out[str(v)] = str(k)

            return out

        font = TTFont(self.fontName)
        img_dict = font['cmap'].tables[2].ttFont.tables['cmap'].tables[1].cmap
        img_dict = reverse_dict(img_dict)
        gs = font.getGlyphSet()
        glyphNames = font.getGlyphNames()
        for i in glyphNames:
            name = self.key(img_dict.get(i))
            if name == None:
                continue
            g = gs[i]
            pen = ReportLabPen(gs, Path(fillColor=colors.black, strokeWidth=10))
            g.draw(pen)
            w, h = g.width, g.width
            g = Group(pen.path)
            g.translate(dx, dy)
            d = Drawing(w + auto_width, h + auto_height)
            d.add(g)
            imageFile = self.imagePath + "/" + str(name) + "." + self.fmt
            renderPM.drawToFile(d, imageFile, self.fmt)


if __name__ == '__main__':
    t2i = TtfToImage(fontName="./22822.ttf", imagePath="test")
    t2i.draw()

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
import sys
import json
import time
from PIL import Image, ImageEnhance, ImageFilter, ImageGrab


class CaptchaImage():
    """
    项目要求：
        验证码图片名称必须是，{标签}.png
        传入路径为单张图片路径，
        该类不单独使用，，使用时确保传入路径目录存在
    """

    def __init__(self, input_path: str, output_path: list):
        self.input_path = input_path
        self.output_path = output_path
        self.__columns_counter = []
        self.__letter_column_id = []

    def open(self):
        self.img = Image.open(self.input_path)
        self.img_size = self.img.size
        self.img_x, self.img_y = self.img_size

    def fresh_img(self):
        """刷新图像参数"""
        self.pix = self.img.load()
        self.img_size = self.img.size
        self.img_x, self.img_y = self.img_size

    def add_background(self, mode="RGBA", color=(255, 255, 255), position=None):
        if position == None:
            position = (0, 0, self.img_x, self.img_y)
        new_img = Image.new(mode=mode, size=self.img_size, color=color)
        new_img.paste(self.img, box=position, mask=self.img)
        self.img = new_img

    def filter(self, condition=ImageFilter.MedianFilter(1)):
        """过滤器"""
        self.img = self.img.filter(condition)

    def contrast(self, factor):
        """增加对比度"""
        enhancer = ImageEnhance.Contrast(self.img)
        self.img = enhancer.enhance(factor=factor)

    def sharpness(self, factor):
        """锐化处理"""
        enhancer = ImageEnhance.Sharpness(self.img)
        self.img = enhancer.enhance(factor=factor)

    def brightness(self, factor):
        """增加亮度"""
        enhancer = ImageEnhance.Brightness(self.img)
        self.img = enhancer.enhance(factor=factor)

    def convert(self):
        """灰度处理"""
        self.img = self.img.convert("L")

    def sub_noise(self, threshold=200):
        """降噪"""
        column_counter = 0
        for x in range(0, self.img_x):
            for y in range(0, self.img_y):
                if self.pix[x, y] < threshold:
                    column_counter += 1
                    self.pix[x, y] = 0
                else:
                    self.pix[x, y] = 255

            self.__columns_counter.append(column_counter)
            column_counter = 0

    def __split_letter__(self, letter_max_length):
        """
        拆分整体字符为单个字符
        :param letter_max_length: 单个字符最大长度
        """

        def split(data: list):
            max_length = 0
            index = 0
            index_length = 0
            for i in range(len(data)):
                length = len(data[i])
                if length > max_length:
                    max_length = length
                    index_length = length
                    index = i
            index_slice = int(index_length / 2)
            a = data[index][0:index_slice]
            b = data[index][index_slice:]
            data[index] = a
            data.insert(index + 1, b)
            return data

        i = 0
        while i in range(len(self.__columns_counter)):
            letter_id = []
            while self.__columns_counter[i] != 0:
                letter_id.append(i)
                i += 1
            if letter_id:
                self.__letter_column_id.append(letter_id)

            i += 1

        while len(self.__letter_column_id) < len(self.output_path):
            self.__letter_column_id = split(self.__letter_column_id)
        return len(self.__letter_column_id)

    def cut(self, letter_max_length=None):
        """字符切割"""
        self.fresh_img()
        self.sub_noise()
        letter_count = self.__split_letter__(letter_max_length)
        print(f"需要拆分：{len(self.output_path)}份，实际拆分：{letter_count}份")
        if letter_count != len(self.output_path):
            raise Exception(f"当前图片切割失败[{self.input_path}]")
        for j in range(letter_count):
            letter = len(self.__letter_column_id[j])
            img = Image.new("L", (letter, self.img_y))
            for y in range(self.img_y):
                i = 0
                for x in self.__letter_column_id[j]:
                    img.putpixel([i, y], self.pix[x, y])
                    i += 1
            self.save(img, path=self.output_path[j])

    def save(self, img, path):
        img.save(path)


class CaptchaImages():
    """
    验证码图片批量处理
    """

    def __init__(self, input_dir, output_path):
        pass


if __name__ == '__main__':
    captcha = CaptchaImage(input_path="./images/MJ1.jpg",
                           output_path=["./test1/7.png", "./test1/2.png", "./test1/5.png", "./test1/3.png"])
    captcha.open()
    captcha.add_background()
    captcha.filter()
    captcha.contrast(factor=2)
    captcha.sharpness(factor=2)
    captcha.brightness(factor=2)
    captcha.convert()
    # img = captcha.img
    # captcha.save(img,path="./test1/7253.png")
    captcha.cut(letter_max_length=12)

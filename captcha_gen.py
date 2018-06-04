#!/usr/bin/python3
'''
TODO
사진에 captcha가 한장씩만 존재하는게 문제가 될 수도 있다고 판단함.
1 ~ 3장 정도로 다양하게 들어갈 수 있도록 할 예정.

사진의 배경이 다양해질 수 있도록 할 예정.

'''
import argparse 
import math
import os
import random
import string	#digit, alphabet, alphanumeric set
import sys
from sys import argv

import PIL
from claptcha import Claptcha
from PIL import Image


def generate_captcha(noise=0.5, length=1):
	"""
	It returns captcha object.
	"""
	def isfont(filename):
		return True if filename.find(".ttf") != -1 or filename.find(".otf") != -1 else False

	def randomChar(length):
		return "".join(random.choices(string.digits, k=length))
	fonts = [font for font in os.listdir("./fonts/") if isfont(font)]


	font = "./fonts/" + random.choice(fonts)
	size = random.randint(100, 200)

	captcha = Claptcha(randomChar(length), font, (size * length, size),
					   margin=(1, 1), resample=Image.BILINEAR, noise=noise)
	return captcha


def add_background(captcha: Claptcha):
	'''
	return: (roi, image)
	'''
	def get_random_ROI():
		leftupper = (random.randint(0, captcha.w), random.randint(0, captcha.h))
		rightlower = (leftupper[0] + captcha.w, leftupper[1] + captcha.h)
		return (*leftupper, *rightlower)
	# white background
	background = Image.new(
		"RGB", (captcha.w * 2, captcha.h * 2), color=(255, 255, 255))
	roi = get_random_ROI()
	background.paste(captcha.image[1], roi)
	return (roi, background)


def write_captcha(image: Image.Image, filename_without_extension):
	folder = "./img/"
	os.makedirs(folder, exist_ok=True)
	return image.save(folder + filename_without_extension + ".jpg")


def make_ground_truth_box(class_index, roi, image: Image.Image, file_basename):
	'''
	roi: (leftupper.x, leftupper.y, rightlower.x, rightlower.y)
	'''
	folder = "./img/"
	os.makedirs(folder, exist_ok=True)

	roi_width = roi[2] - roi[0]
	roi_height = roi[3] - roi[1]
	center = ((roi[0] + roi[2]) / 2, (roi[1] + roi[3]) / 2)

	with open(folder + file_basename + ".txt", mode="w+") as f:
		f.write("{class_index} {x:f} {y:f} {width:f} {height:f}\n".format(
			class_index=class_index, x=center[0] / image.width,
			y=center[1] / image.height,
			width=roi_width / image.width,
			height=roi_height/image.height))
	return


if __name__ == "__main__":
	if len(argv) < 2:
		print("Usage: {} <numbers of captcha> [-valid]".format(argv[0]), file=sys.stderr)
		exit(1)

	num_of_captcha = int(argv[1])


	for i in range(num_of_captcha):
		if argv.count("-valid"):
			length = random.randint(2, 6)
		else:
			length = 1
		captcha = generate_captcha(noise=0, length=length)
		file_basename = "{cnt:05d}_label_{label:s}".format(
			cnt=i, label=captcha.source)
		roi, image = add_background(captcha)
		make_ground_truth_box(captcha.source, roi, image, file_basename)
		write_captcha(image, file_basename)
		print("{}th image, label: {}".format(i, captcha.text))

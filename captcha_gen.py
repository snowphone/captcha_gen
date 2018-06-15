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


class Captcha_image():

	def __init__(self, noise=0, valid=False):
		self.captcha_list = []
		self.roi_list = []
		self.noise = noise
		self.valid = valid
		self.max_size = 200
		self.max_captcha_num = 5
		self.image = Image.new( 
				"RGB", 
				(int(self.max_size * 0.9 * (self.max_captcha_num + 1)), self.max_size * 2),			
				color=(255, 255, 255))

		self._generate_captcha()
		self._add_background()
		return
	
	def _generate_captcha(self):
		"""
		It returns captcha object.
		"""
		def isfont(filename):
			return True if filename.find(".ttf") != -1 or filename.find(".otf") != -1 else False

		def randomChar():
			return random.choice(string.digits)
		fonts = [font for font in os.listdir("./fonts/") if isfont(font)]


		font = "./fonts/" + random.choice(fonts)
		size = random.randint(self.max_size // 2, self.max_size)

		self.captcha_list = [ Claptcha(
			randomChar(), 
			font, 
			(size * 0.9 , size),
			margin=(0, 0), 
			resample=Image.BILINEAR, 
			noise=self.noise) 
			for _ in range(random.randint(1, self.max_captcha_num))]

		return self.captcha_list
	
	def _add_background(self):

		captcha_num = len(self.captcha_list)
		width = self.captcha_list[0].w 
		height = self.captcha_list[0].h

		def get_random_roi(width, height):
			leftupper = (random.randint(0, width), random.randint(0, height))
			rightlower = (leftupper[0] + width, leftupper[1] + height)
			return (leftupper, rightlower)

		def split_roi(leftupper, rightlower):
			ret = []
			for index in range(captcha_num):
				x = leftupper[0] + index * width
				y = leftupper[1]
				roi = (x, y, x + width, y + height)
				ret.append(roi)
			return ret

		_roi = get_random_roi(width * captcha_num, height)
		self.roi_list = split_roi(*_roi)

		for roi, captcha in zip(self.roi_list, self.captcha_list):
			self.image.paste(captcha.image[1], roi)
		return 


	def save(self, filename_without_extension):
		folder = "./img/"
		os.makedirs(folder, exist_ok=True)

		if not self.valid:
			self._make_ground_truth_box(filename_without_extension)

		return self.image.save(folder + filename_without_extension + ".jpg")


	def _make_ground_truth_box(self, file_basename):
		'''
		roi: (leftupper.x, leftupper.y, rightlower.x, rightlower.y)
		'''
		folder = "./img/"

		with open(folder + file_basename + ".txt", mode="w+") as f:
			for roi, captcha in zip(self.roi_list, self.captcha_list):
				roi_width = roi[2] - roi[0]
				roi_height = roi[3] - roi[1]
				center = ((roi[0] + roi[2]) / 2, (roi[1] + roi[3]) / 2)

				f.write("{class_index} {x:f} {y:f} {width:f} {height:f}\n".format(
					class_index=captcha.text,
					x=center[0] / self.image.width,
					y=center[1] / self.image.height,
					width=roi_width / self.image.width,
					height=roi_height / self.image.height)
					)
		return
	#end of Captcha_image 


if __name__ == "__main__":
	try:
		num_of_captcha = int(argv[1])
	except IndexError as err:
		print("Usage: {} <numbers of captcha> [-valid]".format(argv[0]), file=sys.stderr)
		exit(1)

	for i in range(num_of_captcha):
		captcha = Captcha_image()
		label = "".join([cap.text for cap in captcha.captcha_list])
		file_basename = "{cnt:05d}_label_{label:s}".format( cnt=i, label=label )
		captcha.save(file_basename)
		print("{}th image, label: {}".format(i, label))

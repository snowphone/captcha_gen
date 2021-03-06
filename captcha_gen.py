#!/usr/bin/python3
'''
TODO
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
from PIL import ImageFilter
import captcha
from captcha.image import ImageCaptcha, random_color 
from PIL import Image

class myCaptcha(captcha.image.ImageCaptcha):
	def __init__(self, width=160, height=60, fonts=None, font_sizes=None):
		super().__init__(width, height, fonts, font_sizes)
		self.background = random_color(238, 255)
		self.color = random_color(10, 200, random.randint(220, 255))

	def generate_image(self, chars):
		im = self.create_captcha_image(chars, self.color, self.background)
		return im
	#end of myCaptcha





class Captcha_image():

	#public
	def __init__(self, noise=0):

		def isfont(filename):
			return True if filename.find(".ttf") != -1 or filename.find(".otf") != -1 else False

		self.captcha_list = []
		self.label_list = []
		self.table = self._init_table()
		self.fonts = [os.path.join(dirpath, name) 
				for dirpath, _dirname, names in os.walk("./fonts/") 
				for name in names
				if isfont(name)]


		self.roi_list = []
		self.noise = noise
		self.max_size = 80
		self.max_captcha_num = 8

		size = random.randint(self.max_size // 2, self.max_size)
		ratio = 0.7
		self.generator = myCaptcha(fonts=["./fonts/monospace/saxmono.ttf"], font_sizes=(int(size * ratio),int(size * ratio),int(size * ratio)))
		self._generate_captcha(int(size * ratio), size)

		char_num = len(self.captcha_list)
		self.image = Image.new( 
				"RGB", 
				(int(size * ratio * (char_num) * 1.5), int(size * 1.5)),			
				color=self.generator.background)

		self._add_background()
		return

	def save(self, filename_without_extension):
		folder = "./img/"
		os.makedirs(folder, exist_ok=True)

		self._make_ground_truth_box(filename_without_extension)

		return self.image.save(folder + filename_without_extension + ".jpg")

	#private
	def _init_table(self):
		table = {}
		for i, ch in enumerate(string.ascii_lowercase):
			table[ch] = i
		return table

	def _random_char(self):
		return random.choice(string.ascii_lowercase)


	def _generate_captcha(self, width, height, margin=(0,0)):
		"""
		It returns captcha object.
		"""

		char_num = random.randint(1 if self.max_captcha_num == 1 else self.max_captcha_num // 2, self.max_captcha_num)
		self.generator._width = width
		self.generator._height = height

		for _ in range(char_num):
			text = self._random_char()
			self.label_list.append(text)
			self.captcha_list.append(self.generator.generate_image(text))


		return self.captcha_list
	
	def _add_background(self):

		captcha_num = len(self.captcha_list)
		width = self.captcha_list[0].width
		height = self.captcha_list[0].height

		def get_random_roi(width, height):
			leftupper = (random.randint(10, self.image.width - width - 10), random.randint(10, self.image.height - height - 10))
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
			self.image.paste(captcha, roi)

		self._make_noise()
		return 

	def _make_noise(self):
		self.generator.create_noise_dots(self.image, self.generator.color)
		self.generator.create_noise_curve(self.image, self.generator.color)
		self.image = self.image.filter(ImageFilter.SMOOTH)
		return


	def _make_ground_truth_box(self, file_basename):
		'''
		roi: (leftupper.x, leftupper.y, rightlower.x, rightlower.y)
		'''
		folder = "./img/"

		with open(folder + file_basename + ".txt", mode="w+") as f:
			for roi, captcha, text in zip(self.roi_list, self.captcha_list, self.label_list):
				roi_width = roi[2] - roi[0]
				roi_height = roi[3] - roi[1]
				center = ((roi[0] + roi[2]) / 2, (roi[1] + roi[3]) / 2)

				f.write("{class_index} {x:f} {y:f} {width:f} {height:f}\n".format(
					class_index=self.table[text],
					x=center[0] / self.image.width,
					y=center[1] / self.image.height,
					width=roi_width / self.image.width,
					height=roi_height / self.image.height)
					)
		return
	#end of Captcha_image 

class Validation_image(Captcha_image):
	def __init__(self, noise=0):
		super().__init__(noise)
		return

	def _random_char(self):
		n = random.randint(4, 8)
		ret = ""
		for _ in range(n):
			ret += super()._random_char()
		return ret

	def _generate_captcha(self, _w, _h):
		self.max_captcha_num = 1
		n = random.randint(self.max_size // 2, self.max_size)
		width = 200
		height = 75
		self.generator._font_sizes = (42, 50, 56)

		return super()._generate_captcha(width, height, (10, 10))

	def _make_ground_truth_box(self, _file_basename):
		self.image = self.captcha_list[0]
		pass

	def _add_background(self):
		self._make_noise()
		pass



if __name__ == "__main__":
	try:
		num_of_captcha = int(argv[1])
	except IndexError as err:
		print("Usage: {} <numbers of captcha> [-valid]".format(argv[0]), file=sys.stderr)
		exit(1)
	
	isvalid = bool(argv.count("-valid"))

	for i in range(num_of_captcha):
		if isvalid:
			captcha = Validation_image()
		else:
			captcha = Captcha_image() 
		label = "".join([cap for cap in captcha.label_list ])
		file_basename = "{cnt:05d}_label_{label:s}".format( cnt=i, label=label )
		if isvalid:
			file_basename = "valid_" + file_basename 
		captcha.save(file_basename)
		print("{}th image, label: {}".format(i, label))

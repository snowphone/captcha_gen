import math
import os
import random
import string

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

	# def randomString():
	#     rndLetters = (random.choice(string.ascii_uppercase) for _ in range(6))
	#     return "".join(rndLetters)

	font = "./fonts/" + random.choice(fonts)
	size = random.randint(100, 200)

	# Initialize Claptcha object with random text, FreeMono as font, of size
	# 100x30px, using bicubic resampling filter and adding a bit of white noise
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


def make_ground_truth_box(roi, image: Image.Image, file_basename):
	'''
	roi: (leftupper.x, leftupper.y, rightlower.x, rightlower.y)
	'''
	folder = "./img/"
	os.makedirs(folder, exist_ok=True)

	roi_width = roi[2] - roi[0]
	roi_height = roi[3] - roi[1]
	center = ((roi[0] + roi[2]) / 2, (roi[1] + roi[3]) / 2)

	with open(folder + file_basename + ".txt", mode="w+") as f:
		f.write("{index:d} {x:f} {y:f} {width:f} {height:f}\n".format(
			index=0, x=center[0] / image.width,
			y=center[1] / image.height,
			width=roi_width / image.width,
			height=roi_height/image.height))
	return


if __name__ == "__main__":
	for i in range(10):
		captcha = generate_captcha(noise=0.3)
		file_basename = "{cnt:05d}_label_{label:s}".format(
			cnt=i, label=captcha.source)
		roi, image = add_background(captcha)
		make_ground_truth_box(roi, image, file_basename)
		write_captcha(image, file_basename)
		print("{}th image, label: {}".format(i, captcha.text))

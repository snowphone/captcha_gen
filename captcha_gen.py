import random
import string
from PIL import Image
from claptcha import Claptcha
import os



def generate_captcha(noise=0.5, length =1):
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
	captcha = Claptcha(randomChar(length), font, (size * length, size), resample=Image.BILINEAR, noise=noise)
	return captcha

def write_captcha(captcha : Claptcha, init_count_val=None):
	if init_count_val:
		#write_captcha.counter: static variable
		write_captcha.counter = init_count_val
	else:
		write_captcha.counter += 1

	captcha.write("{cnt:05d}_label_{label:s}.png".format(cnt=write_captcha.counter, label=captcha.source))
	return
write_captcha.counter = 0




if __name__ == "__main__":
	for _ in range(10):
		generate_captcha(noise=0.3)

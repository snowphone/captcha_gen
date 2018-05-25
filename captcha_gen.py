import random
import string
from PIL import Image
from claptcha import Claptcha
import os


word_dic = {}

def scg(size, noise=0.5, length =1, font="C:/Windows/Fonts/ARLRDBD.TTF"):

    # def randomString():
    #     rndLetters = (random.choice(string.ascii_uppercase) for _ in range(6))
    #     return "".join(rndLetters)

    def randomChar():
        rndChars = (random.choice(string.ascii_uppercase) for _ in range(length))
        return "".join(rndChars)

    # Initialize Claptcha object with random text, FreeMono as font, of size
    # 100x30px, using bicubic resampling filter and adding a bit of white noise
    #print(randomChar)
    c = Claptcha(randomChar(), font, (size,size), resample=Image.BILINEAR, noise=0.55)
    filename = c.source
    
    #font var, 1char pront? , font,
    #noise, font, 
    #size, margin out
    if filename in word_dic.keys() :
        word_dic[filename] = word_dic[filename] + 1
    else : 
        word_dic[filename] = 1
    text, _ = c.write(filename +'(' + str(word_dic[filename]) +  ').png')
    print(text)  # string printed into filename.png

i=0
while i < 10:
    i = i + 1
    scg(450, 0.3)
import os
import numpy as np
import cv2
from PIL import Image

def RGBAnalysis(image):
    # crop (unnecessary)
    width, height = image.size
    if (width>63 and height>63):
        left = int(width/2)-32
        right = int(width/2)+31
        top = int(height/2)-32
        bottom = int(height/2)+31
        image = image.crop((left, top, right, bottom)) 
    else: pass
    # filter
    # print(image.shape)
    r,g,b = image.split()
    redhis = r.histogram()
    greenhis = g.histogram()
    bluehis = b.histogram()
    # weighted average
    red = 0
    green = 0
    blue = 0
    denom = sum(redhis)
    for i in range(256):
        red += i*redhis[i]
        green += i*greenhis[i]
        blue += i*bluehis[i]
    red = int(red/denom)
    green = int(green/denom)
    blue = int(blue/denom)
    rgb = (red, green, blue)
   
    return rgb   

def reverse_gamma(var): # linear RGB to sRGB
    if var<=0.00304: return var*12.92
    else: return 1.055*(var**(1/2.4))-0.055

def gamma(var): # sRGB to linear RGB
    if var<=0.04045: return var/12.92
    else: return ((var+0.055)/1.055)**2.4

def RGBtoCIEXYZ(rgb):
    trans = [[41.24,35.76,18.05],
            [21.26,71.52,7.22],
            [1.93,11.92,95.05]]
    Rlin = gamma(rgb[0]/255)
    Glin = gamma(rgb[1]/255)
    Blin = gamma(rgb[2]/255)
    cieXYZ = np.matmul(trans,[Rlin, Glin, Blin])
    return cieXYZ

def CIEXYZtoCIEYxy(cieXYZ):
    Sum = sum(list(cieXYZ))
    bigY = cieXYZ[1]
    x = cieXYZ[0]/Sum
    y = cieXYZ[1]/Sum
    return (bigY, x, y)

def cauculate_rgb(img):
    rgb = RGBAnalysis(img)
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cieXYZ = RGBtoCIEXYZ(rgb)
    cieYxy = CIEXYZtoCIEYxy(cieXYZ)

    return img, rgb, cieXYZ, cieYxy

    
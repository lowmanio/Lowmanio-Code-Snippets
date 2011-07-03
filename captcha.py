# python imports
import random
import Image
import ImageFont
import ImageDraw
import ImageFilter
from cStringIO import StringIO
from os import path
 
"""
    This code is taken from and is copyright to:
    http://code.activestate.com/recipes/440588/
	
	It has been modified by Sarah Lowman, especially 
	generateCaptcha() and gen_random_word()
"""
 
FONT_FILE = path.join(ROOT_DIR, 'lowmanio', 'utils', 'arialbd.ttf') # change this to wherever your font file is

 
def gen_captcha(text, fnt, fnt_sz, f, fmt='JPEG'):
    """Generate a captcha image"""
    
    # randomly select the foreground color
    fgcolor = random.randint(0,0xffff00)

    # make the background color the opposite of fgcolor
    bgcolor = fgcolor ^ 0xffffff
    
    # create a font object 
    font = ImageFont.truetype(fnt,fnt_sz)
    
    # determine dimensions of the text
    dim = font.getsize(text)
    
    # create a new image slightly larger that the text
    im = Image.new('RGB', (dim[0]+5,dim[1]+5), bgcolor)
    d = ImageDraw.Draw(im)
    x, y = im.size
    r = random.randint
    
    # draw 100 random colored boxes on the background
    for num in range(100):
        d.rectangle((r(0,x),r(0,y),r(0,x),r(0,y)),fill=r(0,0xffffff))

    # add the text to the image
    d.text((3,3), text, font=font, fill=fgcolor)
    im = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
    
    # save the image to a file
    im.save(f, format=fmt)
 
def gen_random_word(wordLen=6):
    """Generate a random word of length wordLen. Some characters have been removed
    to avoid ambiguity such as i,l,o,I,L,0, and 1"""
 
    allowedChars = "abcdefghjkmnpqrstuvwzyzABCDEFGHJKMNPQRSTUVWZYZ23456789"
    word = ""

    for i in range(0, wordLen):
        word = word + allowedChars[random.randint(0,0xffffff) % len(allowedChars)]

    return word
 
def generateCaptcha():
    """Generate a captcha image in memory using a randomly generated word and a font 
    file on the system. Returns the word and the image"""
    
    word = gen_random_word()
    buf = StringIO()
    gen_captcha(word.strip(), FONT_FILE, 50, buf)
    s = buf.getvalue()
    buf.close()
    return word, s
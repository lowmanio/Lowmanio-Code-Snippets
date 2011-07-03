"""
    Short script to hide a PNG image within another PNG image based
    on the example given on 
        http://en.wikipedia.org/wiki/Steganography
    which hides an image of a cat within an image of trees. The script
    also recovers hidden PNGs. 
    
    From wikipedia:
        "By removing all but the last 2 bits of each color component, 
        an almost completely black image results. Making the resulting 
        image 85 times brighter results in the image"
    
    This script only works with PNG files that are exactly the same 
    height and width.
    
    The fewer colours used the better the result, and especially 
    when using high contrasting colours. 
    
    Installation
    ============
    
    Please download the pyPNG library which can be found at:
        http://code.google.com/p/pypng
        
    If you want to use the images from wikipedia, they can be found here:
        http://en.wikipedia.org/wiki/File:StenographyOriginal.png
        http://en.wikipedia.org/wiki/File:StenographyRecovered.png
    
    To hide an image:
    =================
        > python steg.py encode file-to-hide-data-in.png file-to-be-hidden.png
        
    This will output a file named hidden.png in the same folder
    as the python script.
        
    To recover an image:
    ====================
        > python steg.py decode file-with-hidden-image.png
        
    This will output a file named recovered.png in the same folder
    as the python script. 
    
    Usage
    =====
    
    Feel free to use and modify the script to make it better! If you have any 
    cool additions or bug fixes I'd love to know about them, so email me at 
    sarah@lowmanio.co.uk
    
"""

__author__ = 'Sarah Lowman <http://lowmanio.co.uk/>'

import sys
import png

def decode(line):
    """ Takes in a line of RGB values. Each value is replaced by the last
    two bits of the value multiplied by 85 """
    
    new_line = []
    
    for p in line:
        p = p & 3       # 3 is 00000011 in binary
        p = 85 * p      # scale p to be between 0 and 255 (255/3 = 85)
        new_line.append(p)

    return new_line

def encode(line, hideLine):
    """ Takes in the same line of RGB values from the file to hide in (A) and
    the file to be hidden (B). Each value of B is turned into a number between
    0 and 3 and then ORed with the first 6 bits of A. """
    
    new_line = []
    
    for p, q in zip(line, hideLine):
        x = int(round(q / 85))
        p = (p & 252) | x
        new_line.append(p)

    return new_line

def hide_image(file, hiddenfile):
    """ Hides 'hiddenfile' within 'file' """
    
    im = png.Reader(filename=file)
    width, height, pixels, meta = im.read()

    imHide = png.Reader(filename=hiddenfile)
    widthHide, heightHide, pixelsHide, metaHide = imHide.read()
    
    out_file = open('hidden.png', 'wb')
    
    # transform
    new_pixels = [encode(line, hideLine) for line, hideLine in zip(pixels, pixelsHide)]
    
    # output image
    writer = png.Writer(width=width, height=height, **meta)
    writer.write(out_file, new_pixels)    

def reveal_image(file):
    """ Reveals an image hidden within 'file' """
    
    # input image
    im = png.Reader(filename=file)
    width, height, pixels, meta = im.read()
    
    out_file = open('recovered.png', 'wb')
    
    # transform
    new_pixels = [decode(line) for line in pixels]
    
    # output image
    writer = png.Writer(width=width, height=height, **meta)
    writer.write(out_file, new_pixels)

def main():
    try:
        if sys.argv[1] == "encode":
            try:
                hide_image(sys.argv[2], sys.argv[3])
            except IndexError:
                print "Please supply two PNG files. The first is the file the image will be hidden in, the second is the image to hide."
        elif sys.argv[1] == "decode":
            try:
                reveal_image(sys.argv[2])
            except IndexError:
                print "Please supply a PNG with a hidden image."
        else:
            print "invalid argument. Please use 'encode' or 'decode'"
    except IndexError:
        print "Please type 'encode' or 'decode' after the python file followed by two PNG files for encode, and one for decode."
        
if __name__ == "__main__":
    main()

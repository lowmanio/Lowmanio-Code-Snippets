"""
    
    Installation
    ============
    
    Please download the pyPNG and pyCrypto libraries which can be found at:
        http://code.google.com/p/pypng
        https://www.dlitz.net/software/pycrypto/

    To change the AES key, edit line 148.
    
    To hide an image:
    =================
        > python steg_favicon.py encode file-to-hide-data-in.png text-file.txt
        
    This will output a file named hidden.png in the same folder
    as the python script.
        
    To recover an image:
    ====================
        > python steg_favicon.py decode file-with-hidden-text.png

    This will print the text to the command line

    To test the both:
    =================
        > python steg_favicon.py test file-to-hide-data-in.png text-file.txt

    This will do encode followed by decode. Please check the output to the screen is
    what you expect.
    
    Usage
    =====
    
    Feel free to use and modify the script to make it better! If you have any 
    cool additions or bug fixes I'd love to know about them, so email me at 
    sarah@lowmanio.co.uk
    
"""

__author__ = 'Sarah Holmes <http://lowmanio.co.uk/>'

import sys
import png
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher(object):

    def __init__(self, key):
        self.bs = 16
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


def decode(line):
    new_line = []

    for x, p in enumerate(line):
        if x % 192 == 189:
            new_line.append(chr(p))
        elif x % 192 == 190:
            new_line.append(chr(p))
        elif x % 192 == 191:
            new_line.append(chr(p))
    return "".join(line for line in new_line)


def encode(line, hide_lines):
    new_line = line
    if hide_lines[0] is not None:
        new_line[-3] = hide_lines[0]
    if hide_lines[1] is not None:
        new_line[-2] = hide_lines[1]
    if hide_lines[2] is not None:
        new_line[-1] = hide_lines[2]
    return new_line


def hide_image(file, hiddenfile):
    """ Hides 'hiddenfile' within 'file' """
    
    im = png.Reader(filename=file)
    width, height, pixels, meta = im.read()

    pixelsHide = []
    with open(hiddenfile, 'r') as hidden:
        plain_text = hidden.read()
    cipher_text = cipher.encrypt(plain_text)
    for char in cipher_text:
        pixelsHide.append(ord(char))

    out_file = open('hidden.png', 'wb')
    
    # transform
    new_pixels = []
    for x, p in enumerate(pixels):
        try:
            first = pixelsHide[(x*3)]
        except IndexError:
            first = None
        try:
            second = pixelsHide[(x*3)+1]
        except IndexError:
            second = None
        try:
            third = pixelsHide[(x*3)+2]
        except IndexError:
            third = None
        new_pixels.append(encode(p, (first, second, third)))
    # output image
    writer = png.Writer(width=width, height=height, **meta)
    writer.write(out_file, new_pixels)


def reveal_image(file):
    """ Reveals an image hidden within 'file' """
    
    # input image
    im = png.Reader(filename=file)
    width, height, pixels, meta = im.read()

    # transform
    output = "".join([decode(line) for line in pixels])
    print cipher.decrypt(output)

cipher = AESCipher("7BoxG9Sv^U4VqDGS7lGQ")

def main():

    try:
        if sys.argv[1] == "encode":
            try:
                hide_image(sys.argv[2], sys.argv[3])
            except IndexError:
                print "Please supply two files. The first is the PNG file the image will be hidden in, " \
                      "the second is the text file to hide."
        elif sys.argv[1] == "decode":
            try:
                reveal_image(sys.argv[2])
            except IndexError:
                print "Please supply a PNG with hidden text."
        elif sys.argv[1] == "test":
            hide_image(sys.argv[2], sys.argv[3])
            reveal_image('hidden.png')
        else:
            print "invalid argument. Please use 'encode' or 'decode'"
    except IndexError:
        print "Please type 'encode', 'decode' or 'test' after the python file followed by one PNG and one text file " \
              "for encode and test, and one PNG file for decode. Test encodes and then decodes the results."
        
if __name__ == "__main__":
    main()

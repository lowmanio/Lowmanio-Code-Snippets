"""
	Copyright Sarah Lowman 2009.
	Feel free to use and modify this code, please give a mention to where 
	you got it from though :)
"""

# Mako code to display the Captcha image
# --------------------------------------

<% import time %>
<% img = "captcha" + str(time.time()) + ".jpg" %> # make a random URL for the image to stop the browser caching the image
<p>
	<img src="${urls.build('blog.generateCaptchaImage', dict(id=img))|h}" alt="captcha" title="captcha image" /> 
</p>

# Controller endpoint code for the image URL
# ------------------------------------------

def generateCaptchaImage(self, id):
	""" Generate a captcha. Store the word in self.captcha (the session) and return the image
		Ignores the image URL that gets passed in. """
		
	word, image = generateCaptcha() # method in captcha.py
	self.captcha = word # This is a property that gets and sets the session so that the user's input can be compared 
	return Response(image, mimetype='image/jpeg')
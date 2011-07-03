"""
	Copyright Sarah Lowman 2009.
	Feel free to use and modify this code, please give a mention to where 
	you got it from though :)
"""

# In the Model
#-------------#

@staticmethod
def generateSpans():
	""" A static method inside the Tag or Blog Entry class, using SQLAlchemy.
		Returns a list of tag and normalised weight tuples where the most common 
		tags have vweight 1 and least common have weight 0.
	"""
	counts = session.query(Tag, 
		func.count(Tag.id)).join(blog_tags).group_by(Tag).all()
	
	smallest = min(count for (tag, count) in counts)
	scale = max(count for (tag, count) in counts) - smallest

	scaled = []
	for tag, count in counts:
		if scale != 0:
			scaled.append((tag, (count - smallest)/float(scale)))
		else:
			scaled.append((tag, 1))

	return scaled
	

# In the View
#------------#

	""" Using Mako templates. Goes through the tags and weights and adjusts the font size
	for that tag accordingly. Here the font ranges between 70% and 150% of the normal
	<p> font size 
	"""
<p>
% for tag, weight in tags:   # where tags is the returned value of generateSpans()
	<span style="font-size: ${int(70 + (80 * weight))|h}%">
		<a href="${tag.link|h}">${tag.name|h}</a>
	</span>
% endfor
</p>
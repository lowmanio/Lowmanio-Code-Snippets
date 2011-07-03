"""
	Copyright Sarah Lowman 2009.
	Feel free to use and modify this code, please give a mention to where 
	you got it from though :)
	
	You will need PostgreSQL 8.4 and the Python libraries of SQLAlchemy and 
	Mako (or your favourite templating library)  
"""

###############################################################################

"""
	To set up searching on one of your tables, add this to the model where your table classes are defined. 
	Alternatively if you have already set up your website, then type the SQL commands directly into PostgreSQL. 
	The table I have used here is called blog_entries with associated class Blog, and the columns that will 
	be searched on are contents and title. 
"""

def setup_search(event, schema_item, bind):
    """ Automatically run when SQLAlchemy creates the tables by running Base.metadata.create_all(bind=db) """
    
    # We don't want sqlalchemy to know about this column so we add it externally.
    bind.execute("alter table blog_entries add column search_vector tsvector")
    # This indexes the tsvector column
    bind.execute("create index blog_entries_search_index on blog_entries using gin(search_vector)")
    # This sets up the trigger that keeps the tsvector column up to date.
    bind.execute("""create trigger blog_entry_search_update before update or insert on blog_entries
                    for each row execute procedure
                    tsvector_update_trigger('search_vector', 'pg_catalog.english', 'contents', 'title')""")

# We want to call setup_search after the blog_entries has been created.
Blog.__table__.append_ddl_listener('after-create', setup_search)

###############################################################################

"""
	Add this method to the class you are searching on, in my case Blog:
"""

@staticmethod
def search(searchterms):
	""" Given the user's input, returns a list of 3-tuples: blog post object, 
	a list of fragments containing search terms with <span class="highlight"></span>
	around the search terms and the blog title also containing <span class="highlight">
	</span> around each search term. """
	
	# search_vector is a ts_vector column. To search for terms, you use the @@ operator.
	# plainto_tsquery turns a string into a query that can be used with @@
	# So this adds a where clause like "WHERE search_vector @@ plaint_tsquery(<search string>)"
	q = session.query(Blog).filter('blog_entries.search_vector @@ plainto_tsquery(:terms)')
	
	# This binds the :terms placeholder to the searchterms string. User input should always
	# be put into queries this way to prevent SQL injection.
	q = q.params(terms=searchterms)
	
	# This adds an extra column that is the blog contents made into a "headline" (bunch of
	# fragments) using the postgresql function ts_headline. The 4th argument is a string
	# giving options to the function. StartSel and StopSel give the strings the search
	# terms will be highlighted with. MaxFragments gives the maximum number of fragments
	# returned and FragmentDelimiter give a string that will separate the fragments. We
	# use this to split the fragments into a list later.
	q = q.add_column(func.ts_headline('pg_catalog.english', Blog.contents, 
									  func.plainto_tsquery(searchterms),
									  'MaxFragments=5,FragmentDelimiter=|||,'\
									   'StartSel="<span class=""highlight"">", StopSel = "</span>", ',
									  type_=Unicode))
	
	# This is very similar to above, only instead of using fragments, we pass the option
	# HighlightAll=TRUE which means the whole field (Blog.title) will be returned with highlighting
	# instead of a section of the title.
	q = q.add_column(func.ts_headline('pg_catalog.english', Blog.title, 
									  func.plainto_tsquery(searchterms),
									  'HighlightAll=TRUE, StartSel="<span class=""highlight"">", '\
									  'StopSel = "</span>"',
									  type_=Unicode))
   
	# This calls ts_rank_cd with the search_vector and the query and gives a ranking to each
	# row. We order by this descending. Again, the :terms placeholder is used to insert
	# user input.
	q = q.order_by('ts_rank_cd(blog_entries.search_vector, plainto_tsquery(:terms)) DESC')

	# Because of the two add_column calls above, the query will return a 3-tuple
	# consisting of the actual entry objects, the fragments for the contents and
	# the highlighted headline. In order to make the fragments a list, we split them
	# on '|||' - the FragmentDelimiter.
	return [(entry, fragments.split('|||'), title) for entry, fragments, title in q]
	
###############################################################################

"""
	In your template you will want to do something like this (using Mako here):
"""

	<h2>Search Results</h2>
	<p>You searched for: <b>${searchterms|h}</b> and got <b>${len(results)|h} results</b></p>

% for blogpost in results:
		<% blog, fragments, title = blogpost %>
		<h2>${title}</h2>
			% for frag in fragments:
				<p>&hellip; ${frag} &hellip;</p>
			% endfor
% endfor
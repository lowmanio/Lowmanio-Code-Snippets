"""
	Copyright Sarah Lowman 2009.
	Feel free to use and modify this code, please give a mention to where 
	you got it from though :)
	
    A Python script to put all your songs in a database and produce a simple HTML page of them
    
    To run:
        python music.py
        
    Before you run: 
        Please put this script in your 'My Music' directory. This script assumes you are running 
        Windows and have let Windows Media Player organise your 'My Music' directory into 
        Artists > Albums > Songs. The script will generate a music.html file in the 'My Music' folder.
    
        You will need to have access to a database, for example Postgres or SQLite. SQLite comes with 
        Python 2.5, so use this if you have no database available. In that case, replace with:
            engine = create_engine('sqlite:///:memory:', echo=False)
        Otherwise, please replace with the username, password, port, database etc of your DB. 
        
        Update music_exts and image_exts to your needs 
        Replace the ignorables list with folders you wish the script to ignore.
"""

# imports
## easy_install SQLAlchemy ##
from sqlalchemy import Table, Column, Integer, Unicode, MetaData, ForeignKey, create_engine, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relation, sessionmaker

## http://code.google.com/p/mutagen/ ##
from mutagen.mp3 import MP3

import codecs
import os
import cgi
import sys
import string

Base = declarative_base()   # Classes representing tables inherit from this

music_exts = set(['.mp3', '.wma', '.m4a'])          # all your music extensions to hunt for
image_exts = set(['.jpg', '.png', '.jpeg', '.bmp']) # the album images to hunt for. Windows creates a hidden AlbumArtSmall.jpg if you use Windows Media Player

ignorables = set(['iTunes', 'My Playlists', 'Downloads', 'Incomplete'])   # folders you don't want to look in

artists = {}        # dictionary of artists with value being a list of album names
album_images = {}   # dictionary of (artist, album) tuples with image paths as values

engine = create_engine('postgres://username:password@localhost:port/database', echo=False) # connect to database. set echo to True if you want to see all the SQL being spit out in console
Session = sessionmaker(bind=engine) # make session and bind to db
session = Session()

"""
    Classes to represent an artist, album and song respectively
    __tablename__ is the name of the corresponding table in the database
"""
class Artist(Base):
    __tablename__ = 'music_artist'
    
    id = Column(Integer, primary_key = True)
    name = Column(Unicode)

    def __init__(self, artist):
		self.name = artist
        
    def __repr__(self):
        return "Artist Obj['%s']" % self.name

class Album(Base):
    __tablename__ = 'music_album'
    
    id = Column(Integer, primary_key = True)
    name = Column(Unicode)
    image = Column(Unicode)
    artistid = Column(Integer, ForeignKey('music_artist.id'))
	
    artist = relation('Artist', backref=backref('albums'))
	
    def __init__(self, album, artist, image=None):
        self.name = album
        if image:
            self.image = image
        self.artist = artist
        
    def __repr__(self):
        if self.image:
            return "Album Obj['%s by %s (%s)']" % (self.name, self.artist.name, self.image)
        else:
            return "Album Obj['%s by %s']" % (self.name, self.artist.name)
		
class Song(Base):
    __tablename__ = 'music_song'
    
    id = Column(Integer, primary_key = True)
    name = Column(Unicode)
    albumid = Column(Integer, ForeignKey('music_album.id'))
    genre = Column(Unicode)
    length = Column(Float)
    track_number = Column(Integer, default=0)
    composer = Column(Unicode)
    type = Column(Unicode)
    
    album = relation('Album', backref=backref('songs', order_by=track_number))
	
    def __init__(self, song, album):
        self.type = song.split('.')[-1]
        self.name = ".".join(song.split('.')[:-1])
        self.album = album
        
        self.reformat_name()
        
    def __repr__(self):
        return "Song Obj['%s from %s']" % (self.name, self.album.name)
        
    def reformat_name(self):
        """
            Gets rid of must of the track numbers and punctuation at the beginning of track names
        """
        artist = self.album.artist.name.lower()
        self.name = self.name.lower().replace(artist, "").strip() # get rid of the artists in the name
        self.name = self.name.replace("_", " ") # replace all _'s with spaces
        
        if self.name[0:2].isdigit(): # file starts with number e.g. 12 then get rid of it and any whitespace
            self.name = self.name[2:].strip()   
        
        while self.name[0] in [',' , '.' , '-']: # file now starts with a comma or full stop, get rid of it again
            self.name = self.name[1:].strip()  
        
        self.name = string.capwords(self.name)
        
    def replace_name(self, name):
        self.name = name
	
"""
    The function that steps through all the folders in your music directory and adds the artists, albums and songs to database
    This assumes this Python script is placed in the 'My Music' directory and this directory contains folders of artists,
    each containing folders of albums, each containing songs. 
"""	
def add_music_to_database():
    Base.metadata.drop_all(engine)      # delete old tables first 
    Base.metadata.create_all(engine)    # recreate tables

    music = os.walk(u'.')		

    for (dirpath, dirnames, filenames) in music:	# recursively go through each folder
        
        for i in xrange(len(dirnames) - 1, -1, -1): # don't want to go down folders we have put in ignorables
            if dirnames[i] in ignorables:           # so go through list backgrounds and delete these
                del dirnames[i]

        for f in filenames:
            try:
                _, artist, album = dirpath.split(os.sep)    # split the directory path 
                if artist not in artists:   # add to dictionary and database
                    artists[artist] = []
                    a = Artist(artist)
                    session.add(a)
                    session.commit() 
                else:
                    a = session.query(Artist).filter_by(name=artist).first()
                if album not in artists[artist]: # add to list and database
                    artists[artist].append(album)
                    alb = Album(album, a)
                    session.add(alb)
                    session.commit() 
                else:
                    alb = session.query(Album).filter_by(name=album, artist=a).first()
            except ValueError:
                continue
                
            ext = os.path.splitext(f)[1].lower()    # get the extension of the file
            
            if ext in music_exts:   # found music! Add to database
                m = Song(f, alb)
                genre = None
                length = None
                track_number = None
                composer = None
                name = None
                
                if ext.lower() == ".mp3":
                    try:
                        meta = MP3(os.path.join(dirpath, f))
                        genre = meta.tags['TCON'].text[0]   # get the genre
                        length = meta.info.length           # get track length
                        track_number = meta.tags['TRCK'][0] # get track number
                        composer = meta.tags['TCOM'][0]     # get the composer
                        name = m.tags['TIT2'][0]            # get track name
                    except:
                        pass #print sys.exc_info()

                session.add(m)
                if genre:
                    m.genre = genre
                if length:
                    m.length = length
                if track_number:
                    m.track_number = track_number
                if composer:
                    m.composer = composer
                if name:
                    m.replace_name(name)
                session.commit() 
                
            elif ext in image_exts: # found image! Link to album 
                if (artist, album) not in album_images:
                    album_images[(artist, album)] = f
                    q = session.query(Album).filter_by(name=album, artist=a).first()
                    if q is not None:
                        q.image = os.path.join(dirpath, f)
            else:
                continue
    
    session.commit() 

"""
    Generates a very basic HTML file that lists all your artists, albums (with images) and songs called
    music.html
"""
def generate_html_file():
    filename = "music.html"    
    
    a = session.query(Artist).all()
    albumcount = session.query(Album).count()
    songcount = session.query(Song).count()
    
    f = codecs.open(filename, 'w', 'utf-8')
    f.write('<html>\n\t<head>\n\t\t<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n\t</head>\n\n<body>')
    f.write('\n<h1>Music collection</h1>')
    f.write('\n<p> %s albums and %s songs </p>' % (albumcount, songcount))
    for artist in a:
        f.write('\n<h2>%s</h2>' % cgi.escape(artist.name)) # escape any < > or & for example
        for album in artist.albums:
            f.write('\n\t<h3>%s</h3>' % cgi.escape(album.name))
            if album.image:
                f.write('\n\t<img src="%s" width="75px" />'% cgi.escape(album.image))
            f.write('\n\t<ul>')
            for song in album.songs:
                tn = ""
                if song.track_number != 0:
                    tn = str(song.track_number)
                f.write('\n\t\t<li>%s %s %s</li>' % (tn, cgi.escape(song.name), maketime(song.length)))
            f.write('\n\t</ul>')
    f.write('\n</body>\n</html>')
    f.close()

"""
    length of song given in seconds, convert to [minutes:seconds]
"""    
def maketime(length):
    if length:
        minutes = str(int(length/60))
        seconds = str(int(length%60))
        if len(seconds) == 1:
            seconds = "0" + seconds
        return "[" + minutes + ":" + seconds + "]"
    else:
        return ""
   
"""
    Starting point of code
    Populates database then generates an HTML file
"""
if __name__ == "__main__":
    add_music_to_database()
    generate_html_file()

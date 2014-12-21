#!/usr/bin/env python

# sync.py is an interactive command line interface for syncing music from Rdio.
#
# (c) 2014 Kenneth Leftin
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import unicode_literals
import sys,os.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import copy
import argparse

from python.rdio import Rdio

from rdio_consumer_credentials import RDIO_CREDENTIALS
from rdio_consumer_credentials import TOKEN
try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

# Fix for Python 2.X
try:
    input = raw_input
except NameError:
    pass

# Number of albums to fetch from Rdio in one request.
PAGE_SIZE = 100

# Number of albums to show on a single page in the interactive terminal.
MAX_ALBUMS = 50

def main(argv):
  """Runs the main program.

  Intializes the Rdio connection and begins the prompt.
  """

  parser = argparse.ArgumentParser(description='Interactive command line interface for syncing music from Rdio.')
  parser.add_argument('--fetch_token', action='store_true', default=False, help='Fetch a fresh OAuth token. If not provided, will expect TOKEN to be defined in rdio_consumer_credentials.py')
  parser.add_argument('--fake', action='store_true', default=False, help='Use a fake set of albums. (For testing only)')
  args = parser.parse_args()
  if args.fetch_token:
    rdio = fetchRdioWithToken()
  else:
    rdio = Rdio(RDIO_CREDENTIALS, TOKEN)

  if args.fake:
    albums = fakeAlbums()
  else:
    albums = fetchAllAlbums(rdio)

  sync = Sync(rdio, albums)
  sync.prompt()

def fetchRdioWithToken():
  """Initialized Rdio with a token."""

  rdio = Rdio(RDIO_CREDENTIALS)
  url = rdio.begin_authentication('oob')
  print('Go to: ' + url)
  verifier = input('Then enter the code: ').strip()
  rdio.complete_authentication(verifier)
  return rdio

def fetchAllAlbums(rdio):
  """Fetches albums for a user."""
  albums = []
  c = 0
  while 1:
    print "Fetching Albums..."
    resultList = rdio.call('getFavorites', {'types': 'tracksAndAlbums', 'start': str(c), 'count': str(PAGE_SIZE)})['result']
    if len(resultList) > 0:
      for result in resultList:
        c += 1
        if result['type'] != 'a' or not result['canTether'] or not result['canStream'] or not result['canSample']:
          continue
        result['offline'] = False
        albums.append(result)
    else:
      break

  c = 0
  while 1:
    print "Fetching Offline Tracks..."
    resultList = rdio.call('getSynced', {'type': 'tracksAndAlbums', 'start': str(c), 'count': str(PAGE_SIZE)})['result']
    if len(resultList) > 0:
      for result in resultList:
        c += 1
        if result['type'] != 'a':
          continue
        for album in albums:
          if album['key'] == result['key']:
            album['offline'] = True
    else:
      break

  return albums

# Album dict schema: http://www.rdio.com/developers/docs/web-service/types/album/ref-web-service-type-album
class Sync:
  """Class which holds state for syncing.

  Holds a connection to Rdio and a mutable list of albums.

  Attributes:
    rdio: A connection to Rdio.
    albums: A list of albums. The offline bit on each album may be mutated.
    oldAlbums: A list of albums which should remain constant until after syncing.
        This is used for diffing the mutated albums for syncing.
    filterString: If set, will prompt() will only show albums or artists that
        match this string.
    offset: The page we are on. For example, '50' starts at the 50th element.
    
  """

  def __init__(self, rdio, albums):
    self.rdio = rdio
    self.albums = albums
    self.oldAlbums = copy.deepcopy(albums)
    self.filterString = ''
    self.offset = 0

  def getAlbumView(self):
    filteredAlbums = self.albums
    if self.filterString != '':
      filteredAlbums = filter(lambda a: (self.filterString in a['name']) or (self.filterString in a['artist']), self.albums)
    return filteredAlbums[self.offset:(MAX_ALBUMS + self.offset)]

  def getTotalItemsWithFilter(self):
    filteredAlbums = self.albums
    if self.filterString != '':
      filteredAlbums = filter(lambda a: (self.filterString in a['name']) or (self.filterString in a['artist']), self.albums)
    return len(filteredAlbums)

  def prompt(self):
    """Prompts the user to select from a list of albums"""

    selectChar = ' '
    for idx, album in enumerate(self.getAlbumView()):
      if album['offline']:
        selectChar = 'x'
      else:
        selectChar = ' '
      print '{0}. [{1}] {2} - {3}'.format(str(idx), selectChar, album['artist'], album['name'])

    totalSynced = len(filter(lambda album: album['offline'], self.albums))
    len(filter(lambda album: album['offline'], self.albums))
    print 'Showing {0}-{1} of {2}. Albums Synced: {3}.'.format(
      str(self.offset),
      str(min(self.getTotalItemsWithFilter(), self.offset + MAX_ALBUMS)),
      self.getTotalItemsWithFilter(),
      totalSynced)
    self.handleInput(raw_input('Toggle Album. Or [\'(a)ll\', \'(c)lear\', \'(n)ext\', \'(p)rev\', \'(f)ilter\', \'(s)ort\', \'sync\'] --> '))

  def handleInput(self, input):
    """Handles the input from the prompt"""
    
    if input == 'q':
      quit()
    elif input == 'sort' or input == 's':
      self.sort()
    elif input == 'sync':
      self.sync()
    elif input == 'filter' or input == 'f':
      self.filter()
    elif input == 'next' or input == 'n':
      self.next()
    elif input == 'prev' or input == 'p':
      self.prev()
    elif input == 'clear' or input == 'c':
      for album in self.getAlbumView():
        album['offline'] = False
    elif input == 'all' or input == 'a':
      for album in self.getAlbumView():
        album['offline'] = True
    elif input.isdigit():
      # Toggle selected album.
      idx = int(input)
      if idx < len(self.getAlbumView()):
        album = self.getAlbumView()[idx]
        album['offline'] = not album['offline']
    else:
      print "Unrecognized Input.\n"
    self.prompt()

  def filter(self):
    # Reset offset
    self.offset = 0
    input = raw_input('Enter filter string --> ')
    self.filterString = input

  def next(self):
    self.offset += MAX_ALBUMS
    if self.offset > self.getTotalItemsWithFilter():
      self.offset -= MAX_ALBUMS

  def prev(self):
    self.offset -= MAX_ALBUMS
    if self.offset < 0:
      self.offset = 0

  def sort(self):
    # Reset offset and filterString
    self.offset = 0
    self.filterString = ''
    input = raw_input('[album, artist] --> ')
    if input == 'artist':
      self.albums = sorted(self.albums, key=lambda album: album['artist'])
    elif input == 'album':
      self.albums = sorted(self.albums, key=lambda album: album['name'])
    else:
      print "Unrecognized Input.\n"

  def sync(self):
    """Syncs to Rdio"""
    
    toAdd = []
    toRemove = []

    # Creates the toAdd and toRemove list by intersecting oldAlbums with albums.
    #
    # Probably some clever way to do this with list comprehensions, functional programming
    # or sets.
    for album in self.albums:
      for oldAlbum in self.oldAlbums:
        if album['key'] == oldAlbum['key']:
          if album['offline'] and not oldAlbum['offline']:
            toAdd.append(album)
          elif not album['offline'] and oldAlbum['offline']:
            toRemove.append(album)

    # Final prompt with summary.
    input = raw_input('Adding {0} albums. Removing {1} albums. Ready to sync? [y/n] --> '.format(len(toAdd), len(toRemove)))
    if (input.lower() != 'y' and input.lower() != 'yes'):
      return

    # Actually do the syncing.
    print "Syncing..."
    if len(toRemove) > 0:
      print self.rdio.call('removeFromSynced', {'keys': ','.join([album['key'] for album in toRemove])})
    if len(toAdd) > 0:
      print self.rdio.call('addToSynced', {'keys': ','.join([album['key'] for album in toAdd])})

    # Now albums is exactly oldAlbums to start the process all over agin.
    self.oldAlbums = copy.deepcopy(self.albums)
    print "Done."

def fakeAlbums():
  """Provides a set of fake albums used for testing"""

  albums = [];
  albums.append({'key': '1', 'name': 'Selling England by the Pound', 'artist': 'Genesis', 'offline': False})
  albums.append({'key': '2', 'name': 'Foxtrot', 'artist': 'Genesis', 'offline': False})
  albums.append({'key': '3', 'name': 'Word of Mouth', 'artist': 'The Kinks', 'offline': True})
  albums.append({'key': '4', 'name': 'Wish You Were Here', 'artist': 'Pink Floyd', 'offline': False})
  albums.append({'key': '5', 'name': 'Wishbone Ash', 'artist': 'Wishbone Ash', 'offline': True})
  return albums

if __name__ == "__main__":
   main(sys.argv[1:])

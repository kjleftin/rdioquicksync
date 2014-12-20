#!/usr/bin/env python

from __future__ import unicode_literals

import sys,os.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pprint

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

pp = pprint.PrettyPrinter(depth=6)

    # create an instance of the Rdio object with our consumer credentials
rdio = Rdio(RDIO_CREDENTIALS, TOKEN)

# try:
#   # authenticate against the Rdio service
#   url = rdio.begin_authentication('oob')
#   print('Go to: ' + url)
#   verifier = input('Then enter the code: ').strip()
#   rdio.complete_authentication(verifier)

#   print rdio.token

#   # find out what playlists you created
#   myPlaylists = rdio.call('getPlaylists')['result']['owned']

#   # list them
#   for playlist in myPlaylists:
#     print('%(shortUrl)s\t%(name)s' % playlist)
# except HTTPError as e:
#   # if we have a protocol error, print it
#   print(e.read())


# userid = rdio.call('findUser', {'email': 'kjleftin@gmail.com'})['result']['key']
# print userid
#pp.pprint(rdio.call('getOfflineTracks')['result']);

def fakeAlbums():
  albums = [];
  albums.append({'name': 'Selling England by the Pound', 'artist': 'Genesis'})
  albums.append({'name': 'Foxtrot', 'artist': 'Genesis'})
  albums.append({'name': 'Word of Mouth', 'artist': 'The Kinks', 'offline': True})
  albums.append({'name': 'Wish You Were Here', 'artist': 'Pink Floyd'})
  albums.append({'name': 'Wishbone Ash', 'artist': 'Wishbone Ash', 'offline': True})
  return albums

def fetchAllAlbums():
  albums = []
  c = 0
  while 1:
    print c
    resultList = rdio.call('getAlbumsInCollection', {'start': str(c), 'count': str(50)})['result']
    print "Fetching: " + str(c) + " to " + str(c + 50)
    if len(resultList) > 0:
      print "Found " + str(len(resultList)) + " results."
      for result in resultList:
        c += 1
        albums.append({'name': result['name'], 'artist': result['artist']})
    else:
      break

  offlineAlbums = []
  c = 0
  while 1:
    print c
    resultList = rdio.call('getOfflineTracks', {'start': str(c), 'count': str(50)})['result']
    if len(resultList) > 0:
      for result in resultList:
        c += 1
        val = {'name': result['name'], 'artist': result['artist']};
        if val not in offlineAlbums:
          offlineAlbums.append(val)
    else:
      break

  for album in albums:
    if album in offlineAlbums:
      album['offline'] = True
  return albums

class Sync:
  def __init__(self, rdio, albums):
    self.rdio = rdio
    self.albums = albums

  def prompt(self):
    albumsSynced = 0
    selectChar = ' '
    for idx, album in enumerate(self.albums):
      if (('offline' in album) and album['offline']):
        albumsSynced += 1
        selectChar = 'x'
      else:
        selectChar = ' '
      print '{0}. [{1}] {2} - {3}'.format(str(idx), selectChar, album['name'], album['artist'])
    print 'Albums Synced: {0}. Total Albums {1}.'.format(albumsSynced, len(self.albums))
    self.handleInput(raw_input('Toggle Album. Or [\'next\', \'prev\', \'filter\', \'sort\', \'sync\'] --> '))

  def handleInput(self, input):
    if input == 'q':
      quit()
    elif input == 'sort':
      self.sort()
    elif input == 'sync':
      self.sync()
    elif input == 'filter':
      self.filter()
    elif input == 'next':
      self.next()
    elif input == 'prev':
      self.next()
    elif input.isdigit():
      # Toggle selected album.
      idx = int(input)
      album = self.albums[idx]
      isOffline = False
      if ('offline' in album) and album['offline']:
        isOffline = True
      album['offline'] = not isOffline
    else:
      print "Unrecognized Input."
    self.prompt()

  def filter(self):
    print "Not implemented yet."

  def next(self):
    print "Not implemented yet."

  def prev(self):
    print "Not implemented yet."

  def sort(self):
    input = raw_input('[album, artist] --> ')
    if input == 'artist':
      self.albums = sorted(self.albums, key=lambda album: album['artist'])
    elif input == 'album':
      self.albums = sorted(self.albums, key=lambda album: album['name'])
    else:
      print "Unrecognized Input."

  def sync(self):
    print 'TODO(kjleftin): Implement.'

sync = Sync(rdio, fakeAlbums())
sync.prompt()

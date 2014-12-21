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
  albums.append({'name': 'Selling England by the Pound', 'artist': 'Genesis', 'offline': False})
  albums.append({'name': 'Foxtrot', 'artist': 'Genesis', 'offline': False})
  albums.append({'name': 'Word of Mouth', 'artist': 'The Kinks', 'offline': True})
  albums.append({'name': 'Wish You Were Here', 'artist': 'Pink Floyd', 'offline': False})
  albums.append({'name': 'Wishbone Ash', 'artist': 'Wishbone Ash', 'offline': True})
  return albums

def fetchAllAlbums():
  PAGE_SIZE = 100

  albums = []
  c = 0
  while 1:
    print "Fetching Albums..."
    resultList = rdio.call('getAlbumsInCollection', {'start': str(c), 'count': str(PAGE_SIZE)})['result']
    if len(resultList) > 0:
      for result in resultList:
        c += 1
        albums.append({'name': result['name'], 'artist': result['artist'], 'offline': False})
    else:
      break

  offlineAlbums = []
  c = 0
  while 1:
    print "Fetching Offline Tracks..."
    resultList = rdio.call('getOfflineTracks', {'start': str(c), 'count': str(PAGE_SIZE)})['result']
    if len(resultList) > 0:
      for result in resultList:
        c += 1
        val = {'name': result['name'], 'artist': result['artist']};
        if val not in offlineAlbums:
          offlineAlbums.append(val)
    else:
      break

  for album in albums:
    for offlineAlbum in offlineAlbums:
      if album['name'] == offlineAlbum['name'] and album['artist'] == offlineAlbum['artist']:
        album['offline'] = True
  return albums

class Sync:
  MAX_ALBUMS = 50

  def __init__(self, rdio, albums):
    self.rdio = rdio
    self.albums = albums
    self.filterString = ''
    self.offset = 0

  def getAlbumView(self):
    filteredAlbums = self.albums
    if self.filterString != '':
      filteredAlbums = filter(lambda a: (self.filterString in a['name']) or (self.filterString in a['artist']), self.albums)
    return filteredAlbums[self.offset:(Sync.MAX_ALBUMS + self.offset)]

  def getTotalItemsWithFilter(self):
    filteredAlbums = self.albums
    if self.filterString != '':
      filteredAlbums = filter(lambda a: (self.filterString in a['name']) or (self.filterString in a['artist']), self.albums)
    return len(filteredAlbums)

  def prompt(self):
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
      str(min(self.getTotalItemsWithFilter(), self.offset + Sync.MAX_ALBUMS)),
      self.getTotalItemsWithFilter(),
      totalSynced)
    self.handleInput(raw_input('Toggle Album. Or [\'(a)ll\', \'(c)lear\', \'(n)ext\', \'(p)rev\', \'(f)ilter\', \'(s)ort\', \'sync\'] --> '))

  def handleInput(self, input):
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
      album = self.getAlbumView()[idx]
      isOffline = False
      if ('offline' in album) and album['offline']:
        isOffline = True
      album['offline'] = not isOffline
    else:
      print "Unrecognized Input.\n"
    self.prompt()

  def filter(self):
    # Reset offset
    self.offset = 0
    input = raw_input('Enter filter string --> ')
    self.filterString = input

  def next(self):
    self.offset += Sync.MAX_ALBUMS
    if self.offset > self.getTotalItemsWithFilter():
      self.offset -= Sync.MAX_ALBUMS

  def prev(self):
    self.offset -= Sync.MAX_ALBUMS
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
    print 'Not Implemented yet.\n'

sync = Sync(rdio, fakeAlbums())
sync.prompt()

#!/usr/bin/env python

from __future__ import unicode_literals

import sys,os.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pprint
import copy

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
  albums.append({'key': '1', 'name': 'Selling England by the Pound', 'artist': 'Genesis', 'offline': False})
  albums.append({'key': '2', 'name': 'Foxtrot', 'artist': 'Genesis', 'offline': False})
  albums.append({'key': '3', 'name': 'Word of Mouth', 'artist': 'The Kinks', 'offline': True})
  albums.append({'key': '4', 'name': 'Wish You Were Here', 'artist': 'Pink Floyd', 'offline': False})
  albums.append({'key': '5', 'name': 'Wishbone Ash', 'artist': 'Wishbone Ash', 'offline': True})
  return albums

def fetchAllAlbums():
  PAGE_SIZE = 100

  albums = []
  c = 0
  while 1:
    print "Fetching Albums..."
    resultList = rdio.call('getFavorites', {'types': 'tracksAndAlbums', 'start': str(c), 'count': str(PAGE_SIZE)})['result']
    if len(resultList) > 0:
      for result in resultList:
        c += 1
        if result['type'] != 'a':
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

class Sync:
  MAX_ALBUMS = 50

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

sync = Sync(rdio, fetchAllAlbums())
sync.prompt()

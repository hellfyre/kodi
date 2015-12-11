import xbmc
import xbmcaddon
import socket
import time
import threading
import errno
import re

addon = xbmcaddon.Addon(id='service.knock')
icon = addon.getAddonInfo('icon')

class KnockThread (threading.Thread):

  def __init__(self):
    super(KnockThread, self).__init__()
    self.server_name = addon.getSetting('server_name')
    self.server_address = addon.getSetting('server_address')
    self.server_port = int(addon.getSetting('server_port'))
    self.counter = int(addon.getSetting('interval'))
    self.access_refused = True
    
    sequence = addon.getSetting('sequence')
    separator = None
    for char in list(sequence):
        if(re.search(r'[0-9]', char) == None):
            separator = char
    if(separator):
        self.sequence = str.split(sequence, separator)
    else:
        self.sequence = [sequence]
    
    #xbmc.executebuiltin('xbmc.Notification(%s, %s, 3000, %s)' % (self.server_name, 'Plugin loaded', icon))

  def run(self):
    
    while(not xbmc.abortRequested):
      if(self.counter == 120):
        self.counter = 0
        while not self.cupcake_reachable():
          self.access_refused = True
          xbmc.executebuiltin('xbmc.Notification(%s, %s, 3000, %s)' % (self.server_name, 'Knocking...', icon))
          self.knock()
          time.sleep(10)
        self.loginfo('I have access to cupcake')
        if self.access_refused:
          xbmc.executebuiltin('xbmc.Notification(%s, %s, 3000, %s)' % (self.server_name, 'Open sesame :)', icon))
          self.access_refused = False

      time.sleep(1)
      self.counter += 1

  def cupcake_reachable(self):
    self.logdebug('Trying to reach cupcake...')
    try:
      self.sock = socket.socket()
      self.sock.settimeout(10.0)
      self.sock.connect((self.server_address, self.server_port))
    except:
      self.sock.close()
      self.logdebug('cupcake_reachable: False')
      return False
    self.logdebug('cupcake_reachable: True')
    return True

  def knock(self):
    self.loginfo('Knocking...')
    for port in self.sequence:
      try:
        self.sock = socket.socket()
        self.sock.connect((self.server_address, port))
      except socket.error as e:
        if e.errno == errno.ECONNREFUSED:
          self.logdebug('Knocking on ' + self.server_address + ':' + str(port))
        else:
          self.loginfo('Could not connect to ' + self.server_address + ':' + str(port))
        self.sock.close()

  def loginfo(self, msg):
    xbmc.log('Knocking client: ' + msg, xbmc.LOGINFO)

  def logdebug(self, msg):
    xbmc.log('Knocking client: ' + msg, xbmc.LOGDEBUG)


knockThread = KnockThread()
knockThread.start()

while (not xbmc.abortRequested):
  time.sleep(2)

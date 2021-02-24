#!/usr/bin/env python

import sys
import os
import psutil
import atexit
import dbus
import gi.repository.GLib
from dbus.mainloop.glib import DBusGMainLoop
from notify import notification

def mute():
    os.system('pactl set-sink-mute @DEFAULT_SINK@ 1')

def unmute():
    os.system('pactl set-sink-mute @DEFAULT_SINK@ 0')

# Restore the system volume after exiting
atexit.register(unmute)

# Exit if Spotify is not running
def exit_if_no_spotify():
    for runningProcess in psutil.process_iter(['name']):
        if runningProcess.name() == 'spotify':
            return True

    print("Spotify not found, exiting")
    sys.exit(0)

exit_if_no_spotify()

# Connect to the Spotify DBus interface
DBusGMainLoop(set_as_default = True)
bus = dbus.SessionBus()
spotify_bus = bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')
spotify_properties = dbus.Interface(spotify_bus, 'org.freedesktop.DBus.Properties')

# This function will get called whenever the playing song changes
def properties_changed(bus, message, args):
    # Get the title and artist of the currently playing song to detect if the currently playing song is an ad
    metadata = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
    title = metadata['xesam:title']
    artist = metadata['xesam:artist'][0]

    if title == "Advertisement" and not artist:
        mute()
    else:
        unmute()

spotify_properties.connect_to_signal('PropertiesChanged', properties_changed)

# Run the GLib event loop to process DBus signals as they arrive
mainloop = gi.repository.GLib.MainLoop()
mainloop.run()
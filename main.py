#!/usr/bin/env python

import time
import sys
import os
import psutil
import atexit
import dbus
import gi.repository.GLib
import requests
from subprocess import check_output
from dbus.mainloop.glib import DBusGMainLoop
from subprocess import check_output



# Version check
current_version = 0.0
up_version = float(requests.get('https://raw.githubusercontent.com/XECortex/spotify-adeleminator/main/version').text)

print(f'Spotify AdEleminator v{current_version}by @XECortex')

if up_version > current_version:
    print('A new version of this software is available')
    print('Check out "https://github.com/XECortex/spotify-adeleminator"')



# Get the PulseAudio player ID of Spotify
def get_pulse_id():
    current_id = -1
    sink_list = check_output(['pacmd', 'list-sink-inputs']).splitlines()

    for line in sink_list:
        line = str(line).replace("b'", '').replace("'", '')
        
        if line.startswith('    index:'):
            current_id = line[11:]
        elif line.endswith('binary = "spotify"'):
            return current_id

    return False

while not get_pulse_id():
    print('Spotify is not running yet. Please open Spotify now and start playing a song')
    time.sleep(1)

pulse_id = get_pulse_id()

print('Spotify detected')
print('PulseAudio ID:', pulse_id)



# Mute and unmute Apotify through the PulseAudio player ID
def mute():
    os.system(f'pacmd set-sink-input-mute "{pulse_id}" 1')

def unmute():
    os.system(f'pacmd set-sink-input-mute "{pulse_id}" 0')

# Restore the volume after exiting
atexit.register(unmute)



# Connect to the Spotify DBus interface
print('Connecting to DBus interface...')

bus = dbus.SessionBus()
spotify_bus = bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')
spotify_properties = dbus.Interface(spotify_bus, 'org.freedesktop.DBus.Properties')

last_title = ""
last_artist = ""

print('Everything done! Spotify AdEleminator is now running and listening for ads!')

def song_changed(title, artist):
    print(title, '-', artist)

    if title in ['Advertisement', 'Ad', 'Spotify', 'spotify']: # and artist == '<Unknown>':
        mute()
    else:
        unmute()

while True:
    # Get the title and artist of the currently playing song to detect if the currently playing song is an ad
    metadata = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
    title = metadata['xesam:title'] if metadata['xesam:title'] else '<Unknown>'
    artist = metadata['xesam:artist'][0] if metadata['xesam:artist'][0] else '<Unknown>'

    if title != last_title or artist != last_artist:
        song_changed(title, artist)

    last_title = title
    last_artist = artist
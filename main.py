#!/usr/bin/env python

VERSION = 0.1

import time
import sys
import os
import atexit
import dbus
import gi.repository.GLib
import requests
import shutil
from subprocess import check_output
from dbus.mainloop.glib import DBusGMainLoop
from subprocess import check_output



#* Startup title and version check
up_version = float(requests.get('https://raw.githubusercontent.com/XECortex/spotify-adeleminator/main/version').text)

print('')
print('╭───────────────────────────╮')
print(f'│ \33[1m\33[92mSpotify AdEleminator\33[0m v{VERSION} │')
print('│ \33[3mby @XECortex\33[0m              │')
print('╰───────────────────────────╯')
print('')

if up_version > VERSION:
    print('\33[1m\33[91mA new version of this software is available on GitHub')
    print('Check out "\33[4mhttps://github.com/XECortex/spotify-adeleminator\33[0m\33[91m"\33[0m')
    print('')



#* Get the PulseAudio sink input ID of Spotify
def get_pulse_id():
    current_id = -1
    
    # Get a list of all available sink inputs by using pacmd
    sink_list = check_output(['pacmd', 'list-sink-inputs']).splitlines()

    # Disassemble the chaos and extract the ID we need
    for line in sink_list:
        line = str(line).replace("b'", '').replace("'", '')
        
        if line.startswith('    index:'):
            current_id = line[11:]
        #? We could also search for Spotify's PID here (but it's less performant as we need another for loop)
        elif line.endswith('binary = "spotify"'):
            return current_id

    return False

# If Spotify isn't open yet, wait for for the user to start it
if not get_pulse_id():
    print('\33[33m●\33[0m Spotify is not running yet. Please open Spotify and play a song', end='\r')

    while not get_pulse_id():
        time.sleep(1)

pulse_id = get_pulse_id()

print(' ' * os.get_terminal_size().columns, end='\r')
print('\33[92m●\33[0m Spotify detected')
print('PulseAudio sink input ID:', pulse_id)



#* Mute and unmute Spotify functions
def mute():
    os.system(f'pacmd set-sink-input-mute "{pulse_id}" 1')

def unmute():
    os.system(f'pacmd set-sink-input-mute "{pulse_id}" 0')

# Restore the volume after exiting
atexit.register(unmute)



#* Connect to the Spotify DBus interface
# TODO: Exit if DBus gets disconnected
print('Connecting to DBus interface...')

bus = dbus.SessionBus()
spotify_properties = dbus.Interface(bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2'), 'org.freedesktop.DBus.Properties')

last_title = ""
last_artist = ""

def song_changed(title, artist):
    if title in ['Advertisement', 'Ad', 'Spotify', 'spotify'] and artist == '<Unknown>':
        mute()
        is_ad = True
    else:
        unmute()
        is_ad = False
    
    print(' ' * os.get_terminal_size().columns, end='\r')
    print('▶', title, '-\33[3m', artist, '\33[0m\33[1m\33[31mAdvertisement detected, muting Spotify\33[0m' if is_ad else '\33[0m', end='\r')

#* Main loop
# FIXME: Exit script without any errors when Spotify is closed
print('\33[1mEverything done!\33[0m Spotify AdEleminator is now running and listening for ads!')
print('')
print('\33[1mPlaying:\33[0m')

while True:
    # Get the title and artist of the currently playing song to detect if the currently playing song is an ad
    metadata = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
    title = metadata['xesam:title'] if metadata['xesam:title'] else '<Unknown>'
    artist = metadata['xesam:artist'][0] if metadata['xesam:artist'][0] else '<Unknown>'

    if title != last_title or artist != last_artist:
        song_changed(title, artist)

    last_title = title
    last_artist = artist
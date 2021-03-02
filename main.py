#!/usr/bin/env python3

import time
import sys
import os
import atexit
import shutil
import psutil
from pynput import keyboard
from subprocess import check_output
import dbus
import requests

VERSION = 0.6

def _clear_line():
    print(' ' * os.get_terminal_size().columns, end='\r')

def _exit():
    _clear_line()
    print('\33[1m\33[31mSpotify closed\33[0m')
    time.sleep(1)
    print('\033[?25h')
    psutil.Process(os.getpid()).terminate()

def _is_window_focused():
    focused_id = int(check_output(['xdotool', 'getwindowfocus']).decode())
    window_list = check_output(['wmctrl', '-lp']).splitlines()
    pppid = check_output(['ps', '-p', str(os.getppid()), '-oppid=']).decode().strip()
    
    if pppid == '1':
        pppid = str(os.getppid())

    window_id = 0

    for line in window_list:
        line = line.decode()

        if len(line.replace(pppid, ' ')) < len(line):
            window_id = int(line[:10], 16)

    return window_id == focused_id



#* Startup title and version check
os.system('echo -en "\033]0;Spotify AdEleminator\a"')
os.system('stty -echo')
print('\033[?25l')

up_version = float(requests.get('https://raw.githubusercontent.com/XECortex/spotify-adeleminator/main/version').text)

print('╭───────────────────────────╮')
print(f'│ \33[1m\33[92mSpotify AdEleminator\33[0m v{VERSION} │')
print('│ \33[3mby @XECortex\33[0m              │')
print('╰───────────────────────────╯')
print('')

if up_version > VERSION:
    print('\33[1m\33[91mA new version of this software is available on GitHub')
    print('Check out "\33[4mhttps://github.com/XECortex/spotify-adeleminator\33[0m\33[91m"\33[0m')
    print('')



#* Close hotkey
def key_release(key):
    if key in [ keyboard.KeyCode(char='q'), keyboard.Key.esc ] and _is_window_focused():
        _exit()

listener = keyboard.Listener(on_release=key_release)
listener.start()



#* Get the PulseAudio sink input ID of Spotify
def get_pulse_id():
    current_id = -1
    
    # Get a list of all available sink inputs by using pactl
    sink_list = check_output(['pactl', 'list', 'sink-inputs']).splitlines()

    # Disassemble the chaos and extract the ID we need
    for line in sink_list:
        line = str(line.decode())
        
        if line.startswith('Sink Input #'):
            current_id = line[12:]
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

_clear_line()
print('\33[92m●\33[0m Spotify detected')
print('PulseAudio sink input ID:', pulse_id)



#* Mute and unmute Spotify functions
def mute():
    os.system(f'pactl set-sink-input-mute "{pulse_id}" 1')

def unmute():
    os.system(f'pactl set-sink-input-mute "{pulse_id}" 0')

# Restore the volume after exiting
atexit.register(unmute)



#* Connect to the Spotify DBus interface
print('Connecting to DBus interface...')

bus = dbus.SessionBus()
spotify_properties = dbus.Interface(bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2'), 'org.freedesktop.DBus.Properties')



#* Main loop
last_title = ""
last_artist = ""

def song_changed(title, artist):
    if title in ['Advertisement', 'Ad', 'Spotify', 'spotify'] and artist == '<Unknown>':
        mute()
        is_ad = True
    else:
        time.sleep(1)
        unmute()
        is_ad = False
    
    _clear_line()
    print('▶', title, '-\33[3m', artist, '\33[0m\33[1m\33[31mAdvertisement detected, muting Spotify\33[0m' if is_ad else '\33[0m', end='\r')

print('\33[92m●\33[0m \33[1mEverything done!\33[0m\nSpotify AdEleminator is now running to protect you from all the nasty ads!')
print('')
print('\33[1mPlaying:\33[0m')

while True:
    try:
        # Get the title and artist of the currently playing song to detect if it is an ad
        metadata = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
        title = metadata['xesam:title'] if metadata['xesam:title'] else '<Unknown>'
        artist = metadata['xesam:artist'][0] if metadata['xesam:artist'][0] else '<Unknown>'
    except dbus.exceptions.DBusException as exception:
        _exit()

    if title != last_title or artist != last_artist:
        song_changed(title, artist)

    last_title = title
    last_artist = artist
#!/usr/bin/env python3

VERSION = 1.2

import os
import termios
import sys
import traceback
import psutil
import threading
import argparse
import requests
import time
import dbus

from subprocess import check_output


#* Functions
#? Restore terminal settings
def exit_cleanup(noclear=False, noexit=False):
    os.system('stty echo')
    print('\033[?25h')
    termios.tcflush(sys.stdin, termios.TCIOFLUSH)

    if not noclear:
        os.system('clear')
    
    if not noexit:
        exit()


#? Get the width and height of the terminal
def get_termsize():
    return int(check_output(['stty', 'size']).split()[1])


#? Clear a previously with end='\r' printed line
def clear_line(newline=False, char=' '):
    print(char * get_termsize(), end='\r' if not newline else '\n')


#? Exception handler
def handle_exception(exception):
    exit_cleanup(noexit=True)

    print(f'\33[91m●\33[0m \33[1m\33[91mAn error occured:\33[0m {type(exception).__name__}')
    print_traceback = input('  Do you want to print the error message? [\33[1my\33[0mes/\33[1mn\33[0mo/with \33[1mt\33[0mraceback]: ')

    if print_traceback == 'y':
        print()
        print('>', exception)
    elif print_traceback == 't':
        clear_line(True, '~')
        print(traceback.print_exc())
    elif print_traceback != 'n':
        print('Invalid option')

    exit_cleanup(noclear=True)


#? Check if Spotify is opened
def spotify_running():
    # Iterate over every running application
    for p in psutil.process_iter(['name']):
        # Check if it is a Spotify instance
        if p.info['name'] == 'spotify':
            return True
    
    return False


#? Get the Pulse client ID of Spotify
def get_client_id():
    current_id = -1

    # Lists all sink-inputs
    sink_list = check_output(['pactl', 'list', 'sink-inputs']).splitlines()

    # Disassemble the chaos and extract what we need
    for line in sink_list:
        line = str(line.decode())
        
        if line.startswith('Sink Input #'):
            current_id = line[12:]
        elif line.endswith('binary = "spotify"'):
            return current_id

    return False


def mute(is_ad, client_id):
    # Wait a second after the ad ends as Spotify buffers audio that will play for a few more milliseconds
    if not is_ad:
        time.sleep(1)
    
    os.system(f'pactl set-sink-input-mute "{client_id}" {str(1 if is_ad else 0)}')


def truncate(s, length):
    if len(s) <= length:
        return s
    
    return s[:int(length - 1)] + '…'


def song_changed(title, artist, client_id):
    # Ad detection
    is_ad = (title == '<Unknown>' or title in ['Advertisement', 'Ad', 'Spotify', 'spotify']) and artist == '<Unknown>'

    # Mute the spotify application if an ad is playing
    threading.Thread(target=mute, args=(is_ad, client_id)).start()
    
    return truncate(f'▶ {title} - \33[3m{artist}\33[0m' if not is_ad else '▶ \33[91mAdvertisement\33[0m', get_termsize())


#* Init
# Argument parser
parser = argparse.ArgumentParser()

parser.add_argument('-a', '--autolaunch', action='store_true', help='launch Spotify on program start')
parser.add_argument('-l', '--loop', action='store_true', help='do not close with Spotify but wait for a new instance')

args = parser.parse_args()
autolaunch = args.autolaunch
loop = args.loop


#* Wrapper loop
first_run = True

try:
    while first_run or loop:
        # Set up terminal
        os.system('clear')
        os.system('echo -en "\033]0;Spotify AdEleminator\a"')

        # Disable user input and hide the cursor
        os.system('stty -echo')
        print('\033[?25l')

        # Startup title
        print('╭───────────────────────────╮')
        print(f'│ \33[1m\33[92mSpotify AdEleminator\33[0m v{VERSION} │')
        print('│ \33[3mby @XECortex\33[0m              │')
        print('╰───────────────────────────╯')
        print('')

        # Update checker
        # The latest version is stored on GitHub as a float number
        up_version = float(requests.get('https://raw.githubusercontent.com/XECortex/spotify-adeleminator/main/version').text[3:])

        # If the version on GitHub is newer than the installed, notify the user
        if up_version > VERSION:
            if first_run:
                os.system('notify-send "Spotify AdEleminator" "A new update is available on GitHub\nCheck out <tt>https://github.com/XECortex/spotify-adeleminator</tt>" -i spotify')

            print('\33[1m\33[91m●\33[0m A new update is available on GitHub!')
            print('  Check out \33[4mhttps://github.com/XECortex/spotify-adeleminator\33[0m')
            print('')

        # Detect Spotify
        if not spotify_running():
            # If Spotify isn't running yet and the user enabled autolaunch, launch Spotify
            if autolaunch and first_run:
                print('\33[33m○\33[0m Launching Spotify...', end='\r')
                os.system('spotify >/dev/null 2>&1 &') # Disable debug and error output and disown the process

                # Wait until Spotify is running
                while not spotify_running():
                    time.sleep(1)

        # Get the client ID
        if not get_client_id():
            clear_line()
            print('\33[33m○\33[0m Waiting for Spotify to start playing...', end='\r')

            while not get_client_id():
                time.sleep(1)

        client_id = get_client_id()

        clear_line()
        print(f'\33[92m●\33[0m Spotify detected\n  \33[90mPulse client ID: {client_id}\33[0m\n  \33[90mConnecting to DBus...\33[0m')

        # Connect to the DBus interface and get access to the properties of Spotify using mpris
        bus = dbus.SessionBus()
        spotify_properties = dbus.Interface(bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2'), 'org.freedesktop.DBus.Properties')


        #* Main loop
        last_title = ''
        last_artist = ''
        termsize = 0

        print('\33[92m●\33[0m Spotify AdEleminator is now ready')
        print('')
        print('  \33[1mPlaying:\33[0m')
        print('No data available', end='\r')

        while True:
            # Get information about the currently playing song from Spotify's DBus properties
            try:
                metadata = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
                title = metadata['xesam:title'] if metadata['xesam:title'] else '<Unknown>'
                artist = metadata['xesam:artist'][0] if metadata['xesam:artist'][0] else '<Unknown>'
                # print(metadata['mpris:artUrl'].replace('open.spotify.com', 'i.scdn.co'))
            except:
                break

            # Compare the old and new song information to check if the song has changed
            if title != last_title or artist != last_artist or get_termsize() != termsize:
                termsize = get_termsize()

                clear_line()
                print(song_changed(title, artist, client_id), end='\r')

            last_title = title
            last_artist = artist

        first_run = False

        clear_line()
        print('\33[91m●\33[0m Spotify closed')

        if not loop:
            break
except KeyboardInterrupt:
    False
except Exception as e:
    handle_exception(e)

time.sleep(1)
exit_cleanup()
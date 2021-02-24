#!/usr/bin/env python

import sys
import os
import psutil
import atexit
import dbus
import gi.repository.GLib
from subprocess import check_output
from dbus.mainloop.glib import DBusGMainLoop
from subprocess import check_output

# Exit if Spotify is not running
def exit_if_no_spotify():
    for runningProcess in psutil.process_iter(['name']):
        if runningProcess.name() == 'spotify':
            return True

    print("Spotify not found, exiting")
    sys.exit(0)

exit_if_no_spotify()
print('Spotify found!')

# Get the PulseAudio player ID of spotify
spotify_pid_list = str(check_output(['pidof', 'spotify'])).replace('\\n\'', '').replace('b\'', '').split(' ')
sink_list = check_output(['pacmd', 'list-sink-inputs'])

print('Spotify PIDs:', spotify_pid_list)

current_id = -1
spotify_id = -1

for line in sink_list.splitlines():
    if line.startswith(b'    index:'):
        current_id = str(line)[13:-1]

    for pid in spotify_pid_list:
        if line.startswith(b'\t\tapplication.process.id = "%b"' % pid.encode('utf8')):
            spotify_id = current_id

if spotify_id == -1:
    print("Spotify isn't currently playing anything, exiting")
    sys.exit(0)

print('Spotify PulseAudio player ID:', spotify_id)

# Mute and unmute Apotify through the PulseAudio player ID
def mute():
    os.system(f'pacmd set-sink-input-mute "{spotify_id}" 1')

def unmute():
    os.system(f'pacmd set-sink-input-mute "{spotify_id}" 0')

# Restore the volume after exiting
atexit.register(unmute)

# Connect to the Spotify DBus interface
print('Connecting to DBus interface...')
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

    if (title == "Advertisement" or title == "Spotify") and not artist:
        mute()
    else:
        unmute()

spotify_properties.connect_to_signal('PropertiesChanged', properties_changed)

# Run the GLib event loop to process DBus signals as they arrive
print('Everything done! Spotify AdEleminator is now running and listening for ads!')
mainloop = gi.repository.GLib.MainLoop()
mainloop.run()
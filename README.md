# Spotify AdEleminator - _v0.3_
Enjoy listening to music. Without ads. Legally.

## How does it work?
This script uses the DBus to communicate with Spotify.
Whenever a new song is played, it checks the title of the song. If it reads “Advertisement“, the script will mute spotify via PulseAudio.

## How to use?
1. Clone the repository: `git clone https://github.com/XECortex/spotify-adeleminator.git && cd spotify-adeleminator`
2. Run the install script: `sh install.sh`
3. Start the program from your applications menu or desktop
4. Enjoy music without ads! :)

## Dependencies
- Python
- PulseAudio `pacmd`
- Spotify (who didn't expect that?)

This script currently only works on Linux, but I will add Windows compatibility soon

## Screenshot
![Screenshot](https://raw.githubusercontent.com/XECortex/spotify-adeleminator/main/screenshot.jpg)
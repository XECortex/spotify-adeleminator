# Spotify AdEleminator
Enjoy listening to music. Without ads. Legally.

## How does it work?
This script uses the DBus to communicate with Spotify.
Whenever a new song is played, it checks the title of the song. If it reads “Advertisement“, the script will mute your system sound.

## How to use?
1. Clone the repository: `git clone https://github.com/XECortex/spotify-adeleminator.git && cd spotify-adeleminator`
2. Allow main.py to be executed with `sudo chmod +x main.py`
3. Open Spotify
4. Run `main.py`
5. Enjoy music without ads! :)

## Dependencies
- Python
- PulseAudio
- Spotify (who didn't expect that?)

This script currently only works on Linux, but I will add Windows compatibility soon
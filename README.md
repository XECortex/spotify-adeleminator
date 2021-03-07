# Spotify AdEleminator - _v0.9_
Enjoy listening to music. Without ads. Legally.\
You will still support the artist you listen to when using this program as it doesn't _block_ the ads but _mute_ them! They are still paid because they were played, but you just weren't listening to it (:

**If it doesn't work properly, please open a issue so I can fix it, thank you!**

## How does it work?
This script uses the DBus to communicate with Spotify.
Whenever a new song is played, it checks the title of the song. If it reads “Advertisement“, the script will mute Spotify via PulseAudio.

## How to use?
### Installation
1. Clone the repository: `git clone https://github.com/XECortex/spotify-adeleminator.git && cd spotify-adeleminator`
2. Run the install script: `sh install.sh`
3. Start the program from your applications menu or desktop
4. Enjoy music without ads!

You can also just grab the main.py and run `python main.py` (or whatever you rename the file to)

### Updates
You can simply install updates by running `git pull` in the directory of Spotify AdEleminator on your System.

### Run in background
Just add the `-d` flag when executing Spotify AdEleminator.
If you want to always have this program always running in background, you can, for example, add `path/to/spotify-adeleminator/main.py -d` to your autostart.

## Dependencies
- Python
- PulseAudio or PiperWire-Pulse (`pactl`)
- `xdotool`
- Spotify (who didn't expect that?)

This script currently only works on Linux, but I will add Windows compatibility soon

## Screenshot
![Screenshot](https://raw.githubusercontent.com/XECortex/spotify-adeleminator/main/screenshot.jpg)

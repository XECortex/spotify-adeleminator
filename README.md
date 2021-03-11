# Spotify AdEleminator - _v1.1_

Enjoy listening to music. Without ads. Legally.\
You will still support the artist you listen to when using this program as it doesn't _block_ the ads but _mute_ them! They are still paid because they were played, but you just weren't listening to it (:

_Once a friend told me, “Thank you for that, finally I can listen to music in peace!“_

**If something doesn't work properly, please open a issue so I can fix it, thank you!**

## How does it work?
This script uses the DBus to communicate with Spotify.
Whenever a new song is played, it checks the title of the song. If it reads “Advertisement“ (or other keywords), the script will mute Spotify via PulseAudio.

## How to use?
### Installation
1. Clone the repository: `git clone https://github.com/XECortex/spotify-adeleminator.git && cd spotify-adeleminator`
2. Run the install script: `sh install.sh`
3. Start the program from your applications menu or desktop
4. Enjoy music without ads!

You can also just grab the main.py and run `python main.py` (or whatever you rename the file to)

### Command line options
```
usage: main.py [-h] [-a] [-l]

optional arguments:
  -h, --help        show this help message and exit
  -a, --autolaunch  launch Spotify on program start
  -l, --loop        do not close with Spotify but wait for a new instance
```

### Updates
You can simply install updates by running `git pull` in the directory of Spotify AdEleminator on your System.

## Dependencies
- Python
- PulseAudio or PiperWire-Pulse (`pactl`)
- Spotify (who didn't expect that?)

## Screenshot
![Screenshot](https://raw.githubusercontent.com/XECortex/spotify-adeleminator/main/terminal.png)
![Screenshot](https://raw.githubusercontent.com/XECortex/spotify-adeleminator/main/screenshot.png)

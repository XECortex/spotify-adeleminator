#!/usr/bin/env sh

echo "Installing..."

# Mark main.py as executable
sudo chmod +x main.py

# Create the desktop launcher
touch spotify-adeleminator.desktop
truncate -s 0 spotify-adeleminator.desktop
echo -e "[Desktop Entry]\nType=Application\nName=Spotify AdEleminator\nGenericName=Mute Ads\nIcon=spotify-client\nTerminal=true\nCategories=Audio;Music;Player;AudioVideo;\nComment=Enjoy listening to music. Without ads. Legally.\nExec="$(pwd)"/main.py" >> spotify-adeleminator.desktop

# Mark the launcher as executable
sudo chmod +x spotify-adeleminator.desktop

# Copy the launcher to the desktop and applications directory
sudo cp spotify-adeleminator.desktop /usr/share/applications
cp spotify-adeleminator.desktop ~/Desktop

echo "Done!"
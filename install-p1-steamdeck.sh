flatpak --user --assumeyes --noninteractive install flathub com.usebottles.bottles
flatpak run --command=bottles-cli com.usebottles.bottles new --bottle-name P1 --environment gaming

git clone https://github.com/sonic2kk/steamtinkerlaunch /home/deck/steamtinkerlaunch
chmod +x /home/deck/steamtinkerlaunch/steamtinkerlaunch
wget https://github.com/emanuel2001just/python3-PokeOne-Launcher/releases/download/steamdeck-test1/PokeOne.Launcher.SteamDeck.AppImage -O /home/deck/PokeOne.AppImage

chmod +x /home/deck/PokeOne.AppImage

/home/deck/steamtinkerlaunch/steamtinkerlaunch ansg -ep=/home/deck/PokeOne.AppImage --appname=PokeOne -lo="LD_PRELOAD=${LD_PRELOAD/_32/_64} QT_SCALE_FACTOR=1.25 %command% --fullscreen --notransparency --new-tab --hide-menubar --qwindowgeometry 1024x640"

read -p "Press any key to continue "

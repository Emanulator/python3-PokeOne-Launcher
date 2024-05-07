#flatpak --user --assumeyes --noninteractive install flathub com.usebottles.bottles
echo "Please choose 'user' if asked!"
flatpak --assumeyes install flathub com.usebottles.bottles
export FORCE_OFFLINE=0
echo ""
echo ""
echo "Please Complete the Bottles Setup and close it afterwards"
echo ""
read -p "Press any key to continue when ready "


flatpak run --command=bottles-cli com.usebottles.bottles new --bottle-name P1 --environment gaming
flatpak override --user com.usebottles.bottles --filesystem="~/PokeOne"
git clone https://github.com/sonic2kk/steamtinkerlaunch ~/steamtinkerlaunch
chmod +x ~/steamtinkerlaunch/steamtinkerlaunch
wget https://github.com/emanuel2001just/python3-PokeOne-Launcher/releases/download/steamdeck-test1/PokeOne.Launcher.SteamDeck.AppImage -O ~/PokeOne.AppImage

chmod +x ~/PokeOne.AppImage
unset HOME; export HOME=~

~/steamtinkerlaunch/steamtinkerlaunch ansg -ep=$HOME/PokeOne.AppImage --appname="PokeOne" -lo="LD_PRELOAD=${LD_PRELOAD/_32/_64} QT_SCALE_FACTOR=1.25 %command% --fullscreen --notransparency --new-tab --hide-menubar --qwindowgeometry 1024x640"

read -p "Press any key to continue "

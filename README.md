# Alternative Python Installer
This is a simple python-based installer that allows you to install (in a non-intrusive way) any python version that you like.
## Dependencies
### Ubuntu (tested on 19.10)
```
sudo apt install gcc libbz2-dev libffi-dev libgdbm-dev liblzma-dev libreadline-dev libsqlite3-dev libssl-dev libz1g-dev make tk8.6-dev uuid-dev
```
### Fedora (tested on F31)
```
sudo dnf install gcc gdbm-devel libffi-devel libnsl2-devel libtirpc-devel libuuid-devel make ncurses-devel openssl-devel readline-devel sqlite-devel tk-devel xz-devel
```
## Install Instructions
Please first clone this repo to your home directory, with the name .AlternativePy as follows:
```
git clone https://github.com/Scott-Barnett/AlternativePy.git $HOME/.AlternativePy
```
Then add the executable directory to your path as follows, by adding the following to your $HOME/.bashrc
```
if [ -d "$HOME/.AlternativePy/Executables" ]; then
  PATH="$HOME/.AlternativePy/Executables:$PATH"
fi
```
Update for your current terminal with
```
source $HOME/.bashrc
```
## Removal Instructions
If you decide you no longer want AlternativePy installed, simply remove that line from your .bashrc and run the `source` command again. Also remove the $HOME/.AlternativePy folder.
## Usage
### Installation
```
alternativepy install <version>
```
### Removal
```
alternativepy remove <version>
```
### Full clean of installs
```
alternativepy clean
```


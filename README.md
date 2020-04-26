# Alternative Python Installer
This is a simple python-based installer that allows you to install (in a non-intrusive way) any python version that you like.
## Dependencies
### Ubuntu (tested on 19.10)
```
sudo apt install gcc libbz2-dev libffi-dev libgdbm-compat-dev libgdbm-dev liblzma-dev libreadline-dev libsqlite3-dev libssl-dev make tk8.6-dev uuid-dev
```
### Fedora (tested on F31)
```
sudo dnf install gcc gdbm-devel libffi-devel libnsl2-devel libtirpc-devel libuuid-devel make ncurses-devel openssl-devel readline-devel sqlite-devel tk-devel xz-devel
```
## Install Instructions
Please first clone this repo to a directory of your choice (as shown below, where <DESTINATION_DIR> is the location to be used for the install - I suggest $HOME/.AlternativePy if you have no preference)
```
git clone https://github.com/Scott-Barnett/AlternativePy.git <DESTINATION_DIR>
```
Then add the executable directory to your path by inserting the following to your $HOME/.bashrc
```
if [ -d "$HOME/<DESTINATION_DIR>/bin" ]; then
  PATH="$HOME/<DESTINATION_DIR>/bin:$PATH"
fi
```
Update for your current terminal with
```
source $HOME/.bashrc
```
## Removal Instructions
If you decide you no longer want AlternativePy installed, simply remove that line from your .bashrc and run the `source` command again. Also remove the <DESTINATION_DIR> folder.
## Usage
### Version Installation
```
alternativepy install <version>
```
### Version Removal
```
alternativepy remove <version>
```
### Full clean of installs
```
alternativepy clean
```
### Using the installed versions
Simply use altpy-\<normal python command with full version number\>
For example:
```
altpy-python3.8.2
```
### Using Virtual Environments
Virtual environments work the same way you would expect normally, for example:
```
altpy-python3.8.2 -m venv venv
```
Inside the venv folder, the bin/activate script can be activated. Then the `python` command will link to the altpy python version (in this case 3.8.2)

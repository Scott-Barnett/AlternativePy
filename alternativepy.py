#!/usr/bin/env python3

import sys
import os
import subprocess
import shutil
import urllib.request
import tarfile
from bs4 import BeautifulSoup

PYTHON_BASE_URL = "https://www.python.org/ftp/python"
PYTHON_SOURCE_URL = PYTHON_BASE_URL + "/{}/Python-{}.tgz"
PYTHON_ASC_URL = "{}.asc"
BASE_DIRECTORY = os.path.abspath('.')
DOWNLOAD_LOCATION = os.path.join(BASE_DIRECTORY, "PythonVersions")

def get_confirmation(prompt: str) -> bool:
    """
    Take a prompt and continually ask it until a Y or N is received, and
    then return in the form of a boolean (Y == True)
    """
    response = None
    while response not in ['Y', 'N']:
        response = input(f"{prompt}: ").upper()
    return response == "Y"

def get_valid_python_versions() -> list:
    """
    Obtain a list of valid Python versions from the website and return them
    in the form of a list of strings
    """
    # Download the HTML from the file hosting site
    html = urllib.request.urlopen(PYTHON_BASE_URL)
    # Read the HTML into a string and decode it
    data = html.read().decode()
    # Load the string into Beautifulsoup, ready for parsing
    soup = BeautifulSoup(data, 'html.parser')
    # Find all the link tags
    links = soup.findAll('a')
    versions = []
    # First link is back to the parent directory, so ignore it
    for link in links[1:]:
        # Get the value of the text (not the link itself)
        value = link.get_text()
        try:
            # The first digit is only a number if it is a valid python version
            int(value[:1])
        # We have finished with the valid versions - break from the loop
        except ValueError:
            break
        # Append the valid version to the list (without the / present in the HTML)
        versions.append(value[:-1])
    return versions

def verify_python_version(version: str) -> bool:
    """
    Ensure the user is trying to use a valid Python version
    """
    # Don't query the website if the version is clearly wrong (not beginning with a number)
    try:
        int(version[:1])
    except ValueError:
        return False
    valid_version_list = get_valid_python_versions()
    # If the version is in the version list, it is valid
    return version in valid_version_list

def execute_terminal_command(command: str) -> bool:
    """
    Execute a terminal command (passed as a string). Return exit status (True == Success)
    """
    try:
        process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # The command you are trying to run does not exist - return failure
    except FileNotFoundError:
        return False
    # Process.poll() returns the exit status (None if it is still running). Wait until it finishes
    while process.poll() is None:
        # Obtain the next line of output ready to print (in real time)
        output = process.stdout.readline().decode()[:-1]
        # Print the output so the user knows what's happening
        print(output)
    # Python truthiness states 0 is False, therefore flip it with a Not (0 is success)
    return not process.poll()

def download_python_version(version: str):
    """
    Download a specific Python version and build it, ready to be executed
    """
    # Check the Python version is valid
    if not verify_python_version(version):
        print(f"Invalid Python version: {version}")
        exit(1)
    # Ensure the specified Download location exists
    if not os.path.exists(DOWNLOAD_LOCATION):
        os.mkdir(DOWNLOAD_LOCATION)
    python_dir = os.path.join(DOWNLOAD_LOCATION, version)
    # Overwrite the existing install if requested, otherwise abort
    if os.path.exists(python_dir):
        if not get_confirmation("This python version already exists - would you like to redownload it"):
            print("Aborting...")
            exit(1)
        # Delete the existing install
        shutil.rmtree(python_dir)
    # Obtain the Python URL
    python_url = PYTHON_SOURCE_URL.format(version, version)
    python_location = f"{DOWNLOAD_LOCATION}/{version}.tgz"
    # Download the Python source package as a .tgz
    urllib.request.urlretrieve(python_url, python_location)
    # Open the .tgz and then extract it into the python directory
    f = tarfile.open(python_location, mode="r:gz")
    f.extractall(DOWNLOAD_LOCATION)
    f.close()
    # Rename the directory to the version
    os.rename(f"{DOWNLOAD_LOCATION}/Python-{version}", f"{DOWNLOAD_LOCATION}/{version}")
    # Remove the .tgz
    os.remove(python_location)
    # Change into the Python directory for building
    os.chdir(python_dir)
    # Configure the Python install
    execute_terminal_command("./configure --enable-optimizations --with-ensurepip=install")
    # Build Python
    execute_terminal_command("make")
    os.chdir(BASE_DIRECTORY)

if __name__ == "__main__":
    if sys.version_info < (3, 6):
        print("Please update the Python version used to run this script to at least Python 3.6")
        exit(1)
    COMMANDS = ["install", "clean", "help"]
    if sys.argv[1] not in COMMANDS:
        print("That is an invalid command. Please run \"alternativepy help\" for commands")
        exit(1)
    if sys.argv[1] == "install":
        if len(sys.argv) != 3:
            print("Please enter the command in the following format: install <python-version>")
            exit(1)
        download_python_version(sys.argv[2])
    elif sys.argv[1] == "clean":
        if len(sys.argv) != 2:
            print("Clean cannot take additional arguments")
            exit(1)
        shutil.rmtree(DOWNLOAD_LOCATION)

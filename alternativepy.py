#!/usr/bin/env python3

import sys
import os
import subprocess
import shutil
import urllib.request
import tarfile
import glob
from bs4 import BeautifulSoup

PYTHON_BASE_URL = "https://www.python.org/ftp/python"
PYTHON_SOURCE_URL = PYTHON_BASE_URL + "/{}/Python-{}.tgz"
PYTHON_ASC_URL = "{}.asc"
BASE_DIRECTORY = os.path.abspath('.')
DOWNLOAD_LOCATION = os.path.join(BASE_DIRECTORY, "PythonVersions")
LINKS_LOCATION = os.path.join(BASE_DIRECTORY, "PythonLinks")

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

def execute_terminal_command_with_output(command: str) -> (bool, str):
    """
    Returns the success of the command with the error or output depending on success
    """
    try:
        process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # The command you are trying to run does not exist - return failure
    except FileNotFoundError:
        return (False, "Invalid Command")
    stdout, stderr = process.communicate()
    if not process.poll():
        return (True, stdout.decode()[:-1])
    return (False, stderr.decode()[:-1])

def download_python_version(version: str) -> bool:
    """
    Download a specific Python version, ready to be built
    """

    # Is the specified Python version valid
    if not verify_python_version(version):
        print(f"Invalid Python version: {version}")
        return False
    
    # Does the download location exist? If not, create it
    if not os.path.exists(DOWNLOAD_LOCATION):
        os.mkdir(DOWNLOAD_LOCATION)
    
    # Define the download url and the path it will be downloaded to
    download_url = PYTHON_SOURCE_URL.format(version, version)
    file_download_location = f"{DOWNLOAD_LOCATION}/{version}.tgz"

    # Download the Python version
    urllib.request.urlretrieve(download_url, file_download_location)

    # Open the .tgz and then extract it into the python directory
    f = tarfile.open(file_download_location, mode="r:gz")
    f.extractall(DOWNLOAD_LOCATION)
    f.close()

    # Remove the .tgz
    os.remove(file_download_location)
    return True

def delete_version(version: str) -> bool:
    """
    Remove a version from the system
    """
    # Is the specified Python version valid
    if not verify_python_version(version):
        print(f"Invalid Python version: {version}")
        return False

    # Define the install dir
    INSTALL_DIR = os.path.join(DOWNLOAD_LOCATION, version)
    
    # Delete install
    if os.path.exists(INSTALL_DIR):
        shutil.rmtree(INSTALL_DIR)
    files = glob.glob(f"{LINKS_LOCATION}/*{version}*")
    for f in files:
        os.remove(f)
    return True

def build_python_version(version: str) -> bool:
    """
    Take the files that have been extracted and build them into a full compiled Python version
    """

    # Define directories
    BUILD_DIR = os.path.join(DOWNLOAD_LOCATION, f"Python-{version}")
    INSTALL_DIR = os.path.join(DOWNLOAD_LOCATION, version)

    # Delete the current install if it exists (checks already completed by this point)
    delete_version(version)

    # Change into the correct folder and execute the build commands
    os.chdir(BUILD_DIR)
    execute_terminal_command(f"./configure --enable-optimizations --with-ensurepip=install --prefix={INSTALL_DIR} --exec_prefix={INSTALL_DIR}")

    # Obtain cores that are available to build with
    status, core_output = execute_terminal_command_with_output("nproc")
    if not status:
        print(f"Cannot obtain CPU core number\nError:\n{core_output}\nRunning single-threaded")
        core_output = 1
    
    # Build Python
    execute_terminal_command(f"make -j{core_output}")

    # Install Python to the INSTALL_DIR
    execute_terminal_command("make altinstall")

    # Delete the build directory
    shutil.rmtree(BUILD_DIR)

    # Swap back to the original directory
    os.chdir(BASE_DIRECTORY)
    return True

def create_symlinks(version: str) -> bool:
    """
    Add altpy prefixed *properly versioned* symlinks to the links folder, which is added to the path
    """

    # Ensure the links location exists
    if not os.path.exists(LINKS_LOCATION):
        os.mkdir(LINKS_LOCATION)

    # Define the bin directory
    BIN_DIR = os.path.join(DOWNLOAD_LOCATION, version, "bin")
    
    # Create a symlink for all the bin executables
    executables = os.listdir(BIN_DIR)
    for exe in executables:
        if len(version) > 3:
            link_name = exe.replace(version[:3], version)
        else:
            link_name = exe
        execute_terminal_command(f"ln -s {BIN_DIR}/{exe} {LINKS_LOCATION}/altpy-{link_name}")

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
        shutil.rmtree(LINKS_LOCATION)
        os.mkdir(LINKS_LOCATION)

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
    response = None
    while response not in ['Y', 'N']:
        response = input(f"{prompt}: ").upper()
    return response == "Y"

def get_valid_python_versions() -> list:
    html = urllib.request.urlopen(PYTHON_BASE_URL)
    data = html.read().decode()
    soup = BeautifulSoup(data, 'html.parser')
    links = soup.findAll('a')
    versions = []
    for link in links[1:]:
        value = link.get_text()
        try:
            int(value[:1])
        except ValueError:
            break
        versions.append(value[:-1])
    return versions

def verify_python_version(version: str) -> bool:
    try:
        int(version[:1])
    except ValueError:
        return False
    valid_version_list = get_valid_python_versions()
    return version in valid_version_list

def execute_terminal_command(command: str) -> bool:
    try:
        process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        return False
    while process.poll() is None:
        output = process.stdout.readline().decode()[:-1]
        print(output)
    if process.poll():
        return False
    return True

def download_python_version(version: str):
    if not verify_python_version(version):
        print(f"Invalid Python version: {version}")
        exit(1)
    if not os.path.exists(DOWNLOAD_LOCATION):
        os.mkdir(DOWNLOAD_LOCATION)
    python_dir = os.path.join(DOWNLOAD_LOCATION, version)
    if os.path.exists(python_dir):
        if not get_confirmation("This python version already exists - would you like to redownload it"):
            print("Aborting...")
            exit(1)
        shutil.rmtree(python_dir)
    os.mkdir(python_dir)
    python_url = PYTHON_SOURCE_URL.format(version, version)
    python_location = f"{python_dir}/{version}.tgz"
    urllib.request.urlretrieve(python_url, python_location)
    f = tarfile.open(python_location, mode="r:gz")
    f.extractall(python_dir)
    f.close()
    os.chdir(os.path.join(python_dir, f"Python-{version}"))
    execute_terminal_command("./configure --enable-optimizations --with-ensurepip=install")
    execute_terminal_command("make")
    os.chdir(BASE_DIRECTORY)

if __name__ == "__main__":
    if sys.version_info < (3, 6):
        print("Please update the Python version used to run this script to at least Python 3.6")
        exit(1)
    

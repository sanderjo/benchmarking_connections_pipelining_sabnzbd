#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import re
from timeit import main

import requests

base = "http://localhost:8080/api?"

def get_apikey():
    # read api_key from file $HOME/.sabnzbd/sabnzbd.ini
    with open(os.path.expanduser("~/.sabnzbd/sabnzbd.ini"), "r") as f:
        for line in f:
            print(line)
            if line.startswith("api_key"):
                return line.split("=", 1)[1].strip()
    return None


apikey= "3aa5b2faa7874d75a7fd3059f351d595"
apikey = get_apikey()
if apikey is None:
    print("Could not find API key in ~/.sabnzbd/sabnzbd.ini. Please make sure it is there and try again.")
    sys.exit(1)
else:
    print(f"Using API key: {apikey}")
nzb_name = "test_download_1000MB.nzb"

# #base = "http://111.168.1.111:8080/api?"
# apikey = "3aa5"
URL = f"{base}apikey={apikey}"

def generic_api_request(params):
    try:
        response = requests.get(URL, params=params, timeout=5)
        data = response.json()
        return data
    except Exception as e:
        print(f"Failed to get stats: {e}")
        return None
    
def check_connection_and_apikey():
    params = {
        'mode': 'get_config',
    }
    data = generic_api_request(params)
    print(f"API Response: {data}")
    if data and "config" in data:
        print("API key is valid.")
    else:
        print("API key is invalid or there was an error.")


def get_mbleft():
    params = {
        'mode': 'queue',
    }
    data = generic_api_request(params)
    if data:
        mbleft = data["queue"]["mbleft"]
    else:
        return None
    return float(mbleft)

def get_enabled_servers():
    # mode=get_config&section=servers
    params = {
        'mode': 'get_config',
        'section': 'servers'
    }
    data = generic_api_request(params)
    if data:
        servers = data["config"]["servers"]
        enabled_servers = [s['name'] for s in servers if s["enable"] == 1]
        return enabled_servers
    else:
        return None

def set_server_settings(servername, connections, pipelining):
    params = {
        'mode': 'set_config',
        'section': 'servers',
        'name': servername,
        'connections': connections,
        'pipelining_requests': pipelining
    }
    data = generic_api_request(params)
    if data:
        #print(f"Server settings updated successfully: {data}")
        return True
    else:
        print(f"Failed to update server settings.")
        return False
    
def restart_sabnzbd():
    params = {
        'mode': 'restart',
    }
    data = generic_api_request(params)
    if data:
        print(f"SABnzbd restarted successfully: {data}")
        return True
    else:
        print(f"Failed to restart SABnzbd.")
        return False

def pause_and_resume_sabnzbd():
    # Pause
    params_pause = {
        'mode': 'pause',
    }
    data_pause = generic_api_request(params_pause)
    if data_pause:
        print(f"SABnzbd paused successfully: {data_pause}")
    else:
        print(f"Failed to pause SABnzbd.")
        return False
    
    time.sleep(2)  # Wait for a moment before resuming

    # Resume
    params_resume = {
        'mode': 'resume',
    }
    data_resume = generic_api_request(params_resume)
    if data_resume:
        print(f"SABnzbd resumed successfully: {data_resume}")
        return True
    else:
        print(f"Failed to resume SABnzbd.")
        return False

def add_NZB(filepath):
    params = {
        'mode': 'addlocalfile',
        'name': filepath,
        'pp': "0" # post-processing disabled, we just want to test the download speed
    }
    data = generic_api_request(params)
    if data:
        print(f"NZB file added successfully: {data}")
        return True
    else:
        print(f"Failed to add NZB file.")
        return False

def get_average_speed_of_last_download():
    params = {
        'mode': 'history',
        'limit': 1
    }
    data = generic_api_request(params)
    # if data and "history" in data and len(data["history"]) > 0:
    #     last_download = data["history"][0]
    #     return last_download.get("avg_speed", 0.0)
    # else:
    #     print("No download history found.")
    #     return 0.0
    avg_speed = 0.0
    if data:
        download_str = data["history"]["slots"][0]["stage_log"][1]["actions"][0]
        print(f"Download String: {download_str}")
        # from "Downloaded in 9 mins 59 seconds at an average of 5.3 MB/s<br/>Age: 1h" get "5.3"
        match = re.search(r"an average of (\d+\.\d+) MB/s", download_str)
        if match:
            avg_speed = match.group(1)
            #print(f"Average Speed: {avg_speed}")
            # convert to float
            avg_speed = float(avg_speed)
    return avg_speed

def get_storage_from_history():
    params = {
        'mode': 'history',
        'limit': 1
    }
    data = generic_api_request(params)
    #print(f"History Data: {data}")
    if data:
        slots = data.get("history", {}).get("slots", [])
        #print(f"Slots: {slots}")
        if slots:
            return slots[0].get("storage")
        return None
    return None

def remove_download(nzb_name, storage):
    # from nzb_name, remove ".nzb" to get "test_download_1000MB"
    nzb_name = nzb_name.replace(".nzb", "")
    # print(nzb_name, type(nzb_name))
    # print(storage, type(storage))
    # print(f"Is NZB name in storage path? {'Yes' if str(nzb_name) in str(storage) else 'No'}")
    # pos = str(storage).find(str(nzb_name))
    # print(f"Position of NZB name in storage path: {pos}")
    if str(nzb_name) in str(storage):
        # remove directory "/complete/test_download_1000MB" or "/incomplete/test_download_1000MB"
        dir_to_remove = storage
        #print(f"Removing directory: {dir_to_remove}")
        if os.path.isdir(dir_to_remove):
            try:
                import shutil
                shutil.rmtree(dir_to_remove)
                print(f"Directory removed successfully.")
            except Exception as e:
                print(f"Failed to remove directory: {e}")
        else:
            print(f"Directory not found: {dir_to_remove}")
    else:
        print(f"NZB name not found in storage path: {storage}")
    
def download_and_get_speed(servername, connections, pipelining, nzb_name):
    if not set_server_settings(servername, connections, pipelining):
        print("Failed to set server settings.")
        sys.exit(1)

    pause_and_resume_sabnzbd() # to make new server settings take effect

    # get working diretory
    working_dir = os.getcwd()
    nzb_file = os.path.join(working_dir, nzb_name)
    if not os.path.isfile(nzb_file):
        print(f"NZB file not found: {nzb_file}")
        sys.exit(1)
    add_NZB(nzb_file)

     # wait until it starts downloading. But take some time due to pre-checking.
    print("Waiting for download to start", end="")
    while True:
         mbleft = get_mbleft()
         if mbleft > 0.0:
            # download has started
            break
         print(".", end="")
         time.sleep(0.1)
    print("\nDownload has started.")

     # OK, started, now wait until it finishes. Watch mbleft until it becomes 0 again, which means the download is finished
    while True:
        mbleft = get_mbleft()
        print(f"MB left: {mbleft}   ", end="")
        if mbleft == 0.0:
            print("Download finished.")
            break
        time.sleep(1)

    time.sleep(5) # wait a bit to make sure everything is written to history and storage paths are correct

    # delete from harddisk:
    storage = get_storage_from_history()
    print(f"Storage from history JSON: {storage}")
    remove_download(nzb_name, storage)
    avg_speed = get_average_speed_of_last_download()
    return avg_speed

def get_ping_time(host):
    import subprocess
    try:
        output = subprocess.check_output(["ping", "-c", "1", host], universal_newlines=True)
        match = re.search(r"time=(\d+\.\d+) ms", output)
        if match:
            return float(match.group(1))
    except Exception as e:
        print(f"Failed to ping {host}: {e}")
    return None

if __name__ == "__main__":
    

    mbleft = get_mbleft()
    if mbleft is None:
        print("Could not fetch queue information. Is SABnzbd reachable?")
        sys.exit(1)
    elif mbleft != 0.0:
        print(f"Download in queue, size {mbleft} MB. Please wait for it to finish before running the benchmark.")
        sys.exit(1)


    enabled_servers = get_enabled_servers()
    if len(enabled_servers) == 0:
        print("No enabled servers found.")
        sys.exit(1)
    if len(enabled_servers) > 1:
        print("Multiple enabled servers found. Please disable all but one server before running the benchmark.")
        sys.exit(1)
    servername = enabled_servers[0]
    print(f"Using server: {servername}")
    ping_time = get_ping_time(servername)
    print(f"Ping time to server {servername}: {ping_time} ms")
    print(f"Using NZB file: {nzb_name}")

    print("Starting benchmark...")
    #sys.exit()

    #OK, boilerplate done. Now the stuff we want to test:

    # set server settings
    connections_list = [1, 5, 10, 20, 80]
    pipelining_list = [1, 2, 5, 10, 20]

    # connections = 22
    # pipelining = 5
    for connections in connections_list:
        for pipelining in pipelining_list:
            avg_speed = download_and_get_speed(servername, connections, pipelining, nzb_name)
            print(f"Connections {connections}, Pipelining {pipelining}: Average Speed: {avg_speed}")



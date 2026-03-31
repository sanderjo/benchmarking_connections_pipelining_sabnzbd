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
            #print(line)
            if line.startswith("api_key"):
                return line.split("=", 1)[1].strip()
    return None


apikey= "3aa5b2faa7874d75a7fd3059f351d595"
apikey = get_apikey()
if apikey is None:
    print("Could not find API key in ~/.sabnzbd/sabnzbd.ini. Please make sure it is there and try again.")
    sys.exit(1)
else:
    obfuscated_apikey = apikey[:4] + "..." + apikey[-4:]
    print(f"Using API key: {obfuscated_apikey}")
    #print(f"Using API key: {apikey}", flush=True)

nzb_name = "test_download_1000MB.nzb"
nzb_name = "my_test.nzb"


URL = f"{base}apikey={apikey}"

def generic_api_request(params, timeout=5):
    try:
        response = requests.get(URL, params=params, timeout=timeout)
        data = response.json()
        return data
    except Exception as e:
        print(f"Failed to get stats: {e}", flush=True)
        return None
    
def check_connection_and_apikey():
    params = {
        'mode': 'get_config',
    }
    data = generic_api_request(params)
    print(f"API Response: {data}", flush=True)
    if data and "config" in data:
        print("API key is valid.", flush=True)
    else:
        print("API key is invalid or there was an error.", flush=True)


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
        print(f"Failed to update server settings.", flush=True)
        return False
    
def restart_sabnzbd():
    params = {
        'mode': 'restart',
    }
    data = generic_api_request(params)
    if data:
        print(f"SABnzbd restarted successfully: {data}", flush=True)
        return True
    else:
        print(f"Failed to restart SABnzbd.", flush=True)
        return False

def pause_and_resume_sabnzbd():
    # Pause
    params_pause = {
        'mode': 'pause',
    }
    data_pause = generic_api_request(params_pause)
    if data_pause:
        print(f"SABnzbd paused successfully: {data_pause}", flush=True)
    else:
        print(f"Failed to pause SABnzbd.", flush=True)
        return False
    
    time.sleep(2)  # Wait for a moment before resuming

    # Resume
    params_resume = {
        'mode': 'resume',
    }
    data_resume = generic_api_request(params_resume)
    if data_resume:
        print(f"SABnzbd resumed successfully: {data_resume}", flush=True)
        return True
    else:
        print(f"Failed to resume SABnzbd.", flush=True)
        return False

def add_NZB(filepath):
    params = {
        'mode': 'addlocalfile',
        'name': filepath,
        'pp': "0" # post-processing disabled, we just want to test the download speed
    }
    data = generic_api_request(params)
    if data:
        print(f"NZB file added successfully: {data}", flush=True)
        return True
    else:
        print(f"Failed to add NZB file.", flush=True)
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
        print(f"Download String: {download_str}", flush=True)
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
                print(f"Directory removed successfully.", flush=True)
            except Exception as e:
                print(f"Failed to remove directory: {e}", flush=True)
        else:
            print(f"Directory not found: {dir_to_remove}", flush=True)
    else:
        print(f"NZB name not found in storage path: {storage}", flush=True)
    
def download_and_get_speed(servername, connections, pipelining, nzb_name):
    if not set_server_settings(servername, connections, pipelining):
        print("Failed to set server settings.")
        sys.exit(1)

    pause_and_resume_sabnzbd() # to make new server settings take effect

    # get working diretory where the .NZB file is located, which is the current directory of this script
    working_dir = os.getcwd()
    nzb_file = os.path.join(working_dir, nzb_name)
    if not os.path.isfile(nzb_file):
        print(f"NZB file not found: {nzb_file}")
        sys.exit(1)
    add_NZB(nzb_file)

     # wait until it starts downloading. But take some time due to pre-checking (if on)
    print("Waiting for download to start", end="", flush=True)
    while True:
         mbleft = get_mbleft()
         if mbleft > 0.0:
            # download has started
            break
         print(".", end="", flush=True)
         time.sleep(0.1)
    print(f"\nDownload has started: MB left: {mbleft}", flush=True)

     # OK, started, now wait until it finishes. Watch mbleft until it becomes 0 again, which means the download is finished
    while True:
        mbleft = get_mbleft()
        print(f"MB left: {mbleft}   ", end="", flush=True)
        if mbleft == 0.0:
            print("Download finished.", flush=True)
            break
        time.sleep(1)

    time.sleep(5) # wait a bit to make sure everything is written to history and storage paths are correct

    # delete from harddisk:
    storage = get_storage_from_history()
    print(f"Storage from history JSON: {storage}", flush=True)
    remove_download(nzb_name, storage)
    avg_speed = get_average_speed_of_last_download()
    return avg_speed

def get_ping_time(host):
    import subprocess
    try:
        output = subprocess.check_output(["ping", "-c", "4", host], universal_newlines=True)
        # from the line "rtt min/avg/max/mdev = 10.476/15.200/21.276/4.156 ms" extract the avg time, which is the second number in the min/avg/max/mdev part
        avg_time = re.search(r"rtt min/avg/max/mdev = .*/(\d+\.\d+)/(\d+\.\d+)/", output)
        #print(f"Ping output: {output}")
        if avg_time:
            return float(avg_time.group(1))
    except Exception as e:
        print(f"Error pinging {host}: {e}")
        return None

def get_internet_speed():
    # get internet speed using speedtest-cli
    # curl -s "http://127.0.0.1:8080/api?apikey=3aa5b2faa7874d75a7fd3059f351d595&mode=status&calculate_performance=1" | jq | grep -i internetbandwidth
    params = {
        'mode': 'status',
        'calculate_performance': 1
    }
    data = generic_api_request(params, timeout=15)
    #print(f"Status Data: {data}", flush=True)
    if data and "status" in data and "internetbandwidth" in data["status"]:
        return data["status"]["internetbandwidth"]
    return None

# def get_ping_time(host):
#     import subprocess
#     try:
#         output = subprocess.check_output(["ping", "-c", "4", host], universal_newlines=True)
#         print(f"Ping output: {output}")
#         match = re.search(r"time=(\d+\.\d+) ms", output)
#         if match:
#             return float(match.group(1))
#     except Exception as e:
#         print(f"Failed to ping {host}: {e}")
#     return None

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

    ping_time = int(get_ping_time(servername))
    print(f"Ping time to server {servername}: {ping_time} ms")

    print(f"Using NZB file: {nzb_name}")

    print("Checking internet speed...", flush=True)
    internetspeed = get_internet_speed()
    if internetspeed is not None:
        print(f"Internet speed: {internetspeed} MB/s")
    else:
        print("Could not fetch internet speed.")
        sys.exit(1)

 
    print("Starting benchmark...")
 
 
    # set server settings
    # first test with connections = 20 and pipelining = 5, so we see speed early on.
    connections_list = [20, 10, 5, 80]
    pipelining_list = [5, 1, 2, 10, 20]

    for connections in connections_list:
        for pipelining in pipelining_list:
            print(f"\nservername: {servername}, Connections {connections}, Pipelining {pipelining} ... starting")
            avg_speed = download_and_get_speed(servername, connections, pipelining, nzb_name)
            print(f"servername: {servername}, Connections {connections}, Pipelining {pipelining}: Average Speed: {avg_speed}")

    print("\nBenchmark completed.")

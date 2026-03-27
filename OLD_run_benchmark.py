#!/usr/vin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import re
from timeit import main
import requests

base = "http://drdr.local.:8080/api?"
apikey = "c2e5eb4c6b3e4a05a34c4beb9d2aaab0"

base = "http://localhost:8080/api?"
apikey= "3aa5b2faa7874d75a7fd3059f351d595"

def generic_api_request(params):
    fullurl = base + params + "&apikey=" + apikey
    try:        
        response = requests.get(fullurl)
        if response.status_code == 200:
            data = response.json()
            return data
    except Exception as e:
        print(f"An error occurred while fetching data: {e}")    
        return None

def get_average_speed_of_last_download():

    # get average speed of the last download
    #fullurl = "http://127.0.0.1:8080/api?mode=history&start=0&limit=1&output=json&apikey=c2e5eb4c6b3e4a05a34c4beb9d2aaab0"
    fullurl = base + "mode=history&start=0&limit=1&output=json&apikey=" + apikey
    #print(f"Full URL: {fullurl}")
    try:        
        response = requests.get(fullurl)
        if response.status_code == 200:
            data = response.json()
    except Exception as e:
        #print(f"An error occurred while fetching data: {e}")    
        pass
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

def queue_mbleft():
    fullurl = base + "mode=queue&output=json&apikey=" + apikey
    try:        
        response = requests.get(fullurl)
        if response.status_code == 200:
            data = response.json()
    except Exception as e:
        #print(f"An error occurred while fetching data: {e}")    
        return None
    mbleft = 0.0
    if data:
        mbleft = data["queue"]["mbleft"]
    return float(mbleft)

def get_enabled_servers():
    # "http://drdr.local.:8080/api?mode=get_config&section=servers&apikey=c2e5eb4c6b3e4a05a34c4beb9d2aaab0"
    fullurl = base + "mode=get_config&section=servers&apikey=" + apikey
    try:        
        response = requests.get(fullurl)
        if response.status_code == 200:
            data = response.json()
    except Exception as e:
        #print(f"An error occurred while fetching data: {e}")    
        return None
    enabled_servers = []
    if data:
        for server in data["config"]["servers"]:
            #servers.append(server["name"])
            print(server["name"])
            print(server["enable"])
            if server["enable"] == 1:
                print(f"Server {server['name']} is enabled.")
                enabled_servers.append(server["name"])
    #return servers
    return enabled_servers

def set_server_settings(servername, connections, pipelining):
    # Implementation for setting server settings
    #  "http://drdr.local.:8080/api?mode=set_config&section=servers&name=news.iad.newshosting.com&connections=44&pipelining_requests=7&apikey=c2e5eb4c6b3e4a05a34c4beb9d2aaab0"
    fullurl = base + f"mode=set_config&section=servers&name={servername}&connections={connections}&pipelining_requests={pipelining}&apikey={apikey}"
    try:        
        response = requests.get(fullurl)
        if response.status_code == 200:
            data = response.json()
            #print(f"Server settings updated successfully: {data}")
    except Exception as e:
        print(f"An error occurred while setting server settings: {e}")    
        return False
    return True

def restart_sabnzbd():
    # Implementation for restarting SABnzbd
    # "http://drdr.local.:8080/api?mode=restart&apikey=c2e5eb4c6b3e4a05a34c4beb9d2aaab0"
    fullurl = base + "mode=restart&apikey=" + apikey
    try:        
        response = requests.get(fullurl)
        if response.status_code == 200:
            data = response.json()
            print(f"SABnzbd restarted successfully: {data}")
    except Exception as e:
        print(f"An error occurred while restarting SABnzbd: {e}")    
        return False
    return True

def add_NZB(filepath):
    # Implementation for adding NZB file to the queue
    # "http://drdr.local.:8080/sabnzbd/api?mode=addlocalfile&name=/tmp/blabla.nzb&apikey=your_apikey_here"
    # "http://localhost:8080/api?mode=addlocalfile&name=/home/sander/git/benchmarking_connections_pipelining_sabnzbd/test_download_1000MB.nzb&apikey=3aa5b2faa7874d75a7fd3059f351d595"

    fullurl = base + f"mode=addlocalfile&name={filepath}&apikey={apikey}"
    try:        
        response = requests.get(fullurl)
        if response.status_code == 200:
            data = response.json()
            print(f"NZB file added successfully: {data}")
    except Exception as e:
        print(f"An error occurred while adding NZB file: {e}")    
        return False
    return True



def main():
    print("Hello, World!")

    mbleft = queue_mbleft()
    if mbleft is None:
        print("Could not fetch queue information. Is SABnzbd reachable?")
        sys.exit(1)
    elif mbleft != 0.0:
        print("Download in queue. Please wait for it to finish before running the benchmark.")
        sys.exit(1)

    #print(queue_mbleft())

    enabled_servers = get_enabled_servers()
    if len(enabled_servers) == 0:
        print("No enabled servers found.")
        sys.exit(1)
    if len(enabled_servers) > 1:
        print("Multiple enabled servers found. Please disable all but one server before running the benchmark.")
        sys.exit(1)
    servername = enabled_servers[0]
    print(f"Using server: {servername}")

    # set server settings
    connections = 22
    pipelining = 5
    if not set_server_settings(servername, connections, pipelining):
        print("Failed to set server settings.")
        sys.exit(1)

    restart_sabnzbd() # to make new server settings take effect

    # wait for SABnzbd to restart
    time.sleep(5)
    for i in range(100):
        mbleft = queue_mbleft()
        if mbleft is not None:
            # SAB is restarted
            # break out of loop
            break
        print(".", end="")
        time.sleep(1)
    print("\nSABnzbd is ready. Starting benchmark...")

    # get working diretory
    working_dir = os.getcwd()
    nzb_file = os.path.join(working_dir, "test_download_1000MB.nzb")
    if not os.path.isfile(nzb_file):
        print(f"NZB file not found: {nzb_file}")
        sys.exit(1)

    add_NZB(nzb_file)

    while True:
         mbleft = queue_mbleft()
         if mbleft > 0.0:
            # download has started
            break
         print(".", end="")
         time.sleep(0.1)

    # watch mbleft until it becomes 0 again, which means the download is finished
    while True:
        mbleft = queue_mbleft()
        print(f"MB left: {mbleft}   ", end="")
        if mbleft == 0.0:
            print("Download finished.")
            break
        print(f"{mbleft}", end="")
        time.sleep(1)


    avg_speed = get_average_speed_of_last_download()
    print(f"Final Average Speed: {avg_speed}")

if __name__ == "__main__":    
    main()

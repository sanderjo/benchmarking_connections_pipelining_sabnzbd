#!/usr/bin/env python3

def get_ping_time(host):
    import subprocess
    try:
        output = subprocess.check_output(["ping", "-c", "4", host], universal_newlines=True)
        # from the line "rtt min/avg/max/mdev = 10.476/15.200/21.276/4.156 ms" extract the avg time, which is the second number in the min/avg/max/mdev part
        avg_time = re.search(r"rtt min/avg/max/mdev = .*/(\d+\.\d+)/(\d+\.\d+)/", output)
        print(f"Ping output: {output}")
        if avg_time:
            return float(avg_time.group(1))
    except Exception as e:
        print(f"Error pinging {host}: {e}")
        return None
    
if __name__ == "__main__":
    import os
    import re
    import time
    import sys
    
    servername = "news.astraweb.com"
    
    ping_time = get_ping_time(servername)
    print(f"Ping time to server {servername}: {ping_time} ms")
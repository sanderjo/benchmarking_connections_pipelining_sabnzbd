# benchmarking_connections_pipelining_sabnzbd
Benchmarking of Conncetions and Pipelining in SABnzbd

A tool to measure resulting download speed with different values of Connections and Pipelining.

- Make sure SABnzbd is running. 
- Make sure only one newsserver is active.
- Make sure the queue is empty.
- Use the Wrench to measure your max linespeed
- Make sure no Bandwidth limitation is set.
- Run this script on the same machine as SABNzbd (same user, no docker ... or set apikey in this script manually)
- AND ... afterwards ... restore your server settings ...
```
python3 run_benchmark.py > results/my_results.txt
# wait until it returns to the prompt
cat results/my_results.txt | grep  -e Ping -e "Using NZB" -e Average 

# to get overall info:
cat results/my_results.txt | grep -e "Using server" -e Ping -e Internet -e "Download has started" | sort -ur
# get speeds:
cat results/my_results.txt | grep Average
```
# But easier and much more beuatiful ... if you have python package pandas installed:
$ ./parse_with_pandas.py results/raw-results-news.iad.newshosting.com.txt
Using server: news.iad.newshosting.com
Ping time to server news.iad.newshosting.com: 104 ms
test NZB size (MB): 1086.06


Pipelining Articles     1      2      5      10     20
Connections                                           
5                     27.4   24.4   64.9   71.8  103.2
10                    46.6   56.9  110.9  127.4  119.8
20                    79.5   93.7  150.8  158.1  152.9
80                   135.7  179.6  171.5  173.0  115.7
```

To get the 5 combinations with the highest speed:
```
$ cat raw-results-news.iad.newshosting.com.txt | grep  -e Ping -e Average -e "Using NZB" | awk '{print $NF, $0}'  | sort -n | cut -f2- -d' ' | tail -5
servername: news.iad.newshosting.com, Connections 20, Pipelining 20: Average Speed: 152.9
servername: news.iad.newshosting.com, Connections 20, Pipelining 10: Average Speed: 158.1
servername: news.iad.newshosting.com, Connections 80, Pipelining 5: Average Speed: 171.5
servername: news.iad.newshosting.com, Connections 80, Pipelining 10: Average Speed: 173.0
servername: news.iad.newshosting.com, Connections 80, Pipelining 2: Average Speed: 179.6

```

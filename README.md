# benchmarking_connections_pipelining_sabnzbd
Benchmarking of Conncetions and Pipelining in SABnzbd

A tool to measure resulting download speed with different values of Connections and Pipelining.

- Make sure SABnzbd is running. 
- Make sure only one newsserver is active.
- Make sure the queue is empty.
- Make sure no Bandwidth limitation is set.

```
python3 run_benchmark.py > results/my_results.txt
# wait until it returns to the prompt
cat results/my_results.txt | grep  -e Ping -e "Using NZB" -e Average 
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

#!/bin/bash 
#qsize=$1
iperf -c 10.0.0.2 -p 5001 -t 3600 -i 1 > iperf.txt &

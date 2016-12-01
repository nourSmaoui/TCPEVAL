#!/bin/bash

echo "******** starting experiment " $2 " *************"
mkdir $1/data
mkdir $1/plots
python dummynet.py $1 $2
python plot_cwnd.py $1 $2
python plot_throughput.py $1 $2
python plot_rtt.py $1 $2
python plot_ret.py $1 $2

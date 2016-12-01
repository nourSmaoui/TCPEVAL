#!/bin/bash



for entry in "$1"/*.xml
do
  ./run_exp.sh $1 `basename $entry`
done



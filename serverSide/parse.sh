#!/bin/bash
files=$(shopt -s nullglob dotglob; echo /home/cartracker/*)
if (( ${#files} ))
then
  cp /home/cartracker/* /home/cache/
  python3 reportprser.py > reporter.log
fi

#!/bin/bash


if [[ "$(ps aux | grep cooling-only | wc -l)" != "2" ]]
then
    echo "Not running"
else
    echo "Running"
fi

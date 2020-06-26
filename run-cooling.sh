#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# if the script isn't already running, start it
if [[ "$(ps aux | grep cooling-only | wc -l)" != "2" ]]
then
    source ${DIR}/env/bin/activate
    python ${DIR}/cooling-only.py &>>${DIR}/cooling.log
fi


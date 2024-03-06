#!/bin/bash

# Check if the SECOND_VOLUME_PATH is provided
cd /
if [ -z "$CONFIG" ]; then
    echo "CONFIG is not provided. Running ui protocol."
    # Execute your alternative protocol here
    # For example:
    tini -s -- python /utils/main_ui.py
else
    echo "CONFIG is provided. Running batch protocol."
    # Execute your standard protocol here
    # For example:
    python /utils/main_batch.py
fi

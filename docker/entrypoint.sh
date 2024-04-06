#!/bin/bash

# Check if the SECOND_VOLUME_PATH is provided
cd /
chmod +rw /evcomplex/
if [ -f /config/custom_config.yaml ]; then
    echo "CONFIG is provided. Running batch protocol."
    # Batch protcol
    python /home/utils/main_batch.py
else
    echo "CONFIG is not provided. Running ui protocol."
    # UI protocol
    tini -s -- python /home/utils/main_ui.py
fi

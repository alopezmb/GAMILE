#!/bin/bash

# Run this from local machine and then access 0.0.0.0:8888/tree in the browser
docker exec -it virtualmuseum_manager bash -c "jupyter notebook --ip 0.0.0.0 --no-browser --allow-root"

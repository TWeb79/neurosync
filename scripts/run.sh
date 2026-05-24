#!/bin/bash
# Run NeuroSync locally
# Author: Inventions4All - github:TWeb79

set -e

echo "Starting NeuroSync v0.1.0..."

# Check Python version
python3 --version

# Run the application
python3 -m neurosync.app.main
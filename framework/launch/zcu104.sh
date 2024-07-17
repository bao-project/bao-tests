#!/bin/bash

# Check if the required arguments are provided
if [ -z "$2" ]; then
    echo "Usage: $0 <tcl_script> <firmware_dir>"
    exit 1
fi

tcl_script="$1"
firmware_dir="$2"

# Check if xsct command is available
if ! command -v xsct &> /dev/null; then
    echo "Error: xsct command not found. Please ensure it is installed and available in your PATH."
    exit -1
fi

# Run the xsct command
xsct $tcl_script $firmware_dir

# Check the exit status of the xsct command
if [ $? -ne 0 ]; then
    echo "Error: xsct command failed."
    exit -2
fi

exit 0

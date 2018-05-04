#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EXAMPLE_FOLDER="$DIR/example"
SCRIPT_FOLDER="$DIR/script"
for example in ${EXAMPLE_FOLDER}/**; do
    # input and output folders
    outputFolder="${example}/output"
    rm -rf $outputFolder
done
echo "done clean output folder"

#!/bin/bash
EXAMPLE_FOLDER="example"
SCRIPT_FOLDER="script"
for example in ${EXAMPLE_FOLDER}/**; do
    # input and output folders
    outputFolder="${example}/output"
    echo $outputFolder
    rm -rf $outputFolder
done

#!/bin/bash
EXAMPLE_FOLDER="example"
SCRIPT_FOLDER="script"
for filename in ${EXAMPLE_FOLDER}/*.gv; do
    python3 ${SCRIPT_FOLDER}/graphviz_parser.py $filename -fca
    echo $filename
    dotFileBaseName=$(echo $filename | cut -d"." -f1)
    echo $dotFileBaseName
    dotFileName="${EXAMPLE_FOLDER}/${dotFileBaseName}_nodes.dot"
    echo $dotFileName
    dotFilePng="${EXAMPLE_FOLDER}/${dotFileBaseName}_nodes.png"
    dot -Tpng $dotFileName -o $dotFilePng
done

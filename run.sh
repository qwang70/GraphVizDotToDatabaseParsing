#!/bin/bash
EXAMPLE_FOLDER="example"
SCRIPT_FOLDER="script"
for filename in ${EXAMPLE_FOLDER}/*.gv; do
    python3 ${SCRIPT_FOLDER}/graphviz_parser.py $filename -fca
    echo $filename
    dotFileBaseName=$(echo $filename | cut -d"." -f1)
    echo $dotFileBaseName
    dotNodeFileName="${dotFileBaseName}_nodes.dot"
    echo $dotNodeFileName
    dotNodeFilePng="${dotFileBaseName}_nodes.png"
    dotHierachyFileName="${dotFileBaseName}_hierachy.dot"
    dotHierachyFilePng="${dotFileBaseName}_hierachy.png"
    dot -Tpng $dotNodeFileName -o $dotNodeFilePng
    dot -Tpng $dotHierachyFileName -o $dotHierachyFilePng
done

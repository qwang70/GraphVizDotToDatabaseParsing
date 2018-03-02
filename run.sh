#!/bin/bash
for filename in example/*.gv; do
    python3 graphviz_parser.py $filename -fca
    echo $filename
    dotFileBaseName=$(echo $filename | cut -d"." -f1)
    echo $dotFileBaseName
    dotFileName="${dotFileBaseName}_nodes.dot"
    echo $dotFileName
    dotFilePng="${dotFileBaseName}_nodes.png"
    dot -Tpng $dotFileName -o $dotFilePng
done

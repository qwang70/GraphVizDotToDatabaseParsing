#!/bin/bash
EXAMPLE_FOLDER="example"
SCRIPT_FOLDER="script"
for filename in ${EXAMPLE_FOLDER}/**/*.gv; do
    python3 ${SCRIPT_FOLDER}/graphviz_parser.py $filename -fca
    echo $filename
    dotFileBaseName=$(echo $filename | cut -d"." -f1)
    echo $dotFileBaseName
    dotNodeFileName="${dotFileBaseName}_nodes.dot"
    dotNodeFilePng="${dotFileBaseName}_nodes.png"
    dotEdgeFileName="${dotFileBaseName}_edges.dot"
    dotEdgeFilePng="${dotFileBaseName}_edges.png"
    dotFullFileName="${dotFileBaseName}_full.dot"
    dotFullFilePng="${dotFileBaseName}_full.png"
    dotNodeHierachyFileName="${dotFileBaseName}_nodes_hierachy.dot"
    dotNodeHierachyFilePng="${dotFileBaseName}_nodes_hierachy.png"
    dotEdgeHierachyFileName="${dotFileBaseName}_edges_hierachy.dot"
    dotEdgeHierachyFilePng="${dotFileBaseName}_edges_hierachy.png"
    dot -Tpng $dotNodeFileName -o $dotNodeFilePng
    dot -Tpng $dotEdgeFileName -o $dotEdgeFilePng
    dot -Tpng $dotFullFileName -o $dotFullFilePng
    dot -Tpng $dotNodeHierachyFileName -o $dotNodeHierachyFilePng
    dot -Tpng $dotEdgeHierachyFileName -o $dotEdgeHierachyFilePng
done

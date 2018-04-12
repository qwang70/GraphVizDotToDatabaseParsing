#!/bin/bash
EXAMPLE_FOLDER="example"
SCRIPT_FOLDER="script"
for example in ${EXAMPLE_FOLDER}/**; do
    # input and output folders
    inputFolder="${example}/input"
    outputFolder="${example}/output"
    for filename in ${inputFolder}/*.gv; do
        python3 ${SCRIPT_FOLDER}/graphviz_parser.py $filename 
        gvFileBaseName=$(basename $filename | cut -d"." -f1)
        echo "basename"
        echo $filename
        echo $gvFileBaseName
        mkdir -p ${outputFolder}
        gvNodeFileName="${outputFolder}/${gvFileBaseName}_nodes.gv"
        gvNodeFilePng="${outputFolder}/${gvFileBaseName}_nodes.png"
        gvEdgeFileName="${outputFolder}/${gvFileBaseName}_edges.gv"
        gvEdgeFilePng="${outputFolder}/${gvFileBaseName}_edges.png"
        gvFullFileName="${outputFolder}/${gvFileBaseName}_full.gv"
        gvFullFilePng="${outputFolder}/${gvFileBaseName}_full.png"
        gvNodeHierachyFileName="${outputFolder}/${gvFileBaseName}_nodes_hierachy.gv"
        gvNodeHierachyFilePng="${outputFolder}/${gvFileBaseName}_nodes_hierachy.png"
        gvEdgeHierachyFileName="${outputFolder}/${gvFileBaseName}_edges_hierachy.gv"
        gvEdgeHierachyFilePng="${outputFolder}/${gvFileBaseName}_edges_hierachy.png"
        schema="${outputFolder}/${gvFileBaseName}_schema.db"
        dot -Tpng $gvNodeFileName -o $gvNodeFilePng
        dot -Tpng $gvEdgeFileName -o $gvEdgeFilePng
        dot -Tpng $gvFullFileName -o $gvFullFilePng
        dot -Tpng $gvNodeHierachyFileName -o $gvNodeHierachyFilePng
        dot -Tpng $gvEdgeHierachyFileName -o $gvEdgeHierachyFilePng
#sqlite3 $schema < script/rpqView.sql
    done
done

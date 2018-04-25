#!/bin/bash
EXAMPLE_FOLDER="example"
SCRIPT_FOLDER="script"
for example in ${EXAMPLE_FOLDER}/**; do
    # input and output folders
    inputFolder="${example}/input"
    outputFolder="${example}/output"
    for filename in ${inputFolder}/*.gv; do
        python3 ${SCRIPT_FOLDER}/graphviz_parser.py $filename -config test.json 
        gvFileBaseName=$(basename $filename | cut -d"." -f1)
        echo $gvFileBaseName
        mkdir -p ${outputFolder}
        gvNodeFileName="${outputFolder}/${gvFileBaseName}_nodes.gv"
        gvNodeFilePng="${outputFolder}/${gvFileBaseName}_nodes.png"
        gvEdgeFileName="${outputFolder}/${gvFileBaseName}_edges.gv"
        gvEdgeFilePng="${outputFolder}/${gvFileBaseName}_edges.png"
        gvFullFileName="${outputFolder}/${gvFileBaseName}_full.gv"
        gvFullFilePng="${outputFolder}/${gvFileBaseName}_full.png"
        gvNodeHierarchyFileName="${outputFolder}/${gvFileBaseName}_nodes_hierarchy.gv"
        gvNodeHierarchyFilePng="${outputFolder}/${gvFileBaseName}_nodes_hierarchy.png"
        gvEdgeHierarchyFileName="${outputFolder}/${gvFileBaseName}_edges_hierarchy.gv"
        gvEdgeHierarchyFilePng="${outputFolder}/${gvFileBaseName}_edges_hierarchy.png"
        schema="${outputFolder}/${gvFileBaseName}_schema.db"
        dot -Tpng $gvNodeFileName -o $gvNodeFilePng
        dot -Tpng $gvEdgeFileName -o $gvEdgeFilePng
        dot -Tpng $gvFullFileName -o $gvFullFilePng
        dot -Tpng $gvNodeHierarchyFileName -o $gvNodeHierarchyFilePng
        dot -Tpng $gvEdgeHierarchyFileName -o $gvEdgeHierarchyFilePng
        sqlite3 $schema < script/rpqView.sql
    done
done

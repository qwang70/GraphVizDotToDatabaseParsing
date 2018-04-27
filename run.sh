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
        find ${outputFolder} -name '*.gv' | while read outputGvFile; do
            outputGvFileName=$(echo $outputGvFile | cut -d"." -f1)
            outputGvFileNamePNG="${outputGvFileName}.png"
            dot -Tpng $outputGvFile -o $outputGvFileNamePNG
        done
        schema="${outputFolder}/${gvFileBaseName}_schema.db"
        sqlite3 $schema < script/rpqView.sql
    done
done

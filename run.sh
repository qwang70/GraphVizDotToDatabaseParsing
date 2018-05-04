#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCRIPT_FOLDER="$DIR/script"

#############################
# Run Python sciprt routine #
#############################
run_gva () {
    python3 ${SCRIPT_FOLDER}/graphviz_parser.py $filename -config $CONFIG_FILE
    local gvFileBaseName=$(basename $filename | cut -d"." -f1)
    mkdir -p ${outputFolder}
    find ${outputFolder} -name '*.gv' | while read outputGvFile; do
        local outputGvFileName=$(echo $outputGvFile | cut -d"." -f1)
        local outputGvFileNamePNG="${outputGvFileName}.png"
        dot -Tpng $outputGvFile -o $outputGvFileNamePNG
    done
    local schema="${outputFolder}/${gvFileBaseName}_schema.db"
    sqlite3 $schema < "$SCRIPT_FOLDER/rpqView.sql"
}

#########################
# The command line help #
#########################
display_help() {
    echo "Usage: $0 [-h] -outFolder OUTFOLDER -config CONFIG infile" >&2
    echo
    echo "   if no option provided, the script would run through all the folder"
    echo
    echo "   infile                name of the input dot/gv file"
    echo "   -outFolder OUTFOLDER  path of the output folder"
    echo "   -config CONFIG        name of the configuration json file"
    echo
    exit 1
}

if [ "$#" -eq 0 ];then
    # variables
    EXAMPLE_FOLDER="$DIR/example"
    CONFIG_FILE="$DIR/config.json"
    # iterate all eample folders
    for example in ${EXAMPLE_FOLDER}/**; do
        echo "Begin running the example folder: '${example}'"
        # input and output folders
        inputFolder="${example}/input"
        outputFolder="${example}/output"
        for filename in ${inputFolder}/*.gv; do
            run_gva
        done
    done
else
    while :
    do
        case "$1" in
          *.gv)
              filename=$1
              shift 1
              ;;
          -outFolder)
              if [ $# -ne 0 ]; then
                outputFolder="$2"   # You may want to check validity of $2
              fi
              shift 2
              ;;
          -h | --help)
              display_help  # Call your function
              exit 0
              ;;
          -config)
              echo "in config"
              if [ $# -ne 0 ]; then
                CONFIG_FILE="$2"
              fi
              echo $CONFIG_FILE
              shift 2
              ;;

          --) # End of all options
              shift
              break
              ;;
          -*)
              echo "Error: Unknown option: $1" >&2
              ## or call function display_help
              exit 1
              ;;
          *)  # No more options
              break
              ;;
        esac
    done
    # check whether parameters are provided
    if [ -z ${filename+x} ] || [ -z ${CONFIG_FILE+x} ] || [ -z ${outputFolder+x} ]; 
    then 
        echo 
        echo "Error: Not all three parameters are provided"; 
        echo
        display_help;
        exit 1; 
    fi
    run_gva
fi

# GraphVizDotToDatabaseParsing

- Parsing the dot file with Antlr4 and Python3
```
$ python3 script/graphviz_parser.py -h
usage: graphviz_parser.py [-h] [-outfile OUTFILE] [-fca] infile

A GraphViz dot file to Sqlite idbase converter.

positional arguments:
  infile            name of the input dot/gv file

optional arguments:
  -h, --help        show this help message and exit
  -outfile OUTFILE  name of the output idbase file
  -fca
```
## Example
```
$ python3 script/graphviz_parser.py example/parleocar.gv -fca
```

To run all the examples:
```
./run.sh
```


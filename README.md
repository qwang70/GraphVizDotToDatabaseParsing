# GVA System (GV-Analyzer)

## What is GVA System

GVA System stands for Graphviz Analyer System, which consumes a Graphviz file and output the underlying feature of the graph.


### Why GVA System

Graphviz is an application for drawing graph specified in DOT script languange. It is common for many applications to generate GV files that can then be converted to PNG/PDF/SVG files with Graphviz.

Although DOT script language specifies how the graph should be drawn and output, it does not imply any structure information of a graph. Out tool reveals the underlying structure of the graph. Specifically, it classifies different types of nodes, edges, and the formal concept analysis based hierarchic structure of each type.


### Architecture Walkthrough:

- We first parsed the DOT script language with ANTLR based parser

- The parser record the attributes of each node and edge

- Based on the attributes of nodes and edges, we use formal concept analysis(FCA) to create the hierarchy of the node and edge types

- In the hierarchy graph

## Installation

1. Test the installation of Python 3 works by running the command to check the version

```
$ python3 -V
Python 3.6.4
```

2. Clone the repo to local

3. Install the requried 

```
$ pip3 install antlr4-python3-runtime concepts numpy pandas graphviz
```


## Usage

### Basic usage

```
$ python3 script/graphviz_parser.py  -h
usage: graphviz_parser.py [-h] [-outFolder OUTFOLDER] [-config CONFIG] infile

A GraphViz dot file to Sqlite idbase converter.

positional arguments:
infile                name of the input dot/gv file

optional arguments:
-h, --help            show this help message and exit
-outFolder OUTFOLDER  path of the output folder
-config CONFIG        name of the configuration json file
```

The sample example folder structure is as following:
```
- folderName
- input
- .gv file
- output
- HierarchyGraph
- edge hierarchy gv file
- nodes hierarchy gv file
- TypeGraph
- edge type gv file
- node type gv file
- combination of edge and node type relation gv file
- schema file
```

#### Example

To compute and output the  hierarchy and type graph of `paelocar.gv`:

```
$ python3 script/graphviz_parser.py example/paelocar.gv -config config.json
```

### Configure file structure

The configure file provides the flexibility to let user select the attributes and queries to be included in the final schema file.

The configure file is a json file, where it should contain one or more keys as the following

1. query
2. nodeTypeAttr
3. edgeTypeAttr

The value corresponding to each key is a list of strings. If the string is present in the list as it is, with a "+" ahead, the schema would include the value of the attribute string or query string of each node/nodeType/edgeType. If the string is present in the list with a "-" ahead, the schema would ignore it.

#### Configuration Example

```
{
"query":
    [
    "+indeg>0",
    "+outdeg>0",
    "indeg",
    "-outdeg"
    ],
"nodeTypeAttr":
    [ "fillcolor",
    "style",
    "+shape",
    "-label"],
"edgeTypeAttr":
    ["color", "style"]
}
```

The schema would include `indeg>0`, `outdeg>0` and `indeg` in `node` table, include  `fillcolor`, `style` and `shape` in `nodeType` table, and include `color` and `style` in `edgeType` table.

The sample schema file would look as following:

```
%node(nodeId, nodeTypeId, nodeName, indeg>0, outdeg>0, indeg).
node(n0, nt0, "a", false, true, 0).
node(n1, nt0, "d", true, true, 3).
...
%nodeType(nodeTypeId, fillcolor, style, shape).
nodeType(nt0, "#AAFFAA", "filled,rounded", box).
nodeType(nt1, "#FFFFAA", filled, circle).
nodeType(nt2, "#FFAAAA", filled, octagon).
%edge(edgeId, startNodeId, endNodeId, edgeTypeId).
edge(e0, n5, n2, et1).
edge(e1, n6, n4, et2).
...
%edgeType(edgeTypeId, color, style).
edgeType(et0, "#777777", dashed).
edgeType(et1, "#AAAA00", default).
...

```

#### query

There are 4 queries current are supported:

`indeg>0`/`outdeg>0`: output a boolean that represent whether the indegree/outdegree of a vertex is greater than 0.

`indeg`/`outdeg`: output an integer that represent the indegree/outdegree of a vertex.

These query are useful when we're interested distinguishing the source/sink of the graph, the internal or inidividual vertices of the graph.

#### nodeTypeAttr and edgeTypeAttr

Any node/edge attribute name support by Graphviz ([Graphviz documentation](https://www.graphviz.org/doc/info/attrs.html)) can be included in the list. For example, key `nodeTypeAttr` can have value `["fillcolor", "shape"]`.

### Convert Output gv File to PNG File

Shortcut script that runs the python scipt to generate all gv files, and convert from gv to PNG files is provided.

#### Example:

```
./run.sh example/game-provenance/input/clean_sec2-game-solved-new2.gv -outFolder example/game-provenance/output -config config.json
```

To run all the examples:
```
./run.sh
```

### Run all examples

1. [Optional] Delete all output in the repo

```
./clean.sh
```

2. run all examples

```
./run.sh
```

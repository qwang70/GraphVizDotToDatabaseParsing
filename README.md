# GVA System (GV-Analyzer)

## What is GVA System

GVA System stands for Graphviz Analyer System, which consumes a Graphviz file and output the underlying feature of the graph.


### Why GVA System

Graphviz is an application for drawing graph specified in DOT script languange. It is common for many applications to generate GV files that can then be converted to PNG/PDF/SVG files with Graphviz.

Although DOT script language specifies how the graph should be drawn and output, it does not imply any structure information of a graph. Out tool reveals the underlying structure of the graph. Specifically, it classifies different types of nodes, edges, and the formal concept analysis based hierarchic structure of each type.

### What is FCA

FCA stands for Formal concept analysis. It is useful to describe relationships between a
 set of objects and a set of attributes. In GVA System, a set of objects is a set of nodes/edges in the graphviz generated image, and a set of attributes is a set of graphviz attributes for nodes/edges. 
 
 FCA produces a concept lattice: a collection of formal concepts that are hierarchically ordered by a subconcept-superconcept relation.

### Architecture Walkthrough:

- We first parsed the DOT script language with ANTLR based parser

- The parser record the attributes of each node and edge

- Based on the attributes of nodes and edges, we use formal concept analysis(FCA) to create the hierarchy of the node and edge types

- In the hierarchy graph, the node and edge attributes are represented as a Graphviz node/edge visually.

- Different types of nodes and edges are being recognized and grouped. The node type graph and edge type graph has an instance of different types of nodes and edges that linking with the  node/edge labels in the original graph with the same type.

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
./run.sh example/PaeloCAR/input/paelocar.gv -outFolder example/PaeloCAR/output -config config.json
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

### Example Workthrough

We will work through an example using PaeloCAR example.

#### Call GVA System using `run.sh` shortcut:

```
./run.sh example/CEN_NDC/input/CEN_NDC.gv -outFolder example/CEN_NDC/output -config config.json
```

#### Check the output of GVA System

Under the output directory `example/CEN_NDC/output`,  there should be 2 schema files, one in XSB format (.txt extension), and another one in Sqlite format (.db extension). There should be two directories named "HierarchyGraph" and "TypeGraph".

##### HierarchyGraph Directory

1. Nodes Hierarchy Graph

<table style="width:100%">
    <tr>
        <th style="width:50%">CEN_NDC_nodes_hierarchy.png</th>
        <th style="width:50%">CEN_NDC_nodes_hierarchy_with_name.png</th> 
    </tr>
    <tr>
    <td>
        <p align="center">
        <img src="https://raw.githubusercontent.com/qwang70/GraphVizDotToDatabaseParsing/master/example/CEN_NDC/output/HierarchyGraph/CEN_NDC_nodes_hierarchy.png"   width="100%" title="CEN_NDC_nodes_hierarchy.png">
        </p>
    </td>
    <td>
        <p align="center">
        <img src="https://raw.githubusercontent.com/qwang70/GraphVizDotToDatabaseParsing/master/example/CEN_NDC/output/HierarchyGraph/CEN_NDC_nodes_hierarchy_with_name.png"   width="100%" title="CEN_NDC_nodes_hierarchy_with_name.png">
        </p>
    </td>
    </tr>
</table>

The nodes hierarchy graph implies that there are 109 vertices in the graphviz file in total. Among the 109 vertices, 54 of them are green and box type vertices, and 55 of them are yellow and note type vertices. These two type vertices distinguish themselves by color and shape in FCA.

2. Edges Hierarchy Graph

<table style="width:100%">
    <tr>
        <th style="width:50%">CEN_NDC_edges_hierarchy.png</th>
        <th style="width:50%">CEN_NDC_edges_hierarchy_with_name.png</th> 
    </tr>
    <tr>
    <td>
        <p align="center">
        <img src="https://raw.githubusercontent.com/qwang70/GraphVizDotToDatabaseParsing/master/example/CEN_NDC/output/HierarchyGraph/CEN_NDC_edges_hierarchy.png"  width="100%" title="CEN_NDC_edges_hierarchy.png">
        </p>
    </td>
    <td>
        <p align="center">
        <img src="https://raw.githubusercontent.com/qwang70/GraphVizDotToDatabaseParsing/master/example/CEN_NDC/output/HierarchyGraph/CEN_NDC_edges_hierarchy_with_name.png"  width="100%" title="CEN_NDC_edges_hierarchy_with_name.png">
        </p>
    </td>
    </tr>
</table>

The edges hierarchy graph implies that there are 156 edges in the graphviz file. On the left side of the edge representing all the edges, the purple dashed bi-directed edge represents 49 such type edges in the graphviz file; on the right side, the black solid edge represents 107 such type edges in the graphviz file. Among 107 black solid edges, 53 of them are directed backward, and 54 of them are directed forward. 

Notice that in the edges hierarchy graph, we don't distinguish the edge hierarchy by two nodes on the edge endpoints, but only distinguish the edge hierarchy by the property of graphviz edge itself.

##### TypeGraph Directory

1. Nodes and Edges Type Graph: Nodes Type Graph lists 2 types of nodes, and Edges Type Graph lists 3 types of nodes and edges relationships.
<table style="width:100%">
    <tr>
        <th style="width:50%">CEN_NDC_nodes.png</th>
        <th style="width:50%">CEN_NDC_edges.png</th> 
    </tr>
    <tr>
        <td>
            <p align="center">
            <img src="https://raw.githubusercontent.com/qwang70/GraphVizDotToDatabaseParsing/master/example/CEN_NDC/output/TypeGraph/CEN_NDC_nodes.png"  width="100%" title="CEN_NDC_edges.png">
            </p>
        </td>
        <td>
            <p align="center">
            <img src="https://raw.githubusercontent.com/qwang70/GraphVizDotToDatabaseParsing/master/example/CEN_NDC/output/TypeGraph/CEN_NDC_edges.png"  width="100%" title="CEN_NDC_edges.png">
            </p>
        </td>
    </tr>
</table>

2. Composite Type Graph: The composite type graph combines the two types of nodes, and three types of edge relations into one graph. A green box node can direct to a green box node by a backward edge; a yellow note-shape node can direct to a yellow note-shape node by a forward edge; a green box node and a yellow note-shape node can be bi-directed with a purple dashed edge.

![full_graph](https://raw.githubusercontent.com/qwang70/GraphVizDotToDatabaseParsing/master/example/CEN_NDC/output/TypeGraph/CEN_NDC_full.png)

## Reference

Belohlavek, Radim. "Introduction to formal concept analysis." *Palacky University, Department of Computer Science, Olomouc* (2008): 47.

Shrivastava, Pratik. Wt-Prov-Summer-2017, (2017), GitHub repository, https://github.com/idaks/wt-prov-summer-2017.

Cheng, Jessica. EulerProject, (2017), GitHub repository, https://github.com/EulerProject/ASIST17.

Ludaescher, Bertram. Which one doesn't belong, GitHub repository, https://github.com/ludaesch/wodb.

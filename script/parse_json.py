import json 
import sys
nodeAttrSet = {"indeg>0", "outdeg>0", "indeg", "outdeg"}
nodeTypeAttrSet = {"fillcolor", "style", "shape", \
    "label", "fontsize", "width", "fontname", "height"}
edgeTypeAttrSet = {"style",  \
    "color", "label", "fontsize", "penwidth", "fontname", "pensize",\
    }

def parse_json(filename):
    with open(filename, 'r') as stream:
        json_obj = json.load(stream)

    includeNA = []
    excludeNA = []
    includeNTA = []
    excludeNTA = []
    includeETA = []
    excludeETA = []

    if "nodeAttr" in json_obj:
        for attr in json_obj["nodeAttr"]:
            if attr:
                if attr[0] == "+" and attr[1:] in nodeAttrSet:
                    includeNA.append(attr[1:])
                elif attr[0] == "-" and attr[1:] in nodeAttrSet:
                    excludeNA.append(attr[1:])
                elif attr in nodeAttrSet:
                    includeNA.append(attr)
    if "nodeTypeAttr" in json_obj:
        for attr in json_obj["nodeTypeAttr"]:
            if attr:
                if attr[0] == "+" and attr[1:] in nodeTypeAttrSet:
                    includeNTA.append(attr[1:])
                elif attr[0] == "-" and attr[1:] in nodeTypeAttrSet:
                    excludeNTA.append(attr[1:])
                elif attr in nodeTypeAttrSet:
                    includeNTA.append(attr)
    if "edgeTypeAttr" in json_obj:
        for attr in json_obj["edgeTypeAttr"]:
            if attr:
                if attr[0] == "+" and attr[1:] in edgeTypeAttrSet:
                    includeETA.append(attr[1:])
                elif attr[0] == "-" and attr[1:] in edgeTypeAttrSet:
                    excludeETA.append(attr[1:])
                elif attr in edgeTypeAttrSet:
                    includeETA.append(attr)
    return {"nodeTypeAttr": {"include": includeNTA, "exclude": excludeNTA},\
            "edgeTypeAttr": {"include": includeETA, "exclude": excludeETA},\
            "nodeAttr" : {"include": includeNA, "exclude": excludeNA}}




from concepts import Context
import pandas as pd
import numpy as np
class FCA(object):
    def __init__(self, propertyList):
        # get objs and attrs
        index = [elem.get_name() for elem in propertyList]
        attrs = set()
        for elem in propertyList:
            currAttr = elem.getAttr() 
            for key, val in currAttr.items():
                if key.lower() != "label" and \
                    "{}={}".format(key,val) not in attrs:
                    attrs.add("{}={}".format(key,val))
        # create FCA
        self.fca = pd.DataFrame(index=index, columns=attrs)
        self.fca = self.fca.fillna("") # with 0s rather than NaNs
        for elem in propertyList:
            currAttr = elem.getAttr() 
            for key, val in currAttr.items():
                if key.lower() != "label":
                    self.fca.loc[[elem.get_name()], "{}={}".format(key,val)] = "X"
        ctx_string = self.fca.to_csv()
        self.ctx = Context.fromstring(ctx_string,frmat='csv')
        #dot = self.ctx.lattice.graphviz(filename="fca", view=True)
        self.createNodesGraphviz()

    def createNodesGraphviz(self):
        nodesdot = ""
        atoms = self.ctx.lattice.atoms
        for nid, atom in enumerate(atoms):
            nodesdot += "n{} [{}, label=\"{}\"]\n".format(\
                    nid, ", ".join(atom.intent),\
                    "\n".join(atom.extent).replace('\"', '\\\"') )
                    #"\n".join(atom.intent).replace('\"', '\\\"'))
        dot =   \
        """
        graph{{
            {}
        }}
        """.format(nodesdot)
        with open('nodetype.dot', 'w') as file:
            file.write(dot)
            





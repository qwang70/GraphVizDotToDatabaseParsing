#!/usr/bin/env python3
# fcaVisualize.py - convert lattice to graphviz dot

import os
import glob

import graphviz

__all__ = ['lattice']

SORTKEYS = [lambda c: c.index]

NAME_GETTERS = [lambda c: 'c%d' % c.index]


def lattice(lattice, filename, directory, isEdge, showLabel, **kwargs):
    """Return graphviz source for visualizing the lattice graph."""
    dot = graphviz.Digraph(
        name=lattice.__class__.__name__,
        comment=repr(lattice),
        filename=filename,
        directory=directory,
        node_attr=dict(shape='circle', width='.25', style='filled', label=''),
        edge_attr=dict(dir='none', labeldistance='1.5', minlen='2'),
        **kwargs
    )

    sortkey = SORTKEYS[0]

    node_name = NAME_GETTERS[0]

    for concept in lattice._concepts:
        # pack labels into a dicionary
        # if " appears in the label, replace it with empty string
        node_attr = {}
        node_attr["label"] = str(len(concept.extent))
        for key, val in (intent.split('=', maxsplit=1) for intent in concept.intent):
            if key in node_attr:
                node_attr[key] = ""
            else:
                node_attr[key] = val.replace("\"","")

        name = node_name(concept)
        # draw cluster
        with dot.subgraph(name='cluster_{}'.format(sortkey(concept))) as c:

            if not isEdge:
                # node hierachy
                c.attr(color='transparent')
                c.node(name, _attributes=node_attr)
            else:
                # edge hierachy
                c.attr(color='blue')
                c.node('{}_start'.format(name))
                c.node('{}_end'.format(name))
                c.node(name, style="invis")
                c.edge('{}_start'.format(name), '{}_end'.format(name), \
                        _attributes=node_attr)
                c.edge('{}_start'.format(name), name, style="invis")
                c.edge('{}_end'.format(name),name, style="invis")

                s = graphviz.Digraph('subgraph')
                s.graph_attr.update(rank='same')

                s.node('{}_start'.format(name))
                s.node(name)

        # draw edge with label
        if showLabel and concept.objects:
            labels = [lbl.split(":")[-1] for lbl in concept.objects]
            dot.edge(name,name,
                label='\t\n'.join(labels),
                labelangle='270', color='transparent')

        dot.edges((name, node_name(c))
            for c in sorted(concept.lower_neighbors, key=sortkey))
    return dot

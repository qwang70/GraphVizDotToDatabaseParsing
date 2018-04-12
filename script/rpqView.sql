DROP VIEW IF EXISTS rpqView;
CREATE VIEW rpqView
AS 
SELECT 
n1.nodeName AS startNode, n2.nodeName AS endNode, edgeTypeId AS label
FROM edge
INNER JOIN node n1 ON n1.nodeId = edge.startNode
INNER JOIN node n2 ON n2.nodeId = edge.endNode;


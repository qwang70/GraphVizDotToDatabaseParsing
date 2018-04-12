CREATE VIEW rpqView
AS 
SELECT 
startNodeId AS startNode, endNodeId AS endNode, edgeTypeId AS label
FROM edge;
/*INNER JOIN node n1 ON n1.nodeId = edge.startNode
INNER JOIN node n2 ON n2.nodeId = edge.endNode;
*/

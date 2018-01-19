# GraphVizDotToDatabaseParsing

- Parsing the dot file with Antlr4 and Python3
- Generate a SQLite database from the Tree representation of the parsed dot file
```
$ python3 graphviz_parser.py test.dot
$ python3 graphviz_parser.py test.dot -outfile test.db
```
Both parse `test.dot` and generate `test.db`.

There are two tables in test.db

Table: tokens
column name | data type 
--- | --- 
id | integer primary key
token_type | text
token_val | text

Table: token_tree
column name | data type 
----------- | --------- 
id          | integer
parent_id   | integer
child_id    | integer

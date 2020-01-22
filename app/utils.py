import sqlite3
from flask import url_for



# sqlite db connection
def db_connect(arg=None):
    con = sqlite3.connect('app/database.db')
    if not arg:
        con.row_factory = sqlite3.Row
        return con
    elif arg == 'update':
        return con
    else:
        return 'error'


# had problems with serializing object, both with alchemy & sqlite. 
# (data) Solution below from https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
# turned above solution into a function for reusability
def serialize(cur, result):
    data = [dict(zip([key[0] for key in cur.description], row)) for row in result]
    return data



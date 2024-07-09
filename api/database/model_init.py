db = None 

def init_db(sql_alchemy_db):
    global db
    db = sql_alchemy_db
    
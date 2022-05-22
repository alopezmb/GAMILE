class RamenVisitor:
    def __init__(self, db_object):
        self.id = db_object['_id']
        self.username = db_object['username']
        self.score = db_object['score']
        self.time = db_object['time']


class DbRouter:

    def __init__(self, db):
        self.db = db

    def db_for_read(self, model, **hints):
        return self.db
    
    def db_for_write(self, model, **hints):
        return self.db
    
    def allow_relation(self, obj1, obj2, **hints):
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return self.db == db

class LocalRouter(DbRouter):
    def __init__(self):
        super().__init__('local')

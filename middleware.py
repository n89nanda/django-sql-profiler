from django.db import connection
from models import SQLProfile
from django.conf import settings

default = {"ignores": ["/admin",]}
config = getattr(settings, "DJANGO_SQL_PROFILER", default)

class ProfileMiddleware(object):
    def process_response(self, request, response):
        url = request.get_full_path()
        for ignore in config["ignores"]:
            if url.startswith(ignore):
                return response
                
        for query in connection.queries[:1]:
            sql = SQLProfile()
            sql.millisecond = float(query["time"])
            sql.sql = query["sql"]
            sql.params = query["params"]
            sql.hash = query["hash"]
            sql.url = request.get_full_path()
            sql.save()
            
        return response

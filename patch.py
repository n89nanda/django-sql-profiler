import os
import time
import SocketServer
import traceback
import django

from django.db import models
from django.db import connection
from django.db.backends import util
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.hashcompat import sha_constructor
from django.conf import settings

# Figure out some paths
django_path = os.path.realpath(os.path.dirname(django.__file__))
socketserver_path = os.path.realpath(os.path.dirname(SocketServer.__file__))

def tidy_stacktrace(strace):
    """
    Clean up stacktrace and remove all entries that:
    1. Are part of Django (except contrib apps)
    2. Are part of SocketServer (used by Django's dev server)
    3. Are the last entry (which is part of our stacktracing code)
    """
    trace = []
    for s in strace[:-1]:
        s_path = os.path.realpath(s[0])
        if django_path in s_path and not 'django/contrib' in s_path:
            continue
        if socketserver_path in s_path:
            continue
        trace.append((s[0], s[1], s[2], s[3]))
    return trace

class DatabaseStatTracker(util.CursorDebugWrapper):
    """ Ripped from django debug toolbar """
    def execute(self, sql, params=()):
        start = time.time()
        try:
            return self.cursor.execute(sql, params)
        finally:
            stop = time.time()
            stacktrace = tidy_stacktrace(traceback.extract_stack())
            _params = ''
            try:
                _params = simplejson.dumps([force_unicode(x) for x in params])
            except TypeError:
                pass # object not JSON serializable
            # We keep `sql` to maintain backwards compatibility
            self.db.queries.append({
                'sql': self.db.ops.last_executed_query(self.cursor, sql, params),
                'time': (stop - start) * 1000, # convert to ms
                'raw_sql': sql,
                'params': _params,
                'hash': sha_constructor(settings.SECRET_KEY + sql + _params).hexdigest(),
                'stacktrace': stacktrace,
            })
            
util.CursorDebugWrapper = DatabaseStatTracker
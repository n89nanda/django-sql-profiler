from django.db import models

class SQLProfile(models.Model):
    """ A SQL Profile class """
    sql = models.TextField()
    millisecond = models.FloatField()
    hash = models.CharField(max_length=32)
    params = models.TextField()
    url = models.URLField()
    
    def __unicode__(self):
        return str(self.id)
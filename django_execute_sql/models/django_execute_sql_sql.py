__all__ = ['Sql',]


from django.db import models

class Sql(models.Model):
    name = models.CharField(unique=True,max_length=255)
    sql = models.TextField()
    success = models.BooleanField(null=True,editable=False)

    updated_at = models.DateTimeField(null=True,editable=False,verbose_name="updated")

    class Meta:
        db_table = __name__.split('.')[-1]
        ordering = ('-updated_at',)

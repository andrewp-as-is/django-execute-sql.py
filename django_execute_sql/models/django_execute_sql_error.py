__all__ = ['Error',]


from django.db import models

class Error(models.Model):
    sql = models.TextField(null=True,editable=False)
    exc_type = models.TextField(editable=False,verbose_name="type")
    exc_value = models.TextField(editable=False,verbose_name="value")
    exc_traceback = models.TextField(editable=False,verbose_name="traceback")
    created_at = models.DateTimeField(auto_now_add=True,editable=False,verbose_name="created")

    class Meta:
        db_table = __name__.split('.')[-1]
        ordering = ('-created_at',)

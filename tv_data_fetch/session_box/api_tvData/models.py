from django.db import models

# Create your models here.

class PriceRecord(models.Model):
    symbol = models.CharField(max_length=50)
    date = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.symbol} - {self.date}"

    class Meta:
        ordering = ['-date']
        unique_together = ('symbol', 'date')

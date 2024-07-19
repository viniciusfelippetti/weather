from django.db import models

# Create your models here.

class Estacao(models.Model):
    nome_estacao = models.CharField(max_length=150)
    latitude = models.CharField(max_length=13)
    longitude = models.CharField(max_length=13)

class HistoricoEstacao(models.Model):
    estacao = models.ForeignKey(Estacao, on_delete=models.CASCADE, null=True, blank=True)
    data_hora = models.DateTimeField()
    bateria = models.FloatField()
    nivRegua = models.IntegerField()
    pluvio = models.IntegerField()



import datetime

from django.db import models

# Create your models here.

class Estacao(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    nome_estacao = models.CharField(max_length=150)
    latitude = models.CharField(max_length=13)
    longitude = models.CharField(max_length=13)

    def __str__(self):
        return f"{self.nome_estacao} ({self.id})"

class HistoricoEstacao(models.Model):
    estacao = models.ForeignKey(Estacao, on_delete=models.CASCADE, null=True, blank=True)
    data = models.DateField()
    hora = models.TimeField(default=datetime.time(10, 0))
    precipitacao = models.FloatField()
    pressao = models.FloatField()
    pressao_maxima = models.FloatField()
    pressao_minima = models.FloatField()
    radiacao = models.FloatField()
    temperatura = models.FloatField()
    temperatura_minima = models.FloatField()
    temperatura_maxima = models.FloatField()
    umidade = models.FloatField()
    umidade_minima = models.FloatField()
    umidade_maxima = models.FloatField()
    vento_rajada_maxima = models.FloatField()
    vento_velocidade_horaria = models.FloatField()

    def __str__(self):
        return f"{self.estacao} - {self.data} - {self.hora}"



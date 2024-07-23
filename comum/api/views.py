from datetime import timedelta

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from comum.api.serializers import EstacaoSerializer, HistoricoEstacaoSerializer
from comum.models import Estacao, HistoricoEstacao


class CreateHistoricoEstacaoViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]
    queryset = HistoricoEstacao.objects.all()
    serializer_class = HistoricoEstacaoSerializer

    def create(self, request, *args, **kwargs):
        estacao = get_object_or_404(Estacao, id=request.data["estacao"])
        serializer = HistoricoEstacaoSerializer(data=request.data)
        serializer.estacao = estacao
        if serializer.is_valid():
            serializer.save()
            response_data = {**serializer.data}
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class HistoricoEstacaoView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = HistoricoEstacaoSerializer

    def get_queryset(self):
        estacao_id = self.kwargs['estacao_pk']
        return HistoricoEstacao.objects.filter(estacao_id=estacao_id)

class EstacaoViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Estacao.objects.all()
    serializer_class = EstacaoSerializer


class PredictTimeSeriesView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        estacao_id = self.kwargs.get('estacao_pk')
        previsao_periodo = int(request.query_params.get('periodo', 30))  # Número de dias para previsão

        try:
            estacao = Estacao.objects.get(pk=estacao_id)
        except Estacao.DoesNotExist:
            return Response({'detail': 'Estação não encontrada.'}, status=404)

        # Buscar dados históricos para a estação escolhida
        historico = HistoricoEstacao.objects.filter(estacao=estacao).order_by('data')
        if not historico.exists():
            return Response({'detail': 'Nenhum dado histórico disponível para a estação.'}, status=404)

        # Preparar os dados para o ARIMA
        data = list(historico.values(
            'data', 'precipitacao', 'pressao', 'pressao_maxima', 'pressao_minima', 'radiacao',
            'temperatura', 'temperatura_minima', 'temperatura_maxima', 'umidade',
            'umidade_minima', 'umidade_maxima', 'vento_rajada_maxima', 'vento_velocidade_horaria'
        ))
        df = pd.DataFrame(data)
        df.set_index('data', inplace=True)
        df.index = pd.to_datetime(df.index)
        # Garantir frequência diária

        # Filtrar apenas valores positivos
        df = df.applymap(lambda x: x if x > 0 else np.nan)
        df = df.fillna(method='ffill')

        # Função para treinar o modelo e fazer previsões
        def forecast_arima(series, steps):
            model = ARIMA(series, order=(5, 1, 0))  # (p,d,q) podem ser ajustados conforme necessário
            model_fit = model.fit()
            return model_fit.forecast(steps=steps)

        # Fazer previsões para cada parâmetro
        previsoes = {}
        parametros = ['precipitacao', 'pressao', 'pressao_maxima', 'pressao_minima', 'radiacao',
                      'temperatura', 'temperatura_minima', 'temperatura_maxima', 'umidade',
                      'umidade_minima', 'umidade_maxima', 'vento_rajada_maxima', 'vento_velocidade_horaria']

        for parametro in parametros:
            previsoes[parametro] = forecast_arima(df[parametro], previsao_periodo).tolist()

        # Preparar as datas de previsão
        last_date = df.index[-1]
        forecast_dates = [last_date + timedelta(days=i) for i in range(1, previsao_periodo + 1)]

        # Formatar a resposta
        response = {
            'datas': [date.strftime('%Y-%m-%d') for date in forecast_dates],
            'previsoes': previsoes
        }

        return Response(response, status=200)
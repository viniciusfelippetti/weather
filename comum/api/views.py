from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from comum.api.serializers import EstacaoSerializer, HistoricoEstacaoSerializer
from comum.models import Estacao, HistoricoEstacao


class HistoricoEstacaoViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = HistoricoEstacao.objects.all()
    serializer_class = HistoricoEstacaoSerializer

class EstacaoViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Estacao.objects.all()
    serializer_class = EstacaoSerializer

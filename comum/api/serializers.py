from rest_framework import serializers

from comum.models import Estacao, HistoricoEstacao


class HistoricoEstacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoEstacao
        fields = '__all__'

class EstacaoSerializer(serializers.ModelSerializer):
    historico_estacao = HistoricoEstacaoSerializer(many=True, write_only=True)

    class Meta:
        model = Estacao
        fields = ['id', 'nome_estacao', 'latitude', 'longitude', 'historico_estacao']

    def create(self, validated_data):
        historico_data = validated_data.pop('historico_estacao', [])
        estacao = Estacao.objects.create(**validated_data)
        for historico in historico_data:
            HistoricoEstacao.objects.create(estacao=estacao, **historico)
        return estacao

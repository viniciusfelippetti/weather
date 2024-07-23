from rest_framework import serializers

from comum.models import Estacao, HistoricoEstacao


class HistoricoEstacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoEstacao
        fields = [
            'estacao', 'data', 'hora', 'precipitacao', 'pressao', 'pressao_maxima', 'pressao_minima',
            'radiacao', 'temperatura', 'temperatura_minima', 'temperatura_maxima',
            'umidade', 'umidade_minima', 'umidade_maxima', 'vento_rajada_maxima',
            'vento_velocidade_horaria'
        ]

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

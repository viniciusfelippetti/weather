from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenVerifyView

from comum.api.views import EstacaoViewSet, HistoricoEstacaoViewSet

router = routers.DefaultRouter()
router.register(r'estacao', EstacaoViewSet)
router.register(r'historico-estacao', HistoricoEstacaoViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

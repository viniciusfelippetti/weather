from django.urls import include, path, re_path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenVerifyView, TokenObtainPairView, TokenRefreshView

from comum.api.views import *

router = routers.DefaultRouter()
router.register(r'estacao', EstacaoViewSet)
router.register(r'historico', CreateHistoricoEstacaoViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'estacao/(?P<estacao_pk>[\w-]+)/historico/', HistoricoEstacaoView.as_view(), name='historico-estacao'),
    # path('estacao/<str:estado_pk>/historico/create/', CreateHistoricoEstacaoView.as_view({'post': 'create'}),
    #      name='create-historico-estacao'),
    path('api/predict-time-series/<str:estacao_pk>/', PredictTimeSeriesView.as_view(), name='predict-time-series'),
]

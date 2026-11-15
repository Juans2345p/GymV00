from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.HomeView.as_view(), name='home'),
    path('nfc/', views.NfcListView.as_view(), name='nfc_list'),
    path('nfc/nuevo/', views.NfcCreateView.as_view(), name='nfc_create'),
    path('nfc/<int:pk>/eliminar/', views.NfcDeleteView.as_view(), name='nfc_delete'),
    path('usuarios/', views.UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/nuevo/', views.UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuarios/<int:pk>/', views.UsuarioDetailView.as_view(), name='usuario_detail'),
    path('usuarios/<int:pk>/eliminar/', views.UsuarioDeleteView.as_view(), name='usuario_delete'),
    path('identificaciones/', views.IdentificacionListView.as_view(), name='identificacion_list'),
    path('identificaciones/nueva/', views.IdentificacionCreateView.as_view(), name='identificacion_create'),
    path('identificaciones/<int:pk>/eliminar/', views.IdentificacionDeleteView.as_view(), name='identificacion_delete'),
    path('mensualidades/', views.MensualidadListView.as_view(), name='mensualidad_list'),
    path('mensualidades/nueva/', views.MensualidadCreateView.as_view(), name='mensualidad_create'),
    path('mensualidades/<int:pk>/eliminar/', views.MensualidadDeleteView.as_view(), name='mensualidad_delete'),
    path('rachas/', views.RachaListView.as_view(), name='racha_list'),
    path('rachas/nueva/', views.RachaCreateView.as_view(), name='racha_create'),
    path('rachas/<int:pk>/eliminar/', views.RachaDeleteView.as_view(), name='racha_delete'),
    path('mqtt/', views.mqtt_config_view, name='mqtt_config'),
    path('mqtt/status/', views.mqtt_status_api, name='mqtt_status'),
]
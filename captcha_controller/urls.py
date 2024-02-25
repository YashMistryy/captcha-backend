from django.contrib import admin
from django.urls import path , include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static

unique_root = 'server/'

urlpatterns = [
    path(unique_root+'admin/', admin.site.urls),
    path(unique_root+'api/',include("game.urls")),
    path(unique_root+'user/',include("users.urls")),
    path(unique_root+'api-auth/', include('rest_framework.urls')),
    path(unique_root+'api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(unique_root+'token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]+  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

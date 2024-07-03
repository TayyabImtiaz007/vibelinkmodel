from django.contrib import admin
from django.urls import include, path
from rest_framework_swagger.views import get_swagger_view
from django.conf import settings
from django.conf.urls.static import static  # Import this

schema_view = get_swagger_view(title='JacobRyan API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/docs', schema_view),
    path('api/excerpt/', include('excerpt.urls')),
    path('chatbot/', include('chatbot.urls')),  # Ensure this line exists
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


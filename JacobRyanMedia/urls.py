from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import TemplateView
from excerpt.views import chatbot_view  # Import the chatbot_view

schema_view = get_schema_view(
    openapi.Info(
        title="JacobRyan API",
        default_version='v1',
        description="API documentation for JacobRyanMedia project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourdomain.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)




urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/excerpt/', include('excerpt.urls')),
    path('chatbot/', chatbot_view, name='chatbot'),  # Add this line
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/', admin.site.urls),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/excerpt/', include('excerpt.urls')),  # This should include the excerpt URLs correctly
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

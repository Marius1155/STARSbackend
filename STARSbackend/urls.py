# STARSbackend/urls.py
from django.contrib import admin
from django.urls import path, include # Make sure 'include' is imported
from STARS.graphql.schema import schema

def graphql_view():
    # This import is now safe because django.setup() has already run
    from strawberry.django.views import AsyncGraphQLView
    return AsyncGraphQLView.as_view(
        schema=schema,
        allow_introspection=True
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', graphql_view()),
    # Add this line for allauth
    path('accounts/', include('allauth.urls')),
]

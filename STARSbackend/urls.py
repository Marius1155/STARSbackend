from django.contrib import admin
from django.urls import path
from STARS.graphql.schema import schema

def graphql_view():
    from strawberry.django.views import AsyncGraphQLView
    return AsyncGraphQLView.as_view(schema=schema)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', graphql_view()),
]
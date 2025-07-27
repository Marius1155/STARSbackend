"""
URL configuration for STARSbackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# STARSbackend/urls.py

from django.contrib import admin
from django.urls import path
# DO NOT import the view at the top level
from STARS.graphql.schema import schema

# We define a function to delay the import of AsyncGraphQLView
def graphql_view():
    from strawberry_django.views import AsyncGraphQLView
    return AsyncGraphQLView.as_view(schema=schema)

urlpatterns = [
    path('admin/', admin.site.urls),
    # By calling the function here, the import only happens when Django
    # is building the URL patterns, by which point everything is loaded.
    path('graphql/', graphql_view()),
]
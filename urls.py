from django.urls import path, include

urlpatterns = [
    path('', include(('AssnDestinationsMyApp.urls', 'AssnDestinationsMyApp'))),

]

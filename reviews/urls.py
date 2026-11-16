#app urls

from django.urls import path
from django.http import HttpResponse
from . import views # from . meaning from the same folder as this file

app_name = 'reviews'
#url list
urlpatterns = [
    #http://localhost:8000/reviews/review/new
    path('review/new', views.addreview, name='review-add'),
    #http://localhost:8000/reviews/review/2
    path('review/<int:pk>', views.detailreview, name='review-detail'),
    #http://localhost:8000/reviews/review/2/edit
    path('review/<int:pk>/edit', views.updatereview, name='review-update'),
    #http://localhost:8000/reviews/review/2/delete
    path('review/<int:pk>/delete', views.deletereview, name='review-delete'), # type: ignore

]
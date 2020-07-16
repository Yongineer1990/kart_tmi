from django.urls import path
from .views import (
    CommentView,
    RankDetailView
)

urlpatterns = [
    path('/comment/<str:user_id>', CommentView.as_view()),
    path('/detail/<str:access_id>', RankDetailView.as_view())
]

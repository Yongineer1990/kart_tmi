from django.urls import path
from .views import (
    CommentView,
    RankDetailView,
    IndiRankListView,
    TeamRankListView
)

urlpatterns = [
    path('/comment/<str:user_id>', CommentView.as_view()),
    path('/detail/<str:access_id>', RankDetailView.as_view()),
    path('/indiranklist', IndiRankListView.as_view()),
    path('/teamranklist', TeamRankListView.as_view())
]

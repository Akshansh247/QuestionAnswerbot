from django.urls import path

from .views import (
    QuizView,
    TopicQuizView,
    UserView,
    TopicView,
    RatingView,
    RecommendView,
)


urlpatterns = [
    path("user/", UserView.as_view(), name="user"),
    path("topic/", TopicView.as_view(), name="topic"),
    path("quiz/", QuizView.as_view(), name="quiz"),
    path("quizes/", TopicQuizView.as_view(), name="quiz"),
    path("rating/", RatingView.as_view(), name="rating"),
    path("recommend/", RecommendView.as_view(), name="recommend"),
]

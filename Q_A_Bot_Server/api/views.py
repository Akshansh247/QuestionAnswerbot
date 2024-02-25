import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

from django.shortcuts import render


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Quiz, Rating, Topic, User

from .serializers import (
    QuizSerializer,
    TopicSerializer,
    UserSerializer,
    RatingSerializer,
    QuizMiniSerializer,
)

# Create your views here.


class UserView(APIView):
    def get(self, request, *args, **kwargs):

        usertype = request.data["usertype"]
        if usertype == 0:
            tgid = request.data["tgid"]
            try:
                user = User.objects.get(usertype=usertype, tgid=tgid)
            except:
                return Response()
        if usertype == 1:
            disid = request.data["disid"]
            try:
                user = User.objects.get(usertype=usertype, disid=disid)
            except:
                return Response(data={})
        s = UserSerializer(user)
        return Response(s.data)

    def post(self, request, *args, **kwargs):
        s = UserSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors)


class TopicView(APIView):
    def get(self, request, *args, **kwargs):

        topics = Topic.objects.all()
        s = TopicSerializer(topics, many=True)
        return Response(s.data)

    def post(self, request, *args, **kwargs):
        s = TopicSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors)


class QuizView(APIView):
    def get(self, request, *args, **kwargs):

        quiz = Quiz.objects.get(id=request.data["id"])
        s = QuizSerializer(quiz)
        return Response(s.data)

    def post(self, request, *args, **kwargs):
        s = QuizSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors)


class TopicQuizView(APIView):
    def get(self, request, *args, **kwargs):
        if "id" in request.data:
            id = request.data["id"]
            topic = Topic.objects.get(id=id)
        elif "name" in request.data:
            name = request.data["name"]
            topic = Topic.objects.get(name=name)
        else:
            return Response()
        quizes = topic.quiz.all()
        # quizes = Quiz.objects.all(topic=request.data["topic"])
        s = QuizSerializer(quizes, many=True)
        return Response(s.data)


class RatingView(APIView):
    def get(self, request, *args, **kwargs):

        quiz = request.data["quiz"]
        user = request.data["user"]
        try:
            rating = Rating.objects.get(quiz=quiz, user=user)
        except:
            return Response()
        s = RatingSerializer(rating)
        return Response(s.data)

    def post(self, request, *args, **kwargs):

        quiz = request.data["quiz"]
        user = request.data["user"]
        value = request.data["value"]
        rating = Rating.objects.get(quiz=quiz, user=user)
        s = RatingSerializer(rating, data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors)


def get_recommendation(topic_id, quiz_id):
    topic = Topic.objects.get(id=topic_id)
    quizes = topic.quiz.all()
    ratings = Rating.objects.filter(quiz__in=quizes)
    ratings_df = pd.DataFrame(ratings.values())
    ratings_pdf = ratings_df.pivot(index="quiz_id", columns="user_id", values="value")
    csr_data = csr_matrix(ratings_pdf.values)
    knn = NearestNeighbors(
        metric="cosine", algorithm="brute", n_neighbors=20, n_jobs=-1
    )
    knn.fit(csr_data)
    ratings_pdf.reset_index(inplace=True)

    n_quiz_to_recommend = 3

    # print(ratings_pdf)
    # print(ratings_pdf["quiz_id"])
    quiz_idx = ratings_pdf[ratings_pdf["quiz_id"] == quiz_id].index[0]

    distances, indices = knn.kneighbors(
        csr_data[quiz_idx], n_neighbors=n_quiz_to_recommend + 1
    )
    rec_quiz_indices = sorted(
        list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())),
        key=lambda x: x[1],
    )[:0:-1]
    rec_quizes = []
    for val in rec_quiz_indices:
        quiz_idx = ratings_pdf.iloc[val[0]]["quiz_id"]
        rec_quizes.append(int(quiz_idx))
    return rec_quizes


class RecommendView(APIView):
    def get(self, request, *args, **kwargs):
        topic_id = request.data["topic_id"]
        quiz_id = request.data["quiz_id"]
        rec_quizes = get_recommendation(topic_id, quiz_id)
        quizes = Quiz.objects.filter(id__in=rec_quizes)
        s = QuizMiniSerializer(quizes, many=True)
        return Response(s.data)

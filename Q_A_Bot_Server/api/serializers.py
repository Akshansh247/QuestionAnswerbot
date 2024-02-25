from rest_framework import serializers


from .models import Question, Quiz, Topic, User, Rating


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"


class QuizSerializer(serializers.ModelSerializer):
    topic_info = TopicSerializer(source="topic")
    creator_info = UserSerializer(source="creator")
    question = QuestionSerializer(many=True)
    avg_rating = serializers.SerializerMethodField("get_avg_rating")

    def get_avg_rating(self, quiz):
        ratings = quiz.quiz_rating.all()
        n = len(ratings)
        sum = 0.0
        for rating in ratings:
            sum += rating.value
        try:
            avg = sum / n
        except:
            avg = 0.0
        return avg

    class Meta:
        model = Quiz
        fields = ("id", "topic_info", "creator_info", "question", "avg_rating")


class QuizMiniSerializer(serializers.ModelSerializer):
    topic_info = TopicSerializer(source="topic")
    creator_info = UserSerializer(source="creator")
    avg_rating = serializers.SerializerMethodField("get_avg_rating")

    def get_avg_rating(self, quiz):
        ratings = quiz.quiz_rating.all()
        n = len(ratings)
        sum = 0.0
        for rating in ratings:
            sum += rating.value
        try:
            avg = sum / n
        except:
            avg = 0.0
        return avg

    class Meta:
        model = Quiz
        fields = ("id", "topic_info", "creator_info", "avg_rating")

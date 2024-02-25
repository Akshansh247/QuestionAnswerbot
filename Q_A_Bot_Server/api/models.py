from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class User(models.Model):
    USER_TYPE = ((0, "Telegram"), (1, "Discord"))
    name = models.CharField(max_length=200, blank=True, null=True)
    usertype = models.IntegerField(choices=USER_TYPE)
    tgid = models.IntegerField(default=0, blank=True, null=True)
    disid = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("usertype", "tgid", "disid")


class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Quiz(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="quiz")
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, default=1, related_name="quiz"
    )

    def __str__(self):
        return f"ID: {self.id}, TOPIC: {self.topic}, CREATOR: {self.creator}"


class Question(models.Model):
    OPTIONS = ((0, 0), (1, 1), (2, 2), (3, 3))
    question = models.TextField()
    option0 = models.TextField()
    option1 = models.TextField()
    option2 = models.TextField()
    option3 = models.TextField()
    correct = models.IntegerField(choices=OPTIONS)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="question")

    def __str__(self):
        return self.question


class Rating(models.Model):
    value = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="quiz_rating")

    class Meta:
        unique_together = ("user", "quiz")

    def __str__(self):
        return f"By: {self.user}, QUIZ: {self.quiz.id}, {self.value}"

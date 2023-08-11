import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Play, Performance, TheatreHall, Genre, Actor
from theatre.serializers import PlayListSerializer, PlayDetailSerializer

PLAY_URL = reverse("theatre:play-list")
PERFORMANCE_URL = reverse("theatre:performance-list")


def sample_play(**params):
    defaults = {
        "title": "Sample play",
        "description": "Sample description",
    }
    defaults.update(params)

    return Play.objects.create(**defaults)


def sample_performance(**params):
    theatre_hall = TheatreHall.objects.create(
        name="Green Theatre", rows=30, seats_in_row=30
    )

    defaults = {
        "show_time": "2023-09-02 19:30:00",
        "play": None,
        "theatre_hall": theatre_hall,
    }
    defaults.update(params)

    return Performance.objects.create(**defaults)


def detail_url(play_id):
    return reverse("theatre:play-detail", args=[play_id])


class UnauthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_movies(self):
        sample_play()
        sample_play()

        res = self.client.get(PLAY_URL)

        plays = Play.objects.order_by("id")
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_plays_by_genres(self):
        genre1 = Genre.objects.create(name="Genre 1")
        genre2 = Genre.objects.create(name="Genre 2")

        play1 = sample_play(title="Play 1")
        play2 = sample_play(title="Play 2")

        play1.genres.add(genre1)
        play2.genres.add(genre2)

        play3 = sample_play(title="Play without genres")

        res = self.client.get(PLAY_URL, {"genres": f"{genre1.id},{genre2.id}"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_plays_by_actors(self):
        actor1 = Actor.objects.create(first_name="Actor 1", last_name="Last 1")
        actor2 = Actor.objects.create(first_name="Actor 2", last_name="Last 2")

        play1 = sample_play(title="Movie 1")
        play2 = sample_play(title="Movie 2")

        play1.actors.add(actor1)
        play2.actors.add(actor2)

        play3 = sample_play(title="Play without actors")

        res = self.client.get(PLAY_URL, {"actors": f"{actor1.id},{actor2.id}"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_plays_by_title(self):
        play1 = sample_play(title="Play")
        play2 = sample_play(title="Another Play")
        play3 = sample_play(title="No match")

        res = self.client.get(PLAY_URL, {"title": "play"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_create_play_forbidden(self):
        payload = {
            "title": "Play",
            "description": "Description",
        }
        res = self.client.post(PLAY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_play(self):
        payload = {
            "title": "Play",
            "description": "Description",
        }
        res = self.client.post(PLAY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        play = Play.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(play, key))

    def test_create_play_with_genres(self):
        genre1 = Genre.objects.create(name="Action")
        genre2 = Genre.objects.create(name="Adventure")
        payload = {
            "title": "Kill the death",
            "genres": [genre1.id, genre2.id],
            "description": "He tried to kill the death, but death killed him faster",
        }
        res = self.client.post(PLAY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        play = Play.objects.get(id=res.data["id"])
        genres = play.genres.all()
        self.assertEqual(genres.count(), 2)
        self.assertIn(genre1, genres)
        self.assertIn(genre2, genres)

    def test_create_play_with_actors(self):
        actor1 = Actor.objects.create(first_name="Tom", last_name="Holland")
        actor2 = Actor.objects.create(first_name="Tobey", last_name="Maguire")
        payload = {
            "title": "Kill the death",
            "actors": [actor1.id, actor2.id],
            "description": "He tried to kill the death, but death killed him faster",
            "duration": 148,
        }
        res = self.client.post(PLAY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        play = Play.objects.get(id=res.data["id"])
        actors = play.actors.all()
        self.assertEqual(actors.count(), 2)
        self.assertIn(actor1, actors)
        self.assertIn(actor2, actors)

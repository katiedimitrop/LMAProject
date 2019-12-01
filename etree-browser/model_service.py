# part of logic tier: this will transform user queries into SPARQL queries and
# aggregate the results
from models import ArtistModel, VenueModel, PerformanceModel, TrackModel
import urllib.parse

import json
import re

class ArtistService:
    def __init__(self):
        self.model = ArtistModel()

    def get_all(self):
        return self.model.get_all()

    def get_count(self):
        return self.model.get_all_count()

    def get_performances(self, artist_name):
        # escape single-quote
        artist_name = artist_name.replace("'", r"\'")
        return self.model.get_all_performances(artist_name)

    def get_mb_tags(self, artist_name):
        # escape single-quote
        artist_name = artist_name.replace("'", r"\'")
        return self.model.get_mb_tags(artist_name)


class VenueService:
    def __init__(self):
        self.model = VenueModel()

    def get_all(self):
        return self.model.get_all()

    def get_count(self):
        return self.model.get_all_count()

    def get_count(self):
        return self.model.get_all_count()

    def get_location(self,venue_name):
        venue_name = venue_name.replace("'", r"\'")
        return self.model.get_location(venue_name)

class PerformanceService:
    def __init__(self):
        self.model = PerformanceModel()

    def get_all(self):
        return self.model.get_all()

    def get_count(self):
        return self.model.get_all_count()

    def get_tracks(self, perf_name):
        perf_name = perf_name.replace("'", r"\'")
        return self.model.get_all_tracks(perf_name)

    def get_venue(self, perf_name):
        perf_name = perf_name.replace("'", r"\'")
        return self.model.get_venue(perf_name)

    def get_artist(self, perf_name):
        perf_name = perf_name.replace("'", r"\'")
        return self.model.get_artist(perf_name)

    def get_date(self, perf_name):
        perf_name = perf_name.replace("'", r"\'")
        return self.model.get_date(perf_name)

    def get_description(self, perf_name):
        perf_name = perf_name.replace("'", r"\'")
        return self.model.get_description(perf_name)

class TrackService:
    def __init__(self):
        self.model = TrackModel()

    def get_all(self):
        return self.model.get_all()

    def get_count(self):
        return self.model.get_all_count()

    def get_artist(self, track_name):
        # escape single-quote
        track_name = track_name.replace("'", r"\'")
        track_name = track_name.replace("#", r"\#")
        return self.model.get_artist(track_name)

    def get_performance(self, track_name):
        # escape single-quote
        track_name = track_name.replace("'", r"\'")
        track_name = track_name.replace("#", r"\#")
        return self.model.get_performance(track_name)
# part of logic tier: this will transform user queries into SPARQL queries and
# aggregate the results
from models import ArtistModel, VenueModel, PerformanceModel, TrackModel


class ArtistService:
    def __init__(self):
        self.model = ArtistModel()

    def get_all(self):
        return self.model.get_all()

    def get_count(self):
        return self.model.get_all_count()

    def get_performances(self, artist_name):
        return self.model.get_all_performances(artist_name)


class VenueService:
    def __init__(self):
        self.model = VenueModel()

    def get_all(self):
        return self.model.get_all()

    def get_count(self):
        return self.model.get_all_count()


class PerformanceService:
    def __init__(self):
        self.model = PerformanceModel()

    def get_all(self):
        return self.model.get_all()

    def get_count(self):
        return self.model.get_all_count()

    def get_tracks(self, perf_name):
        return self.model.get_all_tracks(perf_name)

class TrackService:
    def __init__(self):
        self.model = TrackModel()

    def get_all(self):
        return self.model.get_all()

    def get_count(self):
        return self.model.get_all_count()

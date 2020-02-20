# part of logic tier: this will transform user queries into SPARQL queries and
# aggregate the results
import pandas as pd
from models import TrackModel

from sklearn_extra.cluster import KMedoids
class ClusterService:
    def __init__(self):
        self.model = TrackModel()

    def get_analysis_for_track(self, artist_name, track_name):
        track_analysis = self.model.get_analysis_for_track(artist_name,track_name)
        return track_analysis
from test_base import BaseTestCase
import unittest
import SPARQLWrapper
from models import ArtistModel, VenueModel, PerformanceModel, TrackModel

class ModelTests(BaseTestCase):
    #fixture
    def test_get_all_artists(self):
        self.model = ArtistModel()
        self.assertEqual(len(self.model.get_all()), int(self.model.get_all_count()))

    def test_get_all_performances(self):
        self.model = PerformanceModel()
        #print("Performances: \n Received " + str(sum([len(arr) for arr in self.model.get_all()])) + "\n Counted "
              #+ self.model.get_all_count())
        self.assertEqual(sum([len(arr) for arr in self.model.get_all()]), int(self.model.get_all_count()))

    def test_get_all_tracks(self):
        self.model = TrackModel()
        #print("Tracks: \n Received "+str(sum([len(arr) for arr in self.model.get_all()]))+ "\n Counted " +self.model.get_all_count())
        self.assertEqual(sum([len(arr) for arr in self.model.get_all()]), int(self.model.get_all_count()))

    def test_get_all_venues(self):
        self.model = VenueModel()
        #print("Venues: \n Received "+str(sum([len(arr) for arr in self.model.get_all()]))+ "\n Counted " +self.model.get_all_count())
        self.assertEqual(sum([len(arr) for arr in self.model.get_all()]), int(self.model.get_all_count()))

if __name__ == '__main__':
    unittest.main()
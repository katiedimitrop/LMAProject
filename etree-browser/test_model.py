from test_base import BaseTestCase
import unittest
import SPARQLWrapper
from models import ArtistModel, VenueModel, PerformanceModel, TrackModel

class ModelTests(BaseTestCase):
    #fixture
    #def test_get_all_artists(self):
        #self.model = ArtistModel()
        #self.assertEqual(len(self.model.get_all()), int(self.model.get_all_count()))

    #def test_get_all_performances(self):
        #self.model = PerformanceModel()
        #print("Performances: \n Received " + str(sum([len(arr) for arr in self.model.get_all()])) + "\n Counted "
              #+ self.model.get_all_count())
        #self.assertEqual(sum([len(arr) for arr in self.model.get_all()]), int(self.model.get_all_count()))

    #def test_get_all_tracks(self):
        #self.model = TrackModel()
        #print("Tracks: \n Received "+str(sum([len(arr) for arr in self.model.get_all()]))+ "\n Counted " +self.model.get_all_count())
        #self.assertEqual(sum([len(arr) for arr in self.model.get_all()]), int(self.model.get_all_count()))

    #def test_get_all_calma_tracks(self):
        #self.model = TrackModel()
        #print("Tracks: \n Received "+str(sum([len(arr) for arr in self.model.get_all()]))+ "\n Counted " +self.model.get_all_count())
        #self.assertEqual(sum([len(arr) for arr in self.model.get_all_calma_tracks()]), int(self.model.get_all_calma_count()))

    #def test_get_all_venues(self):
        #self.model = VenueModel()
        #print("Venues: \n Received "+str(sum([len(arr) for arr in self.model.get_all()]))+ "\n Counted " +self.model.get_all_count())
        #self.assertEqual(sum([len(arr) for arr in self.model.get_all()]), int(self.model.get_all_count()))

    def test_get_track_analyses(self):
        self.model = TrackModel()
        #tests if number of dictionary entries corresponds to expected value
        self.assertEqual(len(self.model.get_analyses("Guster","The Captain")), 99)
    #def test_get_tempo(self):
        #self.model = TrackModel()
        #self.assertEqual(self.model.get_actual_tempo(), False)

if __name__ == '__main__':
    unittest.main()
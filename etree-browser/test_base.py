from templates import app
import unittest


class BaseTestCase(unittest.TestCase):
    """A base test case for flask-tracking."""

    #def create_app(self):
        #setup test configurations
       # app.configurations.from_object('config.TestConfig')
       # return app
    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False

        self.app = app.test_client()


        # Disable sending emails during unit testing

        self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
        pass

    ##########################
    #### Functional tests ####
    ##########################

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_non_existent_page_name(self):
        response = self.app.get('/whatever', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_analyses(self):
        response = self.app.get('/analyses', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_analysis(self):
        response = self.app.get('/analyses/?artist=Smashing%20Pumpkins&track=Zero', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_non_existent_analysis_artist(self):
        response = self.app.get('/analyses/?artist=NONEXISTENT&track=Zero', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_non_existent_analysis_track(self):
        response = self.app.get('/analyses/?artist=Smashing%20Pumpkins&track=NONEXISTENT', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_artists(self):
        response = self.app.get('/artists', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_performances(self):
        response = self.app.get('/performances', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_venues(self):
        response = self.app.get('/venues', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_tracks(self):
        response = self.app.get('/tracks', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_artist(self):
        response = self.app.get('/artist/?name=Smashing%20Pumpkins', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_non_existent_artist(self):
        response = self.app.get('/artist/?name=NONEXISTENT', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_track(self):
        response = self.app.get('/tracks/?title=There%20It%20Goes', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_non_existent_track(self):
        response = self.app.get('/tracks/?title=NONEXISTENT', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_perf(self):
        response = self.app.get('/performances/?title=Tenacious%20D', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_non_existent_perf(self):
        response = self.app.get('/performance/?title=NONEXISTENT', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_perf_page(self):
        response = self.app.get('/performance/?title=Smashing%20Pumpkins%20Live%20at%20Cabaret%20Metro%20on%201988-10-05', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_non_existent_perf_page(self):
        response = self.app.get('/performance/?title=NONEXISTENT', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_venue(self):
        response = self.app.get('/venues/?title=Manchester%20Academy', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_non_existent_venue(self):
        response = self.app.get('/venues/?title=NONEXISTENT', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_venue_page(self):
        response = self.app.get('/venue/?name=Manchester%20Academy%203', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_non_existent_venue_page(self):
        response = self.app.get('/venue/?name=NONEXISTENT', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()


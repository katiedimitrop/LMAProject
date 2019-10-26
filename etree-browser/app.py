from flask import Flask, render_template
from logic import ArtistService, VenueService, PerformanceService, TrackService

# create an app instance
app = Flask(__name__)


# pick endpoint
@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/artists')
def get_all_artists():
    results = ArtistService().get_all()
    count = ArtistService().get_count()
    return render_template('artists.html', results=results, count=count)


@app.route('/venues')
def get_all_venues():
    results = VenueService().get_all()
    count = VenueService().get_count()
    return render_template('venues.html', results=results, count=count)


@app.route('/performances')
def get_all_performances():
    results = PerformanceService().get_all()
    count = PerformanceService().get_count()
    return render_template('performances.html', results=results, count=count)


@app.route('/tracks')
def get_all_tracks():
    results = TrackService().get_all()
    count = TrackService().get_count()
    return render_template('tracks.html', results=results, count=count)


# on running python, run the flask app
if __name__ == '__main__':
    app.run(debug=True)

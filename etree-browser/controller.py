from flask import Flask, render_template
from model_service import ArtistService, VenueService, PerformanceService, TrackService

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


@app.route('/artists/<artist_name>')
def get_all_artists_performances(artist_name):
    performance_titles = ArtistService().get_performances(artist_name)
    mb_tags = ArtistService().get_mb_tags(artist_name)
    return render_template('artist.html', performance_titles=performance_titles, artist_name=artist_name, mb_tags=mb_tags)


@app.route('/performances')
def get_all_performances():
    results = PerformanceService().get_all()
    count = PerformanceService().get_count()
    return render_template('performances.html', results=results, count=count)


@app.route('/performances/<perf_name>')
def get_performance(perf_name):
    track_titles = PerformanceService().get_tracks(perf_name)
    venue_name = PerformanceService().get_venue(perf_name)
    artist_name = PerformanceService().get_artist(perf_name)
    perf_date = PerformanceService().get_date(perf_name)
    perf_description = PerformanceService().get_description(perf_name)
    return render_template('performance.html', track_titles=track_titles, perf_name=perf_name, venue_name=venue_name,
                           artist_name=artist_name, perf_date = perf_date, perf_description = perf_description)


@app.route('/tracks')
def get_all_tracks():
    results = TrackService().get_all()
    count = TrackService().get_count()
    return render_template('tracks.html', results=results, count=count)


@app.route('/tracks/<track_name>')
def get_track(track_name):

    #artist_name = TrackService().get_artist(track_name)
    #returns performance names, Artists, audio link
    results = TrackService().get_performance(track_name)
    print(results)
    return render_template('track.html',track_name=track_name, results= results)


@app.route('/venues')
def get_all_venues():
    results = VenueService().get_all()
    count = VenueService().get_count()
    return render_template('venues.html', results=results, count=count)


@app.route('/venues/<venue_name>')
def get_venue(venue_name):
    location = VenueService().get_location(venue_name)
    print(location)
    return render_template('venue.html', venue_name=venue_name, location = location )


# on running python, run the flask app
if __name__ == '__main__':
    app.run(debug=True)

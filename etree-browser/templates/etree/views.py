# This is where the routes are defined, could be split into several modules
from templates import app
from flask import Flask, render_template, Blueprint
from model_service import ArtistService, VenueService, PerformanceService, TrackService

#each view should have its own blueprint
etree_blueprint = Blueprint('etree',__name__)

# pick endpoint
@etree_blueprint.route('/')
@etree_blueprint.route('/hello')
def index():
    return render_template('index.html')

@etree_blueprint.route('/home')
def actual_home():
    try:
        results = ArtistService().get_all()
        count = ArtistService().get_count()
        return render_template('home.html', results=results, count=count)
    except Exception as e:
        return str(e)

@etree_blueprint.route('/artists')
def get_all_artists():
    results = ArtistService().get_all()
    count = ArtistService().get_count()
    return render_template("artists.html", results=results, count=count)


@etree_blueprint.route('/artists/<artist_name>')
def get_all_artists_performances(artist_name):
    performance_titles = ArtistService().get_performances(artist_name)
    mb_tags = ArtistService().get_mb_tags(artist_name)
    return render_template('artist.html', performance_titles=performance_titles, artist_name=artist_name,
                           mb_tags=mb_tags)


@etree_blueprint.route('/performances')
def get_all_performances():
    results = PerformanceService().get_all()
    count = PerformanceService().get_count()
    return render_template('performances.html', results=results, count=count)


@etree_blueprint.route('/performances/<perf_name>')
def get_performance(perf_name):
    track_titles = PerformanceService().get_tracks(perf_name)
    venue_name = PerformanceService().get_venue(perf_name)
    artist_name = PerformanceService().get_artist(perf_name)
    perf_date = PerformanceService().get_date(perf_name)
    perf_description = PerformanceService().get_description(perf_name)
    return render_template('performance.html', track_titles=track_titles, perf_name=perf_name,
                           venue_name=venue_name,
                           artist_name=artist_name, perf_date=perf_date, perf_description=perf_description)


@etree_blueprint.route('/tracks')
def get_all_tracks():
    results = TrackService().get_all()
    count = TrackService().get_count()
    return render_template('tracks.html', results=results, count=count)


@etree_blueprint.route('/tracks/<track_name>')
def get_track(track_name):
    # artist_name = TrackService().get_artist(track_name)
    # returns performance names, Artists, audio link
    results = TrackService().get_performance(track_name)
    print(results)
    return render_template('track.html', track_name=track_name, results=results)


@etree_blueprint.route('/venues')
def get_all_venues():
    results = VenueService().get_all()
    count = VenueService().get_count()
    return render_template('venues.html', results=results, count=count)


@etree_blueprint.route('/venues/<venue_name>')
def get_venue(venue_name):
    location = VenueService().get_location(venue_name)
    print(location)
    return render_template('venue.html', venue_name=venue_name, location=location)

# This is where the routes are defined, could be split into several modules
from templates import app
from flask import Flask, render_template, Blueprint
from model_service import ArtistService, VenueService, PerformanceService, TrackService
import urllib.parse

# each view should have its own blueprint
etree_blueprint = Blueprint('etree', __name__)


# pick endpoint

@etree_blueprint.route('/')
def art_home():
    results = ArtistService().get_all()
    count = ArtistService().get_count()

    # need encoded versions of titles wherever there are links
    encoded_r = []
    for result in results["results"]["bindings"]:
        encoded_r.append(urllib.parse.quote(result["name"]["value"].strip('\n')))
    return render_template("home.html", results=results, count=count, encoded_r=encoded_r)


@etree_blueprint.route('/artists/<artist_name>')
def get_all_artists_performances(artist_name):

    # requests to Artists service and template rendering require unencoded version
    artist_name = urllib.parse.unquote(artist_name)

    performance_titles = ArtistService().get_performances(artist_name)
    mb_tags = ArtistService().get_mb_tags(artist_name)

    # need encoded versions of titles wherever there are links
    encoded_perfs = []
    for performance_title in performance_titles["results"]["bindings"]:
        encoded_perfs.append(urllib.parse.quote(performance_title["perftitle"]["value"]))
    return render_template('artist.html', performance_titles=performance_titles,encoded_perfs = encoded_perfs,
                           artist_name=artist_name, mb_tags=mb_tags)

@etree_blueprint.route('/performances')
def perf_home():
    results = PerformanceService().get_all()
    count = PerformanceService().get_count()

    # need encoded versions of titles wherever there are links
    encoded_r = []
    for result in results["results"]["bindings"]:
        encoded_r.append(urllib.parse.quote(result["name"]["value"].strip('\n')))
    return render_template("performances.html", results=results, count=count, encoded_r=encoded_r)

@etree_blueprint.route('/performances/<perf_name>')
def get_performance(perf_name):
    # requests to Perf service and template rendering require unencoded version
    perf_name = urllib.parse.unquote(perf_name)

    track_titles = PerformanceService().get_tracks(perf_name)
    venue_name = PerformanceService().get_venue(perf_name)
    artist_name = PerformanceService().get_artist(perf_name)
    perf_date = PerformanceService().get_date(perf_name)
    perf_description = PerformanceService().get_description(perf_name)

    # need encoded versions of titles wherever there are links
    encoded_a = urllib.parse.unquote(artist_name)

    encoded_ts = []
    for track_title in track_titles["results"]["bindings"]:
        encoded_ts.append(urllib.parse.quote(track_title["tracktitle"]["value"]))

    encoded_v = urllib.parse.unquote(venue_name)


    return render_template('performance.html', track_titles=track_titles, encoded_ts = encoded_ts, perf_name=perf_name,
                        venue_name=venue_name, encoded_v = encoded_v, artist_name=artist_name, encoded_a = encoded_a,
                        perf_date=perf_date, perf_description=perf_description )

@etree_blueprint.route('/tracks')
def track_home():
    results = TrackService().get_all()
    count = TrackService().get_count()

    # need encoded versions of titles wherever there are links
    encoded_r = []
    for result in results["results"]["bindings"]:
        encoded_r.append(urllib.parse.quote(result["trackname"]["value"].strip('\n')))
    return render_template("tracks.html", results=results, count=count, encoded_r=encoded_r)

@etree_blueprint.route('/tracks/<track_name>')
def get_track(track_name):
    # artist_name = TrackService().get_artist(track_name)
    # returns performance names, Artists, audio link

    # requests to Track service and template rendering require unencoded version
    track_name = urllib.parse.unquote(track_name)
    results = TrackService().get_performance(track_name)


    # need encoded versions of titles wherever there are links

    encoded_perfs = []
    encoded_ars = []

    for perf in results["results"]["bindings"]:
        encoded_perfs.append(urllib.parse.quote(perf["perfname"]["value"].strip('\n')))
        encoded_ars.append(urllib.parse.quote(perf["artname"]["value"].strip('\n')))

    return render_template('track.html', track_name=track_name, results=results, encoded_perfs = encoded_perfs,
                           encoded_ars = encoded_ars)

@etree_blueprint.route('/venues')
def venue_home():
    results = VenueService().get_all()
    count = VenueService().get_count()

    # need encoded versions of titles wherever there are links
    encoded_r = []
    for result in results["results"]["bindings"]:
        encoded_r.append(urllib.parse.quote(result["name"]["value"].strip('\n')))
    return render_template("venues.html", results=results, count=count, encoded_r=encoded_r)



@etree_blueprint.route('/venues/<venue_name>')
def get_venue(venue_name):
    #requests to Venue service and template rendering require unencoded version
    venue_name = urllib.parse.unquote(venue_name)
    print(venue_name)
    location = VenueService().get_location(venue_name)

    return render_template('venue.html', venue_name=venue_name, location=location)

@etree_blueprint.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@etree_blueprint.errorhandler(505)
def internal_error(e):
    return render_template('500.html'), 500
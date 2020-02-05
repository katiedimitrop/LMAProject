# This is where the routes are defined, could be split into several modules
from templates import app
from flask import Flask, render_template, Blueprint
from model_service import ArtistService, VenueService, PerformanceService, TrackService
import urllib.parse

import statistics

# each view should have its own blueprint
etree_blueprint = Blueprint('etree', __name__)


# pick endpoint

@etree_blueprint.route('/artists')
def art_home():
    artist_names = ArtistService().get_all()
    count = ArtistService().get_count()

    # need encoded versions of titles wherever there are links
    encoded_r = []
    for artist_name in artist_names:
        encoded_r.append(urllib.parse.quote(artist_name.strip('\n')))
    return render_template("artists.html", artist_names=artist_names, count=count, encoded_r=encoded_r)


@etree_blueprint.route('/analysis')
def analysis_home():
    tracks = TrackService().get_analyses("Guster", "The Captain")
    # print(tracks)
    track_tempos = []
    pt_dict = {}
    for track, track_info in tracks.items():
        track_tempos.append(int(track_info[4]))

    for track, track_info in tracks.items():
        pt_dict["y"] = track_info[4]


    print(pt_dict)
    count = len(track_tempos)
    avg_tempo = statistics.mean(track_tempos)
    max_tempo = max(track_tempos)

    actual_tempo_and_key = TrackService().get_actual_tempo_and_key()
    return render_template("analysis.html", tracks=tracks, count=count, track_tempos=track_tempos, avg_tempo=avg_tempo,
                           max_tempo=max_tempo, actual_tempo_and_key = actual_tempo_and_key)


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
    return render_template('artist.html', performance_titles=performance_titles, encoded_perfs=encoded_perfs,
                           artist_name=artist_name, mb_tags=mb_tags)


@etree_blueprint.route('/performances')
def perf_home():
    performance_names = PerformanceService().get_all()[0][0:30]
    count = PerformanceService().get_count()

    # need encoded versions of titles wherever there are links
    encoded_r = []
    for performance_name in performance_names:
        print(performance_name)
        encoded_r.append(urllib.parse.quote(performance_name.strip('\n')))
    return render_template("performances.html", performance_names=performance_names, count=count, encoded_r=encoded_r)


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

    return render_template('performance.html', track_titles=track_titles, encoded_ts=encoded_ts, perf_name=perf_name,
                           venue_name=venue_name, encoded_v=encoded_v, artist_name=artist_name, encoded_a=encoded_a,
                           perf_date=perf_date, perf_description=perf_description)


@etree_blueprint.route('/tracks')
def track_home():
    track_names = TrackService().get_all()[0][0:30]
    count = TrackService().get_count()

    # need encoded versions of titles wherever there are links
    encoded_r = []
    for track_name in track_names:
        encoded_r.append(urllib.parse.quote(track_name.strip('\n')))
    return render_template("tracks.html", track_names=track_names, count=count, encoded_r=encoded_r)


@etree_blueprint.route('/tracks/<track_name>')
def get_track(track_name):
    # returns performance names, Artists, audio link

    # requests to Track service and template rendering require unencoded version
    track_name = urllib.parse.unquote(track_name)
    performances = TrackService().get_performances(track_name)

    # need encoded versions of titles wherever there are links

    encoded_perfs = []
    encoded_ars = []

    for perf in performances["results"]["bindings"]:
        encoded_perfs.append(urllib.parse.quote(perf["perfname"]["value"].strip('\n')))
        encoded_ars.append(urllib.parse.quote(perf["artname"]["value"].strip('\n')))

    return render_template('track.html', track_name=track_name, performances=performances, encoded_perfs=encoded_perfs,
                           encoded_ars=encoded_ars)


@etree_blueprint.route('/venues')
def venue_home():
    venue_names = VenueService().get_all()[0][0:30]
    count = VenueService().get_count()

    # need encoded versions of titles wherever there are links
    encoded_r = []
    for venue_name in venue_names:
        encoded_r.append(urllib.parse.quote(venue_name.strip('\n')))
    return render_template("venues.html", venue_names=venue_names, count=count, encoded_r=encoded_r)


@etree_blueprint.route('/venues/<venue_name>')
def get_venue(venue_name):
    # requests to Venue service and template rendering require unencoded version
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

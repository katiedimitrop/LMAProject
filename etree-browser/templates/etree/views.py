# This is where the routes are defined, could be split into several modules
from templates import app
from flask import Flask, render_template, Blueprint, request
from model_service import ArtistService, VenueService, PerformanceService, TrackService
from cluster_service import ClusterService
import urllib.parse
import numpy as np
import pandas as pd
import re
import statistics
from statistics import mean
import operator
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import os
import sys
from pprint import pprint
from collections import Counter
# each view should have its own blueprint
etree_blueprint = Blueprint('etree', __name__)


@etree_blueprint.route('/analysis')
def guster_analysis():
    tracks,track_tempos,avg_tempo,max_tempo,predicted_keys,key_percentages,key_lengths,labels = TrackService().get_analyses("Guster", "The Captain")
    actual_tempo_and_key = TrackService().get_actual_tempo_and_key()
    # print(tracks)
    avg_tempo = round(avg_tempo, 2)
    #predicted_key = max(predicted_keys.iteritems(), key=operator.itemgetter(1))[0]
    speed_diff = (1- float(actual_tempo_and_key['tempo'])/ avg_tempo ) * 100
    tempos_rounded = np.around(track_tempos)
    return render_template("guster_analysis.html", tracks=tracks, count=len(track_tempos), tempos=track_tempos, avg_tempo = avg_tempo,
                           max_tempo=max_tempo, actual_tempo_and_key = actual_tempo_and_key, predicted_keys=predicted_keys,
                           key_percentages = key_percentages,  key_lengths = np.around( key_lengths,2), average_length = np.around(mean( key_lengths),2 ),
                           speed_diff = round(speed_diff),tempos_rounded = tempos_rounded )

@etree_blueprint.route('/analyses')
def analyses():
    analyses = []
    encoded_analyses = []
    from os.path import dirname, abspath
    d = dirname(abspath("views.py"))
    artists = os.listdir(d+"/calma_data")

    for artist in artists:
        tracks = os.listdir(d + "/calma_data/"+artist)
        for track_id in range(0,len(tracks)):
            tracks[track_id] = re.sub('.csv', '', tracks[track_id])
            analyses.append([artist,tracks[track_id]])

            encoded_analyses.append( [ urllib.parse.quote(str(artist)),urllib.parse.quote(str(tracks[track_id])) ] )
    #analyses = [["Smashing Pumpkins","Zero"],[]]
    #first column will be artists names and second will be track names
    return render_template("analyses.html", encoded_analyses=encoded_analyses,analyses=analyses)

@etree_blueprint.route('/analysis/1')
def analysis_one():
    tracks,track_tempos,avg_tempo,max_tempo,predicted_keys,key_percentages,key_lengths,labels = TrackService().get_analyses("Guster", "The Captain")
    actual_tempo_and_key = TrackService().get_actual_tempo_and_key()
    # print(tracks)
    avg_tempo = round(avg_tempo, 2)
    track_tempos = [round(tempo) for tempo in track_tempos]
    #predicted_key = max(predicted_keys.iteritems(), key=operator.itemgetter(1))[0]
    speed_diff = (1- float(actual_tempo_and_key['tempo'])/ avg_tempo ) * 100
    #sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials("e5e493afe89e4be1b4f8cd93e4e44e37","03716b8ca8e140dc9e5a13e707bb868b"))
    #TO DO: could get spotify audio analysis data here
    return render_template("analysis1.html", tracks=tracks, count=len(track_tempos), tempos=track_tempos, avg_tempo = avg_tempo,
                           max_tempo=max_tempo, actual_tempo_and_key = actual_tempo_and_key, predicted_keys=predicted_keys,
                           key_percentages = key_percentages,  key_lengths = np.around( key_lengths,2), average_length = np.around(mean( key_lengths),2 ),
                           speed_diff = round(speed_diff),labels = labels )

@etree_blueprint.route('/analyses/', methods=['GET'])
def analysis():

    #these can be used to display actual key instead of key numbers
    key_names = ["C", "Db / C#", "D", "Eb / D#", "E", "F", "Gb / F#", "G", "Ab / G#", "A", "Bb", "B/Cb",
                 "Cm", "Dbm / C#m", "Dm", "Ebm / D#m", "Em", "Fm", "Gbm / F#m", "Gm", "Abm / G#m", "Am", "Bbm",
                 "Bm/Cbm", "unknown"]
    artist = request.args.get('artist')
    track = request.args.get('track')
    artist_name = urllib.parse.unquote(artist)
    track_name = urllib.parse.unquote(track)

    track_analysis = ClusterService().get_kmedoids_for_track(artist_name,track_name)
   #The key for this one on getsongbpm is Wrong
    #studio_metadata = TrackService().get_actual_tempo_and_key()
    #print("KEY " + str(studio_metadata["key"]))
    #print("TEMPO " + str(studio_metadata["tempo"]))

    #this is needed for tempo ploting range
    max_tempo = track_analysis['Tempo'].values.max()
    max_key = track_analysis['Max Key'].values.max()
    max_duration = track_analysis['Track duration'].values.max()
    max_label = track_analysis['Labels'].values.max()
    #the conversion from pandas df to lists is necessary for pandas charts to work
    return render_template("analysis.html",track_analysis = track_analysis,key_names = key_names,
                           count = len(track_analysis),tempos = track_analysis['Tempo'].values.astype(int).tolist()
                           ,max_tempo=int(max_tempo),max_key = max_key
                           ,max_keys = track_analysis['Max Key'].values.astype(int).tolist(),
                           max_duration = max_duration, durs = track_analysis['Track duration'].values.astype(int).tolist()
                           ,labels = track_analysis['Labels'].values.astype(int).tolist(), max_label = max_label
                           )

@etree_blueprint.route('/')
@etree_blueprint.route('/artists')
def art_home():
    artist_names = ArtistService().get_all()
    count = ArtistService().get_count()

    # need encoded versions of titles wherever there are links
    encoded_r = []
    for artist_name in artist_names:
        encoded_r.append(urllib.parse.quote(artist_name.strip('\n')))
    return render_template("artists.html", artist_names=artist_names, count=count, encoded_r=encoded_r)

@etree_blueprint.route('/artist/', methods=['GET'])
def get_all_artists_performances():
    artist_name = request.args.get('name')
    # requests to Artists service and template rendering require unencoded version
    artist_name = urllib.parse.unquote(artist_name)
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials("e5e493afe89e4be1b4f8cd93e4e44e37","03716b8ca8e140dc9e5a13e707bb868b"))
    print(artist_name)
    results = sp.search(q='artist:' + artist_name, type='artist')
    items = results['artists']['items']
    artist_image = None
    if len(items) > 0 :
        artist = items[0]
        if artist_name in artist['name']:
            print(artist['name'], artist['images'][0]['url'])
            #print(artist_name)
            artist_image = artist['images'][0]['url']



    performance_titles = ArtistService().get_performances(artist_name)
    #Just checking if perfs are null in which case don't show page
    perfdicts=  performance_titles["results"]["bindings"]
    perftitles = []
    for perftitle in perfdicts:
        perftitles.append(perftitle["perftitle"]["value"])
    print("HERE:"+str(perftitles))
    if len(perftitles) == 0:
        return render_template('404.html'), 404
    mb_tags = ArtistService().get_mb_tags(artist_name)

    # need encoded versions of titles wherever there are links
    encoded_perfs = []
    for performance_title in performance_titles["results"]["bindings"]:
        encoded_perfs.append(urllib.parse.quote(performance_title["perftitle"]["value"]))
    return render_template('artist.html', performance_titles=performance_titles, encoded_perfs=encoded_perfs,
                           artist_name=artist_name, mb_tags=mb_tags, artist_image = artist_image)


@etree_blueprint.route('/performances')
def perf_home():
   # performance_names = PerformanceService().get_all()[0][0:30000]
    count = PerformanceService().get_count()
    return render_template("performances.html", count=count)

# this returns performances that contain perf_name
@etree_blueprint.route('/performances/', methods=['GET'])
def get_performances():
    perf_name = request.args.get('title')
    perf_name = urllib.parse.unquote(perf_name)
    performances = PerformanceService().get_performance(perf_name)

    # need encoded versions of titles wherever there a

    encoded_perfs = []
    encoded_ars = []
    for perf in performances:
        encoded_perfs.append(urllib.parse.quote(perf.strip('\n')))

    return render_template('all-performances.html', perf_name = perf_name ,performances=performances,
                           encoded_perfs=encoded_perfs)

#this returns only one particular performance page
@etree_blueprint.route('/performance/', methods=['GET'])
def get_performance():
    perf_name= request.args.get('title')
    # requests to Perf service and template rendering require unencoded version
    perf_name = urllib.parse.unquote(perf_name)

    track_titles,audio = PerformanceService().get_tracks(perf_name)
    venue_name = PerformanceService().get_venue(perf_name)
    artist_name = PerformanceService().get_artist(perf_name)
    perf_date = PerformanceService().get_date(perf_name)
    perf_description = PerformanceService().get_description(perf_name)

    # need encoded versions of titles wherever there are links
    encoded_a = urllib.parse.unquote(artist_name)

    encoded_ts = []
    for track_title in track_titles:
        encoded_ts.append(urllib.parse.quote(track_title))

    encoded_v = urllib.parse.quote(venue_name)


    return render_template('performance.html', track_titles=track_titles, encoded_ts=encoded_ts, audio = audio, perf_name=perf_name,
                           venue_name=venue_name, encoded_v=encoded_v, artist_name=artist_name, encoded_a=encoded_a,
                           perf_date=perf_date, perf_description=perf_description)



@etree_blueprint.route('/tracks')
def track_home():
    #track_names = TrackService().get_all()[0][0:30]
    count = TrackService().get_count()

    # need encoded versions of titles wherever there are links
    encoded_r = []
    #for track_name in track_names:
        #encoded_r.append(urllib.parse.quote(track_name.strip('\n')))
    return render_template("tracks.html", count=count) #track_names=track_names, encoded_r=encoded_r)


@etree_blueprint.route('/tracks/', methods=['GET'])
def get_track():
    # returns performance names, Artists, audio link
    track_name = request.args.get('title')
    # requests to Track service and template rendering require unencoded version
    track_name = urllib.parse.unquote(track_name)
    performances = TrackService().get_performances(track_name)

    # need encoded versions of titles wherever there are links

    encoded_perfs = []
    encoded_ars = []

    for perf in performances["results"]["bindings"]:
        encoded_perfs.append(urllib.parse.quote(perf["perfname"]["value"].strip('\n')))
        encoded_ars.append(urllib.parse.quote(perf["artname"]["value"].strip('\n')))

    return render_template('all-tracks.html', track_name=track_name, performances=performances, encoded_perfs=encoded_perfs,
                           encoded_ars=encoded_ars)


@etree_blueprint.route('/venues')
def venue_home():
    #venue_names = VenueService().get_all()[0][0:30]
    count = VenueService().get_count()
    return render_template("venues.html", count=count)

# this returns performances that contain perf_name
@etree_blueprint.route('/venues/', methods=['GET'])
def get_venues():
    venue_name = request.args.get('title')
    venue_name = urllib.parse.unquote(venue_name)
    venues = VenueService().get_venue(venue_name)

    # need encoded versions of titles wherever there a

    encoded_vens = []

    for venue in venues:
        encoded_vens.append(urllib.parse.quote(venue.strip('\n')))

    return render_template('all-venues.html', venue_name = venue_name ,venues=venues,
                           encoded_vens=encoded_vens)

@etree_blueprint.route('/venue/', methods=['GET'])
def get_venue():
    # requests to Venue service and template rendering require unencoded version
    venue_name = request.args.get('name')
    venue_name = urllib.parse.unquote(venue_name)
    perf_names = VenueService().get_performances(venue_name)
    print(venue_name)
    location = VenueService().get_location(venue_name)
    encoded_perfs = []
    for perf in perf_names:
        encoded_perfs.append(urllib.parse.quote(perf.strip('\n')))
    print(perf_names)
    return render_template('venue.html', venue_name=venue_name, location=location,perf_names=perf_names,
                            encoded_perfs = encoded_perfs)


@etree_blueprint.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@etree_blueprint.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# where the querying happens, could be split into several modules
import subprocess
import time
import pandas as pd

from SPARQLWrapper import SPARQLWrapper, JSON

import urllib.request
import shutil
import numpy as np
import rdflib
import csv
import requests

import re

import numpy as np

# each one of the rest of the classes corresponds to one resource
class ArtistModel:
    prefixes = """
                PREFIX etree:<http://etree.linkedmusic.org/vocab/>
                PREFIX mo:<http://purl.org/ontology/mo/>
                PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>"""

    def __init__(self):
        self.sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")

    def get_all(self):
        # Define the query
        self.sparql.setQuery(ArtistModel.prefixes + """
                SELECT ?name
                WHERE 
                {
                ?subject rdf:type mo:MusicArtist.
                ?subject skos:prefLabel ?name
                } order by asc(UCASE(str(?name)))
            """)
        self.sparql.setReturnFormat(JSON)
        artist_names = self.sparql.query().convert()["results"]["bindings"]
        #isolate values from list of dictionaries
        artist_names = [artist_dict["name"]["value"] for artist_dict in artist_names ]

        return artist_names

    def get_all_count(self):
        self.sparql.setQuery(ArtistModel.prefixes + """
                SELECT(COUNT(?label) as ?noOfArtists)
                WHERE
                { ?subject rdf:type mo:MusicArtist . ?subject  skos:prefLabel ?label .}

        """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()

        for result in results["results"]["bindings"]:
            return result["noOfArtists"]["value"]

    def get_all_performances(self, artist_name):
        self.sparql.setQuery(ArtistModel.prefixes + """
                SELECT DISTINCT ?perftitle 
                WHERE
               { ?artist rdf:type mo:MusicArtist. ?artist skos:prefLabel '""" + artist_name + """'. ?artist mo:performed ?perflinks. ?perflinks skos:prefLabel ?perftitle. ?perflinks etree:date ?perfdate. } order by asc(UCASE(str(?perfdate)))
        """)
        self.sparql.setReturnFormat(JSON)
        perf_titles = self.sparql.query().convert()
        return perf_titles

    def get_mb_tags(self, artist_name):
        self.sparql.setQuery(ArtistModel.prefixes + """
                        SELECT DISTINCT ?mbtags
                        WHERE
                       { 
                       ?artist rdf:type mo:MusicArtist. 
                       ?artist skos:prefLabel '""" + artist_name + """'. 
                       ?artist etree:mbTag ?mbtags
                       } 
                """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        return results

class PerformanceModel:
    prefixes = """
                PREFIX etree:<http://etree.linkedmusic.org/vocab/>
                PREFIX mo:<http://purl.org/ontology/mo/>
                PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX event:<http://purl.org/NET/c4dm/event.owl#> 
                """

    def __init__(self):
        self.sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")

    def get_all(self,max_offset_no):
        all_perf_names = []
        more_names = True
        offset_multiplier  = 0
        limit = 80000
        while (more_names):
            self.sparql.setQuery(PerformanceModel.prefixes + """

                                                        SELECT ?name
                                                            WHERE 
                                                            {
                                                            ?subject rdf:type etree:Concert.
                                                            ?subject skos:prefLabel ?name
                                                            } LIMIT 80000 OFFSET """ + str(offset_multiplier * limit))
            self.sparql.setReturnFormat(JSON)
            offset_multiplier += 1
            perf_names = self.sparql.query().convert()["results"]["bindings"]

            # isolate values from list of dictionaries
            perf_names = [perf_dict["name"]["value"] for perf_dict in perf_names]

            all_perf_names.append(perf_names)

            #the last batch will be less than 80.000
            if (len(perf_names) < 80000 or offset_multiplier == max_offset_no):
                more_names = False
        print(len(all_perf_names))
        return all_perf_names

    def get_performance(self,perf_name):
        self.sparql.setQuery(PerformanceModel.prefixes +
        """
        SELECT DISTINCT ?label WHERE
        {

            ?perf rdf:type etree:Concert.
            ?perf skos:prefLabel ?label.        
            filter (regex(?label, '"""+perf_name+"""', "i"))
        } ORDER BY asc(UCASE(str(?perf)))
        """)

        self.sparql.setReturnFormat(JSON)
        perf_names = self.sparql.query().convert()["results"]["bindings"]
        # isolate values from list of dictionaries
        perf_names = [perf_dict["label"]["value"] for perf_dict in perf_names]
        #print(perf_names)
        return perf_names

    def get_all_count(self):
        self.sparql.setQuery(PerformanceModel.prefixes + """
                SELECT(COUNT(?label) as ?noOfPerformances)
                WHERE
                { ?subject rdf:type etree:Concert . ?subject  skos:prefLabel ?label }

        """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()

        for result in results["results"]["bindings"]:
            return result["noOfPerformances"]["value"]

    def get_all_tracks(self, perf_name):
        self.sparql.setQuery(PerformanceModel.prefixes + """
                SELECT DISTINCT ?id ?tracktitle (GROUP_CONCAT(?audiolink, ' , ') as ?audiolinks) 
               
           WHERE{ 
                 ?perf rdf:type etree:Concert. 
                 ?perf skos:prefLabel '"""+perf_name+"""'. 
                 ?perf event:hasSubEvent ?tracklinks .  
                 ?tracklinks skos:prefLabel ?tracktitle .
                 ?tracklinks etree:audio ?audiolink.
                 ?tracklinks etree:number ?id 
               }group by ?id ?tracktitle  order by asc(?id)
        """)

        self.sparql.setReturnFormat(JSON)

        tracks = self.sparql.query().convert()["results"]["bindings"]
        # isolate values from list of dictionaries
        track_titles = [track_dict["tracktitle"]["value"] for track_dict in tracks]
        audio_links = [track_dict["audiolinks"]["value"] for track_dict in tracks]


        audio = np.zeros(50, dtype=np.ndarray)
        track_index = 0
        for track in audio_links:

            string = track
            audio[track_index] = string.split(",")
            #print("TRACK" + str(audio[track_index][1]))
            track_index+=1

        return track_titles, audio

    def get_artist(self, perf_name):
        self.sparql.setQuery(PerformanceModel.prefixes + """
                        SELECT DISTINCT ?artname 
                        WHERE
                       {  
                            ?perf rdf:type etree:Concert.
                            ?perf skos:prefLabel'""" + perf_name + """' .
                            ?perf mo:performer ?artlink.
                            ?artlink skos:prefLabel ?artname
                       } 
                """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for result in results["results"]["bindings"]:
            return result["artname"]["value"]

    def get_venue(self, perf_name):
        self.sparql.setQuery(PerformanceModel.prefixes + """
                        SELECT DISTINCT ?venuename 
                        WHERE
                       {  
                            ?perf rdf:type etree:Concert.
                            ?perf skos:prefLabel '""" + perf_name + """' .
                            ?perf event:place ?venuelink.
                            ?venuelink skos:prefLabel ?venuename
                       } """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for result in results["results"]["bindings"]:
            return result["venuename"]["value"]

    def get_date(self, perf_name):
        self.sparql.setQuery(PerformanceModel.prefixes + """
                        SELECT DISTINCT ?perfdate 
                        WHERE
                       {  
                            ?perf rdf:type etree:Concert.
                            ?perf skos:prefLabel '""" + perf_name + """' .
                            ?perf etree:date ?perfdate
                       } 
                """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for result in results["results"]["bindings"]:
            return result["perfdate"]["value"]

    def get_description(self, perf_name):
        self.sparql.setQuery(PerformanceModel.prefixes + """
                        SELECT DISTINCT ?perfdescr 
                        WHERE
                       {  
                            ?perf rdf:type etree:Concert.
                            ?perf skos:prefLabel'""" + perf_name + """' .
                            ?perf etree:description ?perfdescr
                       } 
                """)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for result in results["results"]["bindings"]:
            return result["perfdescr"]["value"]


class TrackModel:
    prefixes = """
                PREFIX etree:<http://etree.linkedmusic.org/vocab/>
                PREFIX mo:<http://purl.org/ontology/mo/>
                PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX calma: <http://calma.linkedmusic.org/vocab/>
                PREFIX event:<http://purl.org/NET/c4dm/event.owl#> """

    def __init__(self):
        self.sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")

    def get_all(self):
        all_track_names = []
        more_names = True
        offset_multiplier = 0
        limit = 80000
        while (more_names):
            self.sparql.setQuery(TrackModel.prefixes + """

                                                        SELECT ?name
                                                            WHERE 
                                                            {
                                                            ?subject rdf:type etree:Track.
                                                            ?subject skos:prefLabel ?name
                                                            } LIMIT 80000 OFFSET """ + str(offset_multiplier * limit))
            self.sparql.setReturnFormat(JSON)
            offset_multiplier += 1
            track_names = self.sparql.query().convert()["results"]["bindings"]

            # isolate values from list of dictionaries
            track_names = [track_dict["name"]["value"] for track_dict in track_names]

            all_track_names.append(track_names)

            if (len(track_names) < 80000):
                more_names = False

        return all_track_names

    def get_all_calma_tracks(self):
        all_track_names = []
        more_names = True
        offset_multiplier = 0
        limit = 80000
        while (more_names and offset_multiplier < 1):
            self.sparql.setQuery(TrackModel.prefixes + """

                                                        SELECT ?name ?calma_link
                                                            WHERE 
                                                            {
                                                            ?track rdf:type etree:Track.
                                                            ?track skos:prefLabel ?name.
                                                            ?track  calma:data ?calma_link
                                                            } LIMIT 80000 OFFSET """ + str(offset_multiplier * limit))
            self.sparql.setReturnFormat(JSON)
            offset_multiplier += 1
            track_names0 = self.sparql.query().convert()["results"]["bindings"]

            # isolate values from list of dictionaries
            track_names = [track_dict["name"]["value"] for track_dict in track_names0]
            calma_links  = [track_dict["calma_link"]["value"] for track_dict in track_names0]
            print(track_names[1])
            print(calma_links[0])

            response = urllib.request.urlopen(calma_links[0]+"/analyses.ttl")
            myfile = response.read()
            g = rdflib.Graph()
            g.load(myfile)

            # the QueryProcessor knows the FOAF prefix from the graph
            # which in turn knows it from reading the RDF/XML file
            for row in g.query(
                    'select ?s where { []prov:Activityde  prov:wasAssociatedWith <http://calma.linkedmusic.org/software_agents/sonic_annotator>,<http://vamp-plugins.org/rdf/plugins/qm-vamp-plugins#qm-tempotracker>, <http://vamp-plugins.org/rdf/plugins/qm-vamp-plugins#qm-tempotracker_output_beats>.}'):
                print(row.s)

            #print(myfile)
            all_track_names.append(track_names)

            if (len(track_names) < 80000):
                more_names = False

        return all_track_names

    def get_all_count(self):
        self.sparql.setQuery(TrackModel.prefixes + """
                SELECT(COUNT(?track) as ?noOfTracks)
                WHERE
                { 
                    ?track rdf:type etree:Track . 
                    ?track  skos:prefLabel ?label .
                }

        """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()

        for result in results["results"]["bindings"]:
            return result["noOfTracks"]["value"]

    def get_all_calma_count(self):
        self.sparql.setQuery(TrackModel.prefixes + """
                SELECT(COUNT(?track) as ?noOfTracks)
                WHERE
                { 
                    ?track rdf:type etree:Track . 
                    ?track  skos:prefLabel ?label .
                    ?track  calma:data ?calma_data
                }

        """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()

        for result in results["results"]["bindings"]:
            return result["noOfTracks"]["value"]

    def get_artists(self, track_name):
        self.sparql.setQuery(TrackModel.prefixes + """
                                SELECT DISTINCT ?artname 
                                WHERE
                               {  
                                    ?track rdf:type etree:Track .
                                    ?track skos:prefLabel'""" + track_name + """' .
                                    ?track etree:isSubEventOf ?artlink.
                                    ?artlink skos:prefLabel ?artname.
                               }            
                        """)
        self.sparql.setReturnFormat(JSON)
        artist_names = self.sparql.query().convert()["results"]["bindings"]
        # isolate values from list of dictionaries
        artist_names = [artist_dict["name"]["value"] for artist_dict in artist_names]

        return artist_names

    def get_performances(self, track_name):
        self.sparql.setQuery(TrackModel.prefixes + """
                                       SELECT DISTINCT ?perfname ?audiolink ?artname 
                                       WHERE
                                      {  
                                           ?track rdf:type etree:Track .
                                           ?track skos:prefLabel ?trackname .
                                           ?track etree:isSubEventOf ?perflink.
                                           ?track etree:audio ?audiolink .
                                           ?track mo:performer ?artlink .
                                           ?artlink skos:prefLabel ?artname .
                                           ?perflink skos:prefLabel ?perfname.   
                                            FILTER (regex(?trackname, '"""+track_name+"""', "i"))
                                      } GROUP BY ?perfname ORDER BY asc(UCASE(str(?artname)))
                               """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        return results

    def get_analyses(self, track_name, artist):
        #subprocess.call("tempo.R")
        tracks = {}
        tempos = []
        #getting durations
        self.sparql.setQuery(TrackModel.prefixes + """
            SELECT DISTINCT ?audio
            {
                SELECT ?track ?audio 
                WHERE 
                {
                ?artist skos:prefLabel "Guster".
                ?artist mo:performed ?performance .
                ?performance event:hasSubEvent ?track .
                ?track calma:data ?calma.
                ?track  skos:prefLabel "The Captain".
                ?track etree:audio ?audio
                }ORDER BY ?calma LIMIT 102
}
                                       """)
        self.sparql.setReturnFormat(JSON)
        audio_dict = self.sparql.query().convert()["results"]["bindings"]

        with open('TheCaptain-Guster.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            key_lengths = []
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:

                    line_count += 1
                    tempos.append(row[6])

                    #convert durations from one string to an array of floats
                    #keys
                    keys = row[2].split(',')
                    k_durs = np.fromstring(row[3], dtype=np.float, sep=',')
                    # chords
                    chords = row[4].split(',')
                    c_durs = np.fromstring(row[5], dtype=np.float, sep=',')

                    # key_durations
                    k_length = np.sum(k_durs)
                    key_lengths.append(k_length)
                    # chord_durations
                    c_length = np.sum(c_durs)

                    # TOTAL, key length is longer, could be used to approximate song length

                    # percentages
                    k_durs = np.true_divide(k_durs,k_length) * 100
                    c_durs = np.true_divide(c_durs,c_length) * 100

                    #combind keys/chords with their durations, each getting a dictionary
                    keys = dict(zip(keys, k_durs))
                    chords = dict(zip(chords, c_durs))
                    #trackname: keys,key-durations, chords, chord-durations, tempo,
                    tracks.update({ row[1]: [keys, chords, float(row[6]),np.asarray(key_lengths)] })

                    #print("%d: Trackname :%s\n Tempo :%s\n Keys :%s\n K-durs :%s\n "+
                           #"Chords :%s\n C-durs :%s\n"
                         # % (row+1, tracks[row[0]], tracks[row[0]][0], tracks[row[0]][1], tracks[row[0]][2], tracks[row[0]][3], tracks[row[0]][4]))
            #print(f'Processed {line_count} lines.')


        return tracks
    def get_analysis_for_track(self,artist_name,track_name):
        df = pd.read_csv('./calma_data/' + artist_name + "/" + track_name + '.csv')
        print(df.head(5))
        return "hello"
    def get_actual_tempo_and_key(self):


        # api-endpoint
        URL = "http://api.getsongbpm.com/song/?api_key=437f09edee1237d0fc3661edeb854888&id=4xYno0"


        # sending get request and saving the response as response object
        r = requests.get(url=URL)

        # extracting data in json format
        data = r.json()

        # extracting latitude, longitude and formatted address
        # of the first matching location
        tempo = 114# data['song']['tempo']
        key = "C" #data['song']['key_of']


        # printing the output
        print("Tempo:%s\nKey:%s"
              % (tempo, key))

        studio_data = {"tempo":tempo,"key":key}
        return studio_data

    def get_calma_track(self,artist_name,track_name):
        self.sparql.setQuery(TrackModel.prefixes + """
        SELECT DISTINCT ?calma_link ?art_name ?perf_date ?track_name (GROUP_CONCAT(?audio_link, ' , ') as ?audio_links) 
                                                            WHERE 
                                                            {
                                                            ?track rdf:type etree:Track.
                                                            ?track skos:prefLabel ?track_name.
                                                            ?track calma:data ?calma_link.
                                                            ?track mo:performer ?artist.
                                                            ?artist skos:prefLabel ?art_name.
                                                            ?track etree:audio ?audio_link.
                                                            ?track etree:isSubEventOf ?performance.
                                                            ?performance etree:date ?perf_date.
FILTER (regex(?track_name, "Zero", "i")).
                                                            FILTER (regex(?art_name, "Smashing Pumpkins", "i"))} ORDER BY(?perf_date)""")
        self.sparql.setReturnFormat(JSON)
        calma_track = self.sparql.query().convert()["results"]["bindings"]

        # isolate values from list of dictionaries
        calma_links = [calma_dict["calma_link"]["value"] for calma_dict in calma_track]
        audio_links = [calma_dict["audio_links"]["value"] for calma_dict in calma_track]
        perf_dates = [calma_dict["perf_date"]["value"] for calma_dict in calma_track]
        track_names = [calma_dict["track_name"]["value"] for calma_dict in calma_track]
        #NOTE: COUNT OF TRACKS SHOULD BE USED TO SIZE MATRIX
        audio = np.zeros(400, dtype=np.ndarray)
        track_index = 0
        for track in audio_links:
            string = track
            audio[track_index] = string.split(",")
            #print("TRACK" + str(audio[track_index][1]))
            track_index += 1

        return calma_links,audio,perf_dates,track_names

class VenueModel:
    prefixes = """
                PREFIX etree:<http://etree.linkedmusic.org/vocab/>
                PREFIX mo:<http://purl.org/ontology/mo/>
                PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>"""

    def __init__(self):
        self.sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")

    def get_all(self):
        all_venue_names = []
        more_names = True
        offset_multiplier = 0
        limit = 80000
        while (more_names):
            self.sparql.setQuery(VenueModel.prefixes + """

                                                        SELECT ?name
                                                            WHERE 
                                                            {
                                                            ?subject rdf:type etree:Venue.
                                                            ?subject skos:prefLabel ?name
                                                            } LIMIT 80000 OFFSET """ + str(offset_multiplier * limit))
            self.sparql.setReturnFormat(JSON)
            offset_multiplier += 1
            venue_names = self.sparql.query().convert()["results"]["bindings"]




            # isolate values from list of dictionaries
            venue_names = [venue_dict["name"]["value"] for venue_dict in venue_names]

            all_venue_names.append(venue_names)

            if (len(venue_names) < 80000):
                more_names = False

        return all_venue_names

    def get_venue(self,venue_name):
        self.sparql.setQuery(PerformanceModel.prefixes +
        """
        SELECT DISTINCT ?label WHERE
        {
            ?venue rdf:type etree:Venue.
            ?venue skos:prefLabel ?label.
            FILTER (regex(?label, '"""+venue_name+"""', "i"))
        } ORDER BY asc(UCASE(str(?venue)))
        """)

        self.sparql.setReturnFormat(JSON)
        venue_names = self.sparql.query().convert()["results"]["bindings"]
        # isolate values from list of dictionaries
        venue_names = [venue_dict["label"]["value"] for venue_dict in venue_names]
        print(venue_names)
        return venue_names


    def get_all_count(self):
        self.sparql.setQuery(VenueModel.prefixes + """
                SELECT(COUNT(?label) as ?noOfVenues)
                WHERE
                { ?subject rdf:type etree:Venue . ?subject  skos:prefLabel ?label .}

        """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()

        for result in results["results"]["bindings"]:
            return result["noOfVenues"]["value"]

    def get_location(self, venue_name):
        self.sparql.setQuery(VenueModel.prefixes +
                             """SELECT DISTINCT ?locname
                        WHERE
                        {
                        ?venue rdf:type etree:Venue.
                        ?venue  skos:prefLabel '""" + venue_name + """'.
                        ?venue etree:location ?locname
                        }""")
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        return results

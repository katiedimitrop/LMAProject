import os
import numpy as np
import csv
from rdflib.graph import Graph
import requests
import tarfile
import re
from model_service import TrackService
from operator import itemgetter
artist_name = "Grateful Dead"
track_name = "Ripple"
mean_tempos = []

calma_links,audio_links, perf_dates,track_names = TrackService().get_calma_track(artist_name,track_name)

no_of_perfs = len(calma_links)
prefixes = """
PREFIX af: <http://purl.org/ontology/af/>
PREFIX mo: <http://purl.org/ontology/mo/>
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX tl: <http://purl.org/NET/c4dm/timeline.owl#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

#queries we'll make to the rdf
# CHORDS and their DURATIONS
whatFeaturesQuery = """ prefix prov: <http://www.w3.org/ns/prov#>
select distinct ?file ?feature where {
   ?file prov:wasAssociatedWith ?feature
}
ORDER BY ?feature"""

chordFeatureQuery = prefixes+ """

select distinct ?event ?chord ?onsetTime where {
  ?event a af:ChordSegment ;
         event:time ?time ;
         rdfs:label ?chord .
  ?time tl:at ?onsetTime .
}
ORDER BY ?event """

# Keys and their DURATIONS
keyFeatureQuery = prefixes + """

select distinct ?event ?feature ?key ?onsetTime where { 
  ?event a af:KeyChange ;
         event:time ?time ;
         af:feature ?feature ;
         rdfs:label ?key .
  ?time tl:at ?onsetTime .
}
ORDER BY ?event"""

#Tempos
tempoFeatureQuery = prefixes + """
select distinct ?event ?feature ?onsetTime where { 

  ?event a af:Tempo ;
         event:time ?time ;
         af:feature ?feature .
  ?time tl:at ?onsetTime .
  
}
ORDER BY ?event
"""
durationQuery = prefixes + """
select distinct ?duration {
  ?signal a mo:Signal;
         mo:time ?time.
  ?time tl:duration ?duration.
}ORDER BY ?duration
"""
getFeatureBlob = """select distinct ?s ?blob 
where { 
?s <http://calma.linkedmusic.org/vocab/feature_blob> ?blob 
} ORDER BY ?blob

"""

all_key_durs = np.zeros((no_of_perfs ,25), dtype=np.ndarray)
all_durs = np.zeros(no_of_perfs)
#feature numbers of keys, not indeces
all_max_keys = np.zeros(no_of_perfs, dtype=np.int64)
#for each performance of Zero by Smashing Pumpkins (There's 368 of them) we want ot extract
#track,key,key_duration,chord,chord_duration,tempo
for perf_index in range(0,no_of_perfs):
    analyses = Graph()
    analyses.parse(calma_links[perf_index] + "/analyses.ttl")

    timeline = Graph()
    timeline.parse(calma_links[perf_index] + "/metadata#timeline_0")
    timeres = timeline.query(durationQuery)

    for duration in timeres:
        m = re.search('PT(.+?)S', str(duration))
        if m:
            found = m.group(1)

    total_dur = float(found)
    all_durs[perf_index] = total_dur
    # print("Total duration" + str(total_dur))
    # let's query rdf graph to check what features are available for this track
    qres = analyses.query(whatFeaturesQuery)
    f_index = 0
    features = []
    files = []
    for file, feature in qres:
        features.append(str(feature))
        files.append(str(file))
        f_index += 1
        # print("file: %s" % file)
        # print("feature: %s" % feature)

    for f_index in range(0, len(features) - 1):
        if (features[f_index] == "http://vamp-plugins.org/rdf/plugins/qm-vamp-plugins#qm-tempotracker_output_tempo"):
            tempo_link = files[f_index]
            print(perf_index)
            #print("Tempo link ")
            #print(tempo_link)

        if (features[f_index] == "http://vamp-plugins.org/rdf/plugins/qm-vamp-plugins#qm-keydetector_output_key"):
            # print("Key link ")
            key_link = files[f_index]
            # print(key_link)

        if (features[f_index] == "http://vamp-plugins.org/rdf/plugins/nnls-chroma#chordino_output_simplechord"):
            chord_link = files[f_index]
            # print("Chord link ")
            # print(chord_link)

    feature_links = [tempo_link, key_link]
    for feature_index in range(0, 2):
        # parse analysis page as graph to get blob FOR TEMPO
        analysis = Graph()
        analysis.parse(feature_links[feature_index])

        qres = analysis.query(getFeatureBlob)
        for subject, link in qres:
            blob_link = str(link)
            # print(blob_link)

        url = blob_link
        # print(url)
        regex = "(?:analysis_blob)(.*)"
        target_path = 'analysis_blob' + re.findall(regex, url)[0]
        # target_path = 'analysis_blob_73e77ba8-c990-41af-b912-802fbbbaf2a9.tar.bz2'

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # save tarred blob
            with open("./tar_files/" + target_path, 'wb') as f:
                f.write(response.raw.read())

        tar = tarfile.open("./tar_files/" + target_path, "r:bz2")
        # save untarred version in triples
        tar.extractall("./triples/" + target_path)
        tar.close()

        t_graph = Graph()
        os.listdir("./triples/" + target_path)[0]
        t_graph.parse("./triples/" + target_path + "/" + os.listdir("./triples/" + target_path)[0], format="ttl")
        # this is a tempo graph
        if (feature_index == 0):
            tempos_query = t_graph.query(tempoFeatureQuery)
            tempo_events = []

            for event, tempo, onset in tempos_query:
                # isolate event number from link
                event_num = [int(i) for i in event.split("_") if i.isdigit()]
                tempo_events.append([event_num, float(tempo), onset])

            tempo_events = sorted(tempo_events, key=itemgetter(0))
            print(tempo_events)
            tempos = []
            previous = next_ = None
            l = len(tempo_events)
            # pairwise iteration through key events
            sum_weighted_tempo = 0
            for this_event, next_event in zip(tempo_events[0:l], tempo_events[1:l]):
                onset = this_event[2].strip('PT').strip('S')
                #print(" event:" + str(this_event[0]) + " tempo:" + str(this_event[1]) + " onset:" + str(onset))
                # print(" tempo:"+ str(this_event[1]))
                next_onset = (next_event[2].strip('PT')).strip('S')
                # feature 1 will be stored at index 0
                # Tempo duration in each event is next tempo change onset minus this tempo_change onset
                #print("Sum so far:" + str(sum_weighted_tempo))
                #print("Onset: " + str(onset))
                sum_weighted_tempo += (float(next_onset) - float(onset))  * this_event[1]
                # for last key_change

            last_onset = (tempo_events[l - 1])[2]
            last_onset = float(last_onset.strip('PT').strip('S'))
            sum_weighted_tempo += (float(total_dur) - last_onset)  *(tempo_events[l - 1][1])

            mean_tempos.append(sum_weighted_tempo / total_dur)
        else:  # this is a key graph
            key_query_res = t_graph.query(keyFeatureQuery)
            key_events = []
            for event, feature, key, onset in key_query_res:
                event_num = [int(i) for i in event.split("_") if i.isdigit()]
                key_events.append([event_num, feature, key, onset])

            key_events = sorted(key_events, key=itemgetter(0))
            keys = []
            previous = next_ = None
            l = len(key_events)
            # each feature num [1,..,24,25] coresponds to a key [C,..,Bm,unknown]

            # pairwise iteration through key events
            for this_event, next_event in zip(key_events[0:l], key_events[1:l]):
                onset = this_event[3].strip('PT').strip('S')
                # print(" event:"+ str(this_event[0])+" feature:"+ str(this_event[1])+" key:"+ str(this_event[2])+" onset:"+ str(onset))
                # print(" key:"+ str(this_event[2]))
                next_onset = (next_event[3].strip('PT')).strip('S')
                # feature 1 will be stored at index 0
                # key duration in each event is next keychange onset minus this key_change onset
                all_key_durs[perf_index][int(this_event[1]) - 1] += float(next_onset) - float(onset)

            # for last key_change

            feature = int((key_events[l - 1])[1])
            last_onset = (key_events[l - 1])[3]
            last_onset = float(last_onset.strip('PT').strip('S'))
            all_key_durs[perf_index][feature - 1] += float(total_dur) - last_onset

            # sum_dur = 0 #to check if sum duration is equal to total
            max_key_dur = 0.0
            max_key_index = 0
            for index, key_dur in enumerate(all_key_durs[perf_index]):
                if (float(key_dur) > max_key_dur):
                    max_key_index = index
                    max_key_dur = key_dur
            all_max_keys[perf_index] = max_key_index + 1
            # print(str(index+1)+" " +str(key_dur))
            # sum_dur+=key_dur



row_list = [
    ["id", "Track Name", "Performance Date","Track duration","Tempo","Max Key","Keys","Key_durations"]
]
key_names = ["C", "Db / C#", "D", "Eb / D#", "E", "F", "Gb / F#", "G", "Ab / G#", "A", "Bb", "B/Cb",
             "Cm", "Dbm / C#m", "Dm", "Ebm / D#m", "Em", "Fm", "Gbm / F#m", "Gm", "Abm / G#m", "Am", "Bbm", "Bm/Cbm","unknown"]
for perf_id in range(0, no_of_perfs):

    non_empty_indeces = np.zeros(25, dtype=np.ndarray)
    keys_in_this_perf = []
    durs_in_this_perf = []
    max_key_index = 0
    max_key_dur = 0

    # go through all key durations in this track, isolate a list of the non zero ones
    # these are the only ones we'll keep in the csv
    for index, duration in enumerate(all_key_durs[perf_id]):
        if duration != 0:
            # set to one wherever there exists a duration
            non_empty_indeces[index] = 1
            durs_in_this_perf.append(duration)

    # using the flag indicators, isolate the key names that correspond to the previous
    # durations
    for index, flag in enumerate(non_empty_indeces):
        if flag:
            keys_in_this_perf.append(key_names[index])

    row_list.append([perf_id, track_names[perf_id], perf_dates[perf_id], all_durs[perf_id], str(mean_tempos[perf_id]),
                 int(all_max_keys[perf_id]), keys_in_this_perf, durs_in_this_perf])
print(all_max_keys)
counts = np.bincount(all_max_keys)
print(np.argmax(counts))

with open('./calma_data/' + artist_name + "/" + track_name + ".csv", 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(row_list)
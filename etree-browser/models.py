# where the querying happens
from SPARQLWrapper import SPARQLWrapper, JSON


# class generalQueryModel: #for the general queryer that will be implemented later

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
        results = self.sparql.query().convert()
        return results

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
        # Define the query
        self.sparql.setQuery(VenueModel.prefixes + """
                SELECT DISTINCT ?name
                WHERE 
                {
                ?subject rdf:type etree:Venue.
                ?subject skos:prefLabel ?name
                } order by asc(UCASE(str(?name)))
            """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        print(results)
        return results

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

    def get_all(self):
        # Define the query
        self.sparql.setQuery(PerformanceModel.prefixes + """
                SELECT DISTINCT ?name
                WHERE 
                {
                ?subject rdf:type etree:Concert.
                ?subject skos:prefLabel ?name
                } order by asc(UCASE(str(?name)))
            """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        print(results)
        return results

    def get_all_count(self):
        self.sparql.setQuery(PerformanceModel.prefixes + """
                SELECT(COUNT(?label) as ?noOfPerformances)
                WHERE
                { ?subject rdf:type etree:Concert . ?subject  skos:prefLabel ?label .}

        """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()

        for result in results["results"]["bindings"]:
            return result["noOfPerformances"]["value"]

    def get_all_tracks(self, perf_name):
        self.sparql.setQuery(PerformanceModel.prefixes + """
                SELECT DISTINCT ?tracktitle 
                WHERE
               { ?perf rdf:type etree:Concert. ?perf skos:prefLabel '""" + perf_name
                             + """'. ?perf event:hasSubEvent ?tracklinks .  ?tracklinks skos:prefLabel ?tracktitle  } 
        """)
        self.sparql.setReturnFormat(JSON)
        track_titles = self.sparql.query().convert()

        return track_titles

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
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>"""

    def __init__(self):
        self.sparql = SPARQLWrapper("http://etree.linkedmusic.org/sparql")

    def get_all(self):
        # Define the query
        self.sparql.setQuery(TrackModel.prefixes + """
                SELECT DISTINCT ?trackname
                WHERE 
                {
                ?track rdf:type etree:Track.
                ?track skos:prefLabel ?trackname
                } order by asc(UCASE(str(?trackname))) OFFSET 1
            """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        return results

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

    def get_artist(self, track_name):
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
        results = self.sparql.query().convert()
        for result in results["results"]["bindings"]:
            return result["artname"]["value"]

    def get_performance(self, track_name):
        self.sparql.setQuery(TrackModel.prefixes + """
                                       SELECT DISTINCT ?perfname ?audiolink ?artname 
                                       WHERE
                                      {  
                                           ?track rdf:type etree:Track .
                                           ?track skos:prefLabel'""" + track_name + """' .
                                           ?track etree:isSubEventOf ?perflink.
                                           ?track etree:audio ?audiolink .
                                           ?track mo:performer ?artlink .
                                           ?artlink skos:prefLabel ?artname .
                                           ?perflink skos:prefLabel ?perfname   
                               
                                      } GROUP BY ?perfname ORDER BY asc(UCASE(str(?artname)))
                               """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        return results
        # for result in results["results"]["bindings"]:
        # return result["perfname"]["value"]

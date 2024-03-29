#!/usr/bin/env RScript
 # ONLY NEED TO DO THIS BEFORE THE FIRST USE OF THE SCRIPT
    install.packages(c("RCurl", "SPARQL", "ggplot2", "rJava", "devtools","dplyr"),repos = "http://cran.us.r-project.org")
    library("devtools")
    install_github("egonw/rrdf", subdir="rrdflibs")
    install_github("egonw/rrdf", subdir="rrdf", build_vignettes=FALSE)
library("RCurl")
library("SPARQL")
library("rrdf")
library("ggplot2")
library(dplyr)
setwd(tempdir())
#following line: see http://www.bramschoenmakers.nl/en/node/726
options( java.parameters = "-Xmx3g" )
endpoint = "http://etree.linkedmusic.org/sparql"

etreeTrackQuery <- "
PREFIX etree:<http://etree.linkedmusic.org/vocab/>
PREFIX mo:<http://purl.org/ontology/mo/>
PREFIX event:<http://purl.org/NET/c4dm/event.owl#>
PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
PREFIX timeline:<http://purl.org/NET/c4dm/timeline.owl#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX calma:<http://calma.linkedmusic.org/vocab/>
SELECT ?track ?calma
{
  BIND(<http://etree.linkedmusic.org/artist/422feb50-4aac-012f-19e9-00254bd44c28> as ?artist) .
  ?artist mo:performed ?performance .
  ?performance event:hasSubEvent ?track .
  ?track calma:data ?calma ;
  skos:prefLabel \"The Captain\" .
  }
  ORDER BY ?calma
  LIMIT 102
  "
whatFeaturesQuery <- "
prefix prov: <http://www.w3.org/ns/prov#>
select distinct ?feature where {
   ?file prov:wasAssociatedWith ?feature
}
ORDER BY ?feature"

calmaFeatureQuery <- "
PREFIX af: <http://purl.org/ontology/af/>
PREFIX mo: <http://purl.org/ontology/mo/>
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX tl: <http://purl.org/NET/c4dm/timeline.owl#>

select ?event ?feature where {
  ?file a mo:AudioFile .
  ?event a af:Tempo ;
         af:feature ?feature .
}
ORDER BY ?file"

graphify <- function(files, remote=TRUE) {
  if(remote) {
    files <- gsub('<|>', '', files) # get rid of uri decoration if any
    data <- gsub('\\"', '"', getURL(files)) # un-escape quote marks
    files = gsub("http://calma.linkedmusic.org/data/", "", files)
    files = gsub("/", "--", files)
  }
  else { # got sent a local directory
    files <- paste0(files, "/", list.files(files))
  }

  g = new.rdf()
  for (f in 1:length(files)) {
    if(remote){ # need to write to our local tmp folder
      track <- files[f]
      track <- regmatches(track, gregexpr(pattern = "track_[^/]*", track))[[1]]
      cat(x=data[f], file=files[f], append=FALSE)
    }
    thisg = load.rdf(filename = files[f], format="TURTLE")
    g = combine.rdf(g, load.rdf(filename = files[f], format="TURTLE"))
  }
  return(g)
}

untarBlobs <- function(blobURIs) {
  tmp = tempfile(tmpdir = tempdir())
  blobFiles <- basename(blobURIs)
  for (f in 1:length(blobFiles)) {
    download.file(blobURIs[f], blobFiles[f])
    untar(blobFiles[f], compressed = 'gzip', exdir = tmp)
    file = gsub(".tar.gz", "", blobFiles[f])
    file = gsub(".tar.bz2", "", file)
    file <- paste0(tmp,  "/", file)
  }
  files <- paste0(tmp, "/", list.files(tmp))
  print("---------------------")
  for (f in 1:length(files)) {
      contextualized <- gsub("<#>", paste0("<", files[f], "#>"), readLines(files[f]))
      cat(x = contextualized, file=files[f], append = FALSE)

    }
  return(tmp)
}

queryFeatureFiles <- function(g, feature) {
  calmaFileQuery <- paste0("
  prefix prov: <http://www.w3.org/ns/prov#>
  select distinct ?file where {
     ?file prov:wasAssociatedWith <", feature, ">
  }
  ORDER BY ?file")
  files <- sparql.rdf(g, calmaFileQuery)
  return (files)
}

result <- SPARQL(endpoint, etreeTrackQuery)$results
# chop off the <'s and >'s
calma <- substr(result$calma, 2, nchar(result$calma))
calma <- substr(calma, 1, nchar(calma)-1)
# add trailing /
calma <- paste0(calma, "/")
files <- paste0(calma, "analyses.ttl")
etreeCalma <- cbind(result, files)
g <- graphify(files)

# What features are available for these files?
features <- sparql.rdf(g, whatFeaturesQuery)

featurefiles <- queryFeatureFiles(g, features[18])
g <- graphify(featurefiles)
etreeCalma <- cbind(etreeCalma, featurefiles)
names(etreeCalma) <- c("etree", "calma", "analysis.ttl", "feature")
etreeCalma$etree <- factor(etreeCalma$etree)
etreeCalma$calma<- factor(etreeCalma$calma)

query = "select distinct ?blob where { ?s <http://calma.linkedmusic.org/vocab/feature_blob> ?blob }"
blobFileURIs <- sparql.rdf(g, query)
blobFileDir <- untarBlobs(blobFileURIs)
featureGraph <- graphify(blobFileDir, remote=FALSE)
#summarize.rdf(featureGraph)

tempoData <- as.data.frame(sparql.rdf(featureGraph, calmaFeatureQuery))
tempoData$track <- factor((gsub(".*/([^/#]+)#.*", "\\1", as.character(tempoData$event),fixed=FALSE, perl=TRUE)))
tempoData$eventNum <- as.numeric(gsub(".*event_(\\d+)", "\\1", tempoData$event,fixed=FALSE, perl=TRUE))
tempoData$feature <- as.numeric(as.character(tempoData$feature))
tempoData <- unique(tempoData[order(tempoData$track, tempoData$eventNum),])
#ggplot(tempoData, aes(track, feature)) + geom_boxplot() + theme_bw() +
  #theme(axis.text.x = element_text(angle=90))
#ggplot(tempoData, aes(eventNum, feature)) + geom_line(aes(color=track)) + facet_wrap(~track) + theme_bw()

#MY ADDITION: isolate trackname and tempo, then calculate means
strippedTempos <- tempoData %>% select(track,feature)
strippedTempos <- aggregate(.~track, data = strippedTempos, mean)

write.csv(strippedTempos,"TheCaptain-Tempo1.csv")







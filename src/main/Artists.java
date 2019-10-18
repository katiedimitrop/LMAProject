package main;

import org.apache.jena.query.*;

//This is a test run of querying the etree sparql endpoint to obtain 
//all the artists in the collection and display them on a localhost page

public class Artists extends Object

{
	public static void main(String[] args)
	{
		//Create a new query to get all artist names
		String queryString = 
		 
		"PREFIX foaf:  <http://xmlns.com/foaf/0.1/> SELECT ?name " +
		 "WHERE {" +
		 "?artist foaf:name ?name . "+ 
		  "}";
	   
		Query query = QueryFactory.create(queryString); 
	    QueryExecution qExe = QueryExecutionFactory.sparqlService( "http://etree.linkedmusic.org/sparql", query );
	    ResultSet results = qExe.execSelect();
	    ResultSetFormatter.out(System.out, results, query) ;	
	}

  
}


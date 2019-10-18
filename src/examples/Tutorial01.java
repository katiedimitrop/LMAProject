package examples;

import org.apache.jena.rdf.model.*;
import org.apache.jena.vocabulary.*;

    /** Tutorial 1 creating a simple model
	 */
	
	public class Tutorial01 extends Object
	{
	    // some definitions
	    static String personURI    = "http://somewhere/JohnSmith";
	    static String fullName     = "John Smith";
	    static String givenName     = "John";
	    static String familyName     = " Smith";
	      public static void main (String args[]) 
	      {
	        // create an empty model
	        Model model = ModelFactory.createDefaultModel();
	
	     // create the resource
	    //and add the properties cascading style
	   Resource johnSmith
	     = model.createResource(personURI)
	            .addProperty(VCARD.FN, fullName)
	            .addProperty(VCARD.N,
	                         model.createResource()
	                              .addProperty(VCARD.Given, givenName)
	                              .addProperty(VCARD.Family, familyName));
	        System.out.println("That's all folks");     
	      }
	      
	      //Statement or triple: each arc in an RDF model.. asserts a fact about a resource
	      //subject(resource)/predicate(property)/object(target resource or literal)
	}
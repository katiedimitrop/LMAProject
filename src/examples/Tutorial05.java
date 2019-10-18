package examples;

import java.io.File;
import java.io.InputStream;

import org.apache.jena.rdf.model.*;
import org.apache.jena.util.FileManager;
import org.apache.jena.vocabulary.*;

//Writing RDF in its xml form 
public class Tutorial05 extends Object 
{
	
	static final String inputFileName  = "src/examples/vc-db-1.rdf";
    public static void main (String args[]) 
    {     
    	System.out.println(new File(".").getAbsoluteFile());
        // create an empty model
        Model model = ModelFactory.createDefaultModel();

        // use the FileManager to find the input file
        InputStream in = FileManager.get().open( inputFileName );
       if (in == null) {
           throw new IllegalArgumentException(
                                        "File: " + inputFileName + " not found");
       }

       // read the RDF/XML file
       //second argument can be a relative URI 
       model.read(in, null);

       // write it to standard out
       model.write(System.out);
            
             
        
    }
}
    
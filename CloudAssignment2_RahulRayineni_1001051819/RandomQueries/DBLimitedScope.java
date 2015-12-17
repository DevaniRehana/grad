/*
 *   Name: Rahul Rayineni
 *     Id: 1001051819
 * Course: CSE 6331-002
 * Assignment-2 Step-8: Calculating the Query time for 2000 random queries on 2000 limited 
 */

package amazon;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Random;

import org.springframework.util.StopWatch;

/*
 * In this class I calculated the query time for 2000 random queries on 
 * 2000 limited set of tuples 
 */

public class DBLimitedScope {
	
	// JDBC driver name and database URL
	   static final String JDBC_DRIVER = "com.mysql.jdbc.Driver";  
	   static final String DB_URL = "jdbc:mysql://cloud.cqttge96yqpa.us-west-2.rds.amazonaws.com/clouduta";

	   //  Database credentials
	   static final String USER = "root";
	   static final String PASS = "clouduta";
	   
	public static void main(String[] args) {
	   Connection conn = null;
	   Statement stmt = null;
	   
	   try{
	      //Register JDBC driver
	      Class.forName("com.mysql.jdbc.Driver");

	      //Open a connection with the amazon RDS point url, username and password for the db
	      System.out.println("Connecting to database...");
	      conn = DriverManager.getConnection(DB_URL,USER,PASS);

	      //Create a statement to execute the query
	      System.out.println("Creating statement...");
	      stmt = conn.createStatement();
	      
	      int c=0;
	      
	     //Random Number generator class to generate a random number with the given range
	      Random rand = new Random();
	      
	      //randomnumber to store the random number
	      int randomNum =0;
	      
	      //Dropping the view if already exits and then creating it
	      stmt.executeUpdate("DROP VIEW IF EXISTS Scope;");
	      
	      //Creating a view with 2000 Set of tuples
	      String createView ="create view Scope as ("
	  			+ "select * from all_month limit 2000"+");";
	      
	      System.out.println("View created with 2000 set of tuples");
	      
	      stmt.executeUpdate(createView);
	      
	      //Starting the timer
	      StopWatch s=new StopWatch();
	      s.start();
	      
	      /*
	       *  In this loop we execute a query for 2000 times on 2000 set of tuples
	       */ 
	      
	      while(c<=2000)  
	    {  	
	    
	    	//generating the random number between 1 and 30  
	    	randomNum = rand.nextInt((30-1)+1)+1;  
	    	
	    	//Random Query on 2000 set of tuples
	       stmt.executeQuery("SELECT latitude,longitude,mag FROM Scope where nst="+randomNum+";");
	       
	       System.out.println("Query Executed ---->"+c);
	       
	       c++;      
	       
	    }  
	      
	      //end the timer 
	      s.stop();
	      
	      //printing the time taken to execute queries in seconds
	      System.out.println("Time taken to execute 2000 queries on 2000 limited scope "+s.getTotalTimeSeconds()+" secs");

	      
	      stmt.close();
	      conn.close();
	   }catch(SQLException se){
	      //Handle errors for JDBC
	      se.printStackTrace();
	   }catch(Exception e){
	      //Handle errors for Class.forName
	      e.printStackTrace();
	   }finally{
	      //finally block used to close resources
	      try{
	         if(stmt!=null)
	            stmt.close();
	      }catch(SQLException se2){
	      }// nothing we can do
	      try{
	         if(conn!=null)
	            conn.close();
	      }catch(SQLException se){
	         se.printStackTrace();
	      }//end finally try
	   }//end try
	   System.out.println("Goodbye!");
	}//end main

}

/*
 *   Name: Rahul Rayineni
 *     Id: 1001051819
 * Course: CSE 6331-002
 * Assignment-2 Step-8: Displaying the time magnitude relationship 
 */

package amazon;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Random;

import org.springframework.util.StopWatch;

public class TimeMagnitude {

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
	      stmt = conn.createStatement();
	      
	      //sql query ti calculate the time magnitude relationship
	      String sql;
	      sql= "Select week(time_date) as week ,avg(mag) as magnitude from all_month group by week order by magnitude";
	       
	      ResultSet rs = stmt.executeQuery(sql);
	     
	      while(rs.next()){
	          //Retrieve by column name
	          String w  = rs.getString("week");
	          String m = rs.getString("magnitude");
	         
	          //Display values
	          System.out.println("week"  + w);
	          System.out.println("average magnitude of week " +w+" is "+m);
	         
	       }
	      
	      //close all resources
	       rs.close();
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

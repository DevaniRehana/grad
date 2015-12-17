/*
 *   Name: Rahul Rayineni
 *     Id: 1001051819
 * Course: CSE 6331-002
 * Assignment-2: Calculating the Query time for 2000 random queries  
 */

package amazon;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import org.springframework.util.StopWatch;


public class MySqlModule {

	
	/*
	 * In this method we insert data from CSV file to RDS  
	 * 
	 */
	
 public static void execute_insert(String fileName) throws FileNotFoundException{
	 
	 final String JDBC_DRIVER = "com.mysql.jdbc.Driver";  
	 
	 final String DB_URL = "jdbc:mysql://cloud.cqttge96yqpa.us-west-2.rds.amazonaws.com/clouduta";
	 
	 //  Database credentials
	 final String USER = "root";
	 final String PASS = "clouduta";
	 
	 //splitting the csv file based on delimiter ,
	 String splitBy = ",";
        
     BufferedReader br = new BufferedReader(new FileReader("C:\\Users\\rayin_000\\Desktop\\"+fileName));

     String line;

    //Connection and statement variables to hold the variables  
     Connection conn = null;
     Statement statement = null;
     PreparedStatement stmt = null;
     


try{
    // Register JDBC driver
    Class.forName(JDBC_DRIVER);

    //Open a connection
    System.out.println("Connecting to a selected database...");
    conn = DriverManager.getConnection(DB_URL, USER, PASS);
    System.out.println("database connected successfully...");
    
    //Getting a statement object to execute the queries
    
    statement = conn.createStatement();
    
   
    //Checking the table if already exists in RDS, If exists drop the table
    
    statement.executeUpdate("DROP TABLE IF EXISTS all_month;");
    
    
    System.out.println("creating table in databse");
    
    
    //Creating a table in RDS to store the CSV File data
    
    String createTableSQL ="create table all_month("
			+ "time_date VARCHAR(30),"
			+ "latitude VARCHAR(30),"
			+ "longitude VARCHAR(30),"
			+ "depth VARCHAR(30),"
			+ "mag VARCHAR(30),"
			+ "magType VARCHAR(30),"
			+ "nst VARCHAR(30),"
			+ "gap VARCHAR(30),"
			+ "dmin VARCHAR(30),"
			+ "rms VARCHAR(30),"
			+ "net VARCHAR(30),"
			+ "id VARCHAR(30),"
			+ "updated VARCHAR(30),"
			+ "place VARCHAR(100),"
			+ "type VARCHAR(30));";

    statement.executeUpdate(createTableSQL);
  
    System.out.println("Table created successfully in database");
    
    
    //STEP 4: Execute a query
    System.out.println("Inserting records into the table...");
	
    br.readLine();
	
    StopWatch s=new StopWatch();
    
	s.start();  
		

	while((line = br.readLine()) !=null){
      
	  String[] b = line.split(splitBy);
      
      stmt = conn.prepareStatement("INSERT INTO all_month VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)");//select statement type here
      stmt.setString(1, b[0]);
      stmt.setString(2, b[1]);
      stmt.setString(3, b[2]);
      stmt.setString(4, b[3]);
      stmt.setString(5, b[4]);
      stmt.setString(6, b[5]);
      stmt.setString(7, b[6]);
      stmt.setString(8, b[7]);
      stmt.setString(9, b[8]);
      stmt.setString(10, b[9]);
      stmt.setString(11, b[10]);
      stmt.setString(12, b[11]);
      stmt.setString(13, b[12]);
      if(b.length==16)
      {
      stmt.setString(14, b[13]+","+b[14]);
      stmt.setString(15, b[15]);
      }
      else if(b.length==15)
      {
    	  stmt.setString(14, b[13]);
    	  stmt.setString(15, b[14]);
    	  
      }
      else if(b.length==17)
      {
    	  
    	  stmt.setString(14, b[13]+","+b[14]+","+b[15]);
    	  stmt.setString(15, b[16]);
    	  
      }
      stmt.executeUpdate();
    }

     s.stop();
     System.out.println("Time taken to upload "+fileName+" data");
     System.out.println(s.getTotalTimeSeconds()+"secs");

br.close();
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
          conn.close();
    }catch(SQLException se){
    }// do nothing
    try{
       if(conn!=null)
          conn.close();
    }catch(SQLException se){
       se.printStackTrace();
    }//end finally try
 }//end try

 }
 

 /*
  * This method is for retrieving the data from RDS
 */
 public static void execute_select() {
	 
	 
	 final String JDBC_DRIVER = "com.mysql.jdbc.Driver";  
	 final String DB_URL = "jdbc:mysql://cloud.cqttge96yqpa.us-west-2.rds.amazonaws.com/clouduta";
	 
	 //  Database credentials
	 final String USER = "root";
	 final String PASS = "clouduta";
        

     Connection conn = null;
     Statement stmt = null;
     String sql;



try{
    // Register JDBC driver
    Class.forName(JDBC_DRIVER);

    // Open a connection
    System.out.println("Connecting to a selected database...");
    conn = DriverManager.getConnection(DB_URL, USER, PASS);
    System.out.println("Connected database successfully...");
    
    // Getting a statement object to execute a query
    stmt = conn.createStatement();
	
    //Sql Query to retrieve the data from RDS
    sql = "Select * from all_month";
	
    //Stopwatch class from spring framework to calculate the time 
	StopWatch s=new StopWatch();
    
	s.start();  
	
    ResultSet rs = stmt.executeQuery(sql);
	
	while(rs.next()){
        
		//Retrieve by column name
        System.out.print("time " + rs.getString("time_date"));
        System.out.print("latitude " + rs.getString("latitude"));
        System.out.print("longitude: " + rs.getString("longitude"));
        System.out.print("depth " + rs.getString("depth"));
        System.out.print("mag"+rs.getString("mag"));
        System.out.print("magType"+rs.getString("magType"));
        System.out.print("nst"+rs.getString("nst"));
        System.out.print("gap"+rs.getString("gap"));
        System.out.print("dmin"+rs.getString("dmin"));
        System.out.print("rms"+rs.getString("rms"));
        System.out.print("mag"+rs.getString("net"));
        System.out.print("mag"+rs.getString("id"));
        System.out.print("mag"+rs.getString("updated"));
        System.out.print("mag"+rs.getString("place"));
        System.out.println("mag"+rs.getString("type"));
     }
     
	//end timer
     s.stop();	

    //printing the time taken to fetch data from RDS
     System.out.println("Time taken to fetch data from RDS"+s.getTotalTimeSeconds()+" secs");

    //closing the resources
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
          conn.close();
    }catch(SQLException se){
    }// do nothing
    try{
       if(conn!=null)
          conn.close();
    }catch(SQLException se){
       se.printStackTrace();
    }//end finally try
 }//end try
 }

 
 /*
  * The main method which calls the two functions to upload and download from RDS
  */
 
public static void main(String args[]) throws FileNotFoundException
{
	   //passing the csv file to load into RDS 
	   execute_insert("all_month.csv");
       
	   //the below function call is for Retrieving the data from RDS
	   execute_select();
}

}

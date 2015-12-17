load data LOCAL infile "C:/Windows/Temp/all_month.csv" 
into table all_month columns terminated by ',' 
optionally enclosed by "" 
escaped by "" 
lines terminated by '\n' 
ignore 1 lines;


CREATE TABLE all_month (
  time_date varchar(30) NOT NULL,
  latitude varchar(30) NOT NULL,
  longitude varchar(30) NOT NULL,
  depth varchar(30) NOT NULL,
  mag varchar(30) NOT NULL,
  magtype varchar(30) NOT NULL,
  nst varchar(30) NOT NULL,
  gap varchar(30) NOT NULL,
  dmin varchar(30) NOT NULL,
  rms varchar(30) NOT NULL,
  net varchar(30) NOT NULL,
  nid varchar(30) NOT NULL,
  updated varchar(30) NOT NULL,
  place varchar(100) NOT NULL,
  type varchar(30) NOT NULL
);


drop table all_month;


SELECT latitude,longitude,mag FROM all_month
ORDER BY RAND()
LIMIT 1



create view limited as (select * from consumer_complaints2 limit 200)
select * from limited
select Product,Issue,ZIP_code from consumer_complaints2 where ZIP_code like '%76%'
select product from consumer_complaints2
INSERT INTO consumer_complaints22(Complaint_ID,
                          Product ,
                          Subproduct,
                          Issue ,
                          Subissue ,
                          State ,
                          ZIP_code ,
                          Submitted_via ,
                          Date_received ,
                          Date_sent_to_company ,
                          Company ,
                          Company_response ,
                          Timely_response ,
                          Consumer_disputed) values (1426958,'Debt collection', 'NULL', "Cont'd attempts collect debt not owed", 'Debt was paid', 'OH',43026,'Web', 06/18/2015, 06/18/2015, 'Oracle Financial Group LLC.','Closed with monetary relief','Yes','NULL')
select * from Consumer_Complaints10
select zip_code from consumer_complaints2 where zip_code like '0%'
select max(complaint_id),min(complaint_id) from consumer_complaints2
select max(ZIP_code),min(ZIP_code) from consumer_complaints2

select harish_kamuju2 where FATALITY_AGE >= 40
desc 6339_dataset;
select age,count(age) from 6339_dataset where DIAGNOSIS_CODE_1 and DIAGNOSIS_CODE_2 
select * FROM 6339_dataset where DIAGNOSIS_CODE_1 is null and DIAGNOSIS_CODE_2 is null

select age,DIAGNOSIS_CODE_1,count(age) from 6339_dataset group by age,DIAGNOSIS_CODE_1 

select age,occurence from (select age,DIAGNOSIS_CODE_1,DIAGNOSIS_CODE_2,count(age) as occurence from 6339_dataset group by age,DIAGNOSIS_CODE_1,DIAGNOSIS_CODE_2 order by count(age) desc ) tmp 

select age,DIAGNOSIS_CODE_1,DIAGNOSIS_CODE_2,count(age) as occurence from 6339_dataset group by age,DIAGNOSIS_CODE_1,DIAGNOSIS_CODE_2 order by count(age) desc 


select t1.age,t1.DIAGNOSIS_CODE_1,t1.DIAGNOSIS_CODE_2 from 6339_dataset as t1,6339_dataset as t2 where t1.age=t2.age and t1.DIAGNOSIS_CODE_1=t2.DIAGNOSIS_CODE_1 and t1.DIAGNOSIS_CODE_2=t2.DIAGNOSIS_CODE_2 group by t1.age,t1.DIAGNOSIS_CODE_1,t1.DIAGNOSIS_CODE_2


 group by age,DIAGNOSIS_CODE_1 
 
 
 select age,DIAGNOSIS_CODE_1,DIAGNOSIS_CODE_2 from 6339_dataset where age = '9' and DIAGNOSIS_CODE_1=DIAGNOSIS_CODE_2
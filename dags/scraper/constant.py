insertQuery = """INSERT INTO job_data (
          job_title, 
          job_description,
          job_tags,
          job_tier,
          job_type,
          job_posted_on,
          job_budget_or_duration,
          scraped_on,
          job_domain,
          hash_key_value)
            VALUES (
              %(job)s,
              %(description)s,
              %(tag)s,
              %(tier)s,
              %(type)s,
              %(postedOn)s,
              %(budgetOrDuration)s,
              %(scrapedOn)s,
              %(domain)s,
              %(hashKey)s)"""

transformed_data_insert_query="""
insert into entries (scraped_on,search_key_id) 
    select date(jd.scraped_on),
    (select id from search_keys where search_key = jd.job_domain)
from job_data jd where date(scraped_on)= '{{ ds }}' and
not exists(select * from entries e where e.scraped_on=date(jd.scraped_on) and e.search_key_id = (select id from search_keys where search_key = jd.job_domain)) 
group by date(scraped_on),job_domain;

INSERT INTO transformed_job_data (untransformed_job_id, title, descriptions,tags, tier, posted_on, entry_id,hash_key_value)
with add_row_number as (
SELECT jd.job_id, jd.job_title, jd.job_description,jd.job_tags, jd.job_tier,
CASE 
		WHEN job_posted_on LIKE '%%sec%%' THEN
			date(date_sub(jd.scraped_on,interval REGEXP_REPLACE(job_posted_on, '[^0-9]+', '') SECOND))
        WHEN job_posted_on LIKE '%%min%%' OR job_posted_on LIKE '%%minute%%' THEN
			date(date_sub(jd.scraped_on,interval REGEXP_REPLACE(job_posted_on, '[^0-9]+', '') MINUTE))
		WHEN job_posted_on LIKE '%%hr%%' OR job_posted_on LIKE '%%hour%%' THEN
            date(date_sub(jd.scraped_on,interval REGEXP_REPLACE(job_posted_on, '[^0-9]+', '') HOUR))
		WHEN job_posted_on LIKE '%%day%%' THEN
			date(date_sub(jd.scraped_on,interval REGEXP_REPLACE(job_posted_on, '[^0-9]+', '') DAY))
		WHEN job_posted_on LIKE '%%week%%' THEN
            date(date_sub(jd.scraped_on,interval REGEXP_REPLACE(job_posted_on, '[^0-9]+', '') WEEK))
		WHEN job_posted_on LIKE '%%month%%' THEN
			date(date_sub(jd.scraped_on,interval REGEXP_REPLACE(job_posted_on, '[^0-9]+', '') MONTH))
        ELSE NULL
    END AS posted_on, 
    e.id AS entry_id,
    hash_key_value,
    row_number() over (partition by jd.hash_key_value order by jd.job_id) row_num
FROM job_data jd 
JOIN entries e ON DATE(jd.scraped_on) = DATE(e.scraped_on) and jd.job_domain = (SELECT search_key FROM search_keys WHERE id = e.search_key_id)
where date(jd.scraped_on) =  '{{ ds }}' and  not exists(select * from transformed_job_data td where jd.hash_key_value=td.hash_key_value) 
)select 
job_id,job_title,job_description,job_tags,job_tier,posted_on,entry_id,hash_key_value
 from add_row_number where row_num=1 order by job_id;

insert into hourly (transformed_job_id,minimum_pay,maximum_pay,minimum_duration,maximum_duration,hours_per_week_id)
select td.id,
cast(REGEXP_SUBSTR(substring_index(job_type,'-',1), '[0-9]+')as unsigned integer)as minimum_pay,
    case
		when job_type like '%$%' and job_type like '%-%' then 
			convert(REGEXP_SUBSTR(substring(job_type,locate('-',job_type)), '[0-9]+'),unsigned int)
		when job_type like '%$%' and job_type not like '%-%' then 
			cast(REGEXP_SUBSTR(job_type,'[0-9]+')as unsigned int)
		else null
	end as maximum_pay,
	case
		when job_budget_or_duration like 'more%' then  
			cast(REGEXP_SUBSTR(substring_index(job_budget_or_duration,',',1), '[0-9]+')as unsigned int)
		when job_budget_or_duration like '%to%' then 
			cast(REGEXP_SUBSTR(substring_index(job_budget_or_duration,'to',1), '[0-9]+')as unsigned int)
		else null
	end as minimum_duration,
	case
		when job_budget_or_duration like 'less%' then
			cast(REGEXP_SUBSTR(substring_index(job_budget_or_duration,',',1), '[0-9]+')as unsigned int)
		when job_budget_or_duration like '%to%' then
			cast(REGEXP_SUBSTR(substring(job_budget_or_duration,locate('to',job_budget_or_duration)), '[0-9]+')as unsigned int)
		else null
	end as maximum_duration,
    (SELECT id 
	FROM hours_per_week hp
	WHERE hp.hours = (
		CASE
			WHEN job_budget_or_duration LIKE '%hrs/week' AND job_budget_or_duration LIKE '%, less than%' THEN 
				CONCAT('less than ', REGEXP_substr(SUBSTRING(job_budget_or_duration, LOCATE(',', job_budget_or_duration)), '[0-9]+'))
			WHEN job_budget_or_duration LIKE '%+ hrs/week' THEN
				CONCAT('more than ', REGEXP_substr(SUBSTRING(job_budget_or_duration, LOCATE(',', job_budget_or_duration)), '[0-9]+'))
			ELSE 'not specified'
		END))as 'hrs/week'
from job_data jd
join transformed_job_data td on jd.job_id=td.untransformed_job_id 
where date(jd.scraped_on) = '{{ ds }}' and job_type like "hourly%" and
not exists(select * from hourly h where h.transformed_job_id=td.id);

INSERT INTO fixed_price (transformed_job_id, budget)
SELECT
    td.id,
    CASE 
		WHEN job_budget_or_duration REGEXP '^\\$.*k$' THEN -- $2k 
			CAST(REPLACE(REPLACE(lower(job_budget_or_duration), 'k', ''), '$', '') * 1000 AS UNSIGNED INT)
        WHEN job_budget_or_duration REGEXP '^\\$.*m$' THEN -- $1m 
            CAST(REPLACE(REPLACE(lower(job_budget_or_duration), 'm', ''), '$', '') * 1000000 AS UNSIGNED INT)
        WHEN job_budget_or_duration LIKE '%,%' THEN -- $2,000 
            CAST(REPLACE(REPLACE(job_budget_or_duration, ',', ''), '$', '') AS UNSIGNED INT)
        WHEN job_budget_or_duration LIKE '$%' THEN
            CAST(REGEXP_SUBSTR(job_budget_or_duration, '[0-9]+') AS unSIGNED INT)
        ELSE
            null
    END AS budget
FROM job_data AS jd
JOIN transformed_job_data AS td ON jd.job_id = td.untransformed_job_id	
WHERE date(jd.scraped_on) = '{{ ds }}' and job_type LIKE "fixed-price%" and
not exists(select * from fixed_price fp where fp.transformed_job_id=td.id); 

"""

url_list = [
    ['https://www.upwork.com/nx/jobs/search/?sort=recency&ontology_skill_uid=1031626760125923328','mobile app development'],
    ['https://www.upwork.com/nx/jobs/search/?sort=recency&ontology_skill_uid=1031626795211276288','web development'],
    ['https://www.upwork.com/nx/jobs/search/?sort=recency&ontology_skill_uid=1031626720351338496','blockchain'],
    ['https://www.upwork.com/nx/jobs/search/?q=data%20engineer&sort=recency','data engineer']
]
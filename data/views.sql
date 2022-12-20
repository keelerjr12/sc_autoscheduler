DROP VIEW vw_pilots_quals;

CREATE OR REPLACE VIEW vw_pilots_quals AS
SELECT  p.id, 
        p.last_name,
        p.first_name,
        auth_group.name as auth_group_name,
        orgs.name as assigned_org,
        pq_denorm.operations_supervisor,
        pq_denorm.sof,
        pq_denorm.rsu_controller,
        pq_denorm.rsu_observer,
        pq_denorm.pit_ip
FROM    (SELECT pq.pilot_id, 
                max(CASE WHEN name = 'Operations Supervisor' then 1 END) AS operations_supervisor,
                max(CASE WHEN name = 'SOF' then 1 END) AS sof,
                max(CASE WHEN name = 'RSU Controller' then 1 END) AS rsu_controller,
                max(CASE WHEN name = 'RSU Observer' then 1 END) AS rsu_observer,
                max(CASE WHEN name = 'PIT IP' then 1 END) AS pit_ip
        FROM    pilots_quals pq
        JOIN    quals q
        ON      pq.qual_id = q.id
        GROUP BY pq.pilot_id) AS pq_denorm
RIGHT JOIN pilots p
ON p.id = pq_denorm.pilot_id
JOIN auth_group
ON  auth_group.id = p.auth_group_id
LEFT JOIN pilots_orgs po
ON po.pilot_id = p.id
LEFT JOIN orgs
ON orgs.id = po.org_id
ORDER BY p.last_name, p.first_name;

SELECT * FROM vw_pilots_quals;
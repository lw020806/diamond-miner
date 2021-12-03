-- We send 1 probe per flow
-- Prefix 200.0.0.0/24 is OK (2 nodes and 1 link discovered)
-- Prefix 201.0.0.0/24 has a routing loop (same node at two different TTLs)
-- Prefix 202.0.0.0/24 is sending multiple replies per probe (3 replies)
INSERT INTO probes__test_invalid_prefixes
VALUES (1, '::ffff:200.0.0.0', 1, 1, 1),
       (1, '::ffff:200.0.0.0', 2, 1, 1),
       (1, '::ffff:201.0.0.0', 1, 1, 1),
       (1, '::ffff:201.0.0.0', 2, 1, 1),
       (1, '::ffff:201.0.0.0', 3, 1, 1),
       (1, '::ffff:202.0.0.0', 1, 4, 1);

INSERT INTO results__test_invalid_prefixes
VALUES (0, 1, '::ffff:100.0.0.1', '::ffff:200.0.0.0', 24000, 33434, 1, 1, '::ffff:150.0.0.1', 1, 11, 0, 250, 0, [], 0.0, 1),
       (0, 1, '::ffff:100.0.0.1', '::ffff:200.0.0.0', 24000, 33434, 2, 1, '::ffff:150.0.0.2', 1, 11, 0, 250, 0, [], 0.0, 1),
       (0, 1, '::ffff:100.0.0.1', '::ffff:201.0.0.0', 24000, 33434, 1, 1, '::ffff:150.0.1.1', 1, 11, 0, 250, 0, [], 0.0, 1),
       (0, 1, '::ffff:100.0.0.1', '::ffff:201.0.0.0', 24000, 33434, 2, 1, '::ffff:150.0.1.2', 1, 11, 0, 250, 0, [], 0.0, 1),
       (0, 1, '::ffff:100.0.0.1', '::ffff:201.0.0.0', 24000, 33434, 3, 1, '::ffff:150.0.1.2', 1, 11, 0, 250, 0, [], 0.0, 1),
       (0, 1, '::ffff:100.0.0.1', '::ffff:202.0.0.0', 24000, 33434, 1, 1, '::ffff:150.0.2.1', 1, 11, 0, 250, 0, [], 0.0, 1),
       (0, 1, '::ffff:100.0.0.1', '::ffff:202.0.0.0', 24000, 33434, 1, 1, '::ffff:150.0.2.2', 1, 11, 0, 250, 0, [], 0.0, 1),
       (0, 1, '::ffff:100.0.0.1', '::ffff:202.0.0.0', 24000, 33434, 1, 1, '::ffff:150.0.2.3', 1, 11, 0, 250, 0, [], 0.0, 1),
       (0, 1, '::ffff:100.0.0.1', '::', 24000, 33434, 1, 1, '::ffff:150.0.2.3', 1, 11, 0, 250, 0, [], 0.0, 1);

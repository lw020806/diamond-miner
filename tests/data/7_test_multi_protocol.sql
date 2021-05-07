-- At TTL 1, we discover 1 node with UDP, 2 with ICMP
-- At TTL 2, we discover 1 node for both protocols

INSERT INTO test_multi_protocol
VALUES ('::ffff:100.0.0.1', '::ffff:200.0.0.1', 24000, 33434, 1, 1, 17, '::ffff:150.0.0.1', 1, 11, 0, 250, 0, [], 0.0, 1),
       ('::ffff:100.0.0.1', '::ffff:200.0.0.2', 24000, 33434, 1, 1, 17, '::ffff:150.0.0.1', 1, 11, 0, 250, 0, [], 0.0, 1),
       ('::ffff:100.0.0.1', '::ffff:200.0.0.1', 24000, 33434, 1, 1, 1, '::ffff:150.0.0.1', 1, 11, 0, 250, 0, [], 0.0, 1),
       ('::ffff:100.0.0.1', '::ffff:200.0.0.2', 24000, 33434, 1, 1, 1, '::ffff:150.0.0.2', 1, 11, 0, 250, 0, [], 0.0, 1)
       ('::ffff:100.0.0.1', '::ffff:200.0.0.1', 24000, 33434, 2, 2, 17, '::ffff:150.0.1.1', 1, 11, 0, 250, 0, [], 0.0, 1)
       ('::ffff:100.0.0.1', '::ffff:200.0.0.2', 24000, 33434, 2, 2, 17, '::ffff:150.0.1.1', 1, 11, 0, 250, 0, [], 0.0, 1)
       ('::ffff:100.0.0.1', '::ffff:200.0.0.1', 24000, 33434, 2, 2, 1, '::ffff:150.0.1.1', 1, 11, 0, 250, 0, [], 0.0, 1)
       ('::ffff:100.0.0.1', '::ffff:200.0.0.2', 24000, 33434, 2, 2, 1, '::ffff:150.0.1.1', 1, 11, 0, 250, 0, [], 0.0, 1);

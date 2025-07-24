Create a cluster
```shell
sudo kind create cluster --config kind-config.yaml
```
# global-cluster

```cassandraql
CREATE KEYSPACE IF NOT EXISTS slot_game
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS slot_game.spin_history (
    username text,
    spin_id uuid,
    timestamp timestamp,
    bet_amount double,
    win_amount double,
    result text,
    PRIMARY KEY (username, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

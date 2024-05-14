create user ${DB_REPL_USER} with replication encrypted password ${DB_REPL_PASSWORD};
select pg_create_physical_replication_slot('replication_slot');

-- Runs only when the postgres volume is created. For an existing volume, create new
-- databases by hand: docker-compose exec postgres createdb -U prepza <name>
CREATE DATABASE library;
CREATE DATABASE generation;
CREATE DATABASE rounds;
CREATE DATABASE companies;
CREATE DATABASE billing;
CREATE DATABASE notifications;
CREATE DATABASE ats;
CREATE DATABASE api;
CREATE DATABASE assistant;

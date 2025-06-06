-- Database: <TEST_DB_NAME>

-- DROP DATABASE IF EXISTS <TEST_DB_NAME>;

CREATE DATABASE <TEST_DB_NAME>
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = '<LC_COLLATE>'
    LC_CTYPE = '<LC_CTYPE>'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres REVOKE ALL ON TABLES FROM postgres;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres REVOKE ALL ON SEQUENCES FROM postgres;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres
GRANT SELECT, USAGE ON SEQUENCES TO PUBLIC;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres REVOKE USAGE ON TYPES FROM PUBLIC;

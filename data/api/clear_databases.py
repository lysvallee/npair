import os
import logging
from sqlalchemy import create_engine, text
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="/app/logs/clear_databases.log",
)

logger = logging.getLogger(__name__)

# PostgreSQL connection details
NPAIR_DB_URL = os.environ.get("NPAIR_DB_URL")

# Cassandra connection details
CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST")
CASSANDRA_PORT = int(os.environ.get("CASSANDRA_PORT"))
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE")


def clear_postgresql_db():
    engine = create_engine(NPAIR_DB_URL)
    try:
        with engine.connect() as connection:
            # Disable foreign key checks
            connection.execute(text("SET CONSTRAINTS ALL DEFERRED"))

            # Get all table names
            result = connection.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            )
            tables = [row[0] for row in result]

            # Truncate all tables
            for table in tables:
                connection.execute(text(f"TRUNCATE TABLE {table} CASCADE"))

            # Re-enable foreign key checks
            connection.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))

        logger.info(f"Cleared all data from postgreSQL database")
    except Exception as e:
        logger.error(f"Error clearing postgreSQL database: {str(e)}")


def clear_cassandra_db():
    if not all([CASSANDRA_HOST, CASSANDRA_PORT, CASSANDRA_KEYSPACE]):
        logger.error("Cassandra connection details are not fully set")
        return

    try:
        auth_provider = PlainTextAuthProvider(
            username="cassandra", password="cassandra"
        )
        cluster = Cluster(
            [CASSANDRA_HOST], port=CASSANDRA_PORT, auth_provider=auth_provider
        )
        session = cluster.connect()

        # Get all table names in the keyspace
        query = f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = '{CASSANDRA_KEYSPACE}'"
        rows = session.execute(query)

        # Truncate all tables
        for row in rows:
            table_name = row.table_name
            session.execute(f"TRUNCATE TABLE {CASSANDRA_KEYSPACE}.{table_name}")

        cluster.shutdown()
        logger.info(f"Cleared all data from Cassandra keyspace: {CASSANDRA_KEYSPACE}")
    except Exception as e:
        logger.error(f"Error clearing Cassandra database: {str(e)}")


if __name__ == "__main__":
    clear_postgresql_db()
    clear_cassandra_db()
    logger.info("All databases have been cleared.")

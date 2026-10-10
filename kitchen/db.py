# kitchen/db.py -- the only way scripts talk to Neo4j
import os
from pathlib import Path
from neo4j import GraphDatabase

def _load_env():
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        raise SystemExit("kitchen/.env is missing; see BIBLE part 2 section 6.3")
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

_load_env()
_driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
)

def run(cypher, **params):
    """Run one Cypher statement; return a list of dict rows."""
    db = os.environ.get("NEO4J_DATABASE", "neo4j")
    with _driver.session(database=db) as session:
        return [record.data() for record in session.run(cypher, **params)]

def env(key, default=None):
    return os.environ.get(key, default)

if __name__ == "__main__":
    print(run("RETURN 1 AS ok"))

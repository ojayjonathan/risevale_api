from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

# TEST_DB_URL = "sqlite:///:memory:"
# TEST_DB_URL = "postgresql://koo_movers:koo_movers#124@localhost:5432/koo_movers"
TEST_DB_URL = "sqlite:///test.db"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=True,
)

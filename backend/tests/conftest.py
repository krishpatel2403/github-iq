import os
import tempfile

import pytest
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.remove(path)
    except PermissionError:
        pass  # file may still be held on Windows; harmless after session ends


@pytest.fixture(scope="function")
def db_session(db_path):
    test_engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(bind=test_engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    test_engine.dispose()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()

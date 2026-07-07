import os, json
import pytest
from dotenv import load_dotenv
from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from db import models
from api.main import app
from bin.seed_countries_regions import generate_country_objects, generate_origin_objects

from bin.seed.seed_roasters import sample_roaster_objects
from bin.seed.seed_green_coffees import sample_green_coffee_objects
from bin.seed.seed_roasted_coffees import sample_roasted_coffee_objects

SAMPLE_DATA_PATH = "assets/sample-data.json"

# Set up environment
os.environ["APP_ENV"] = "testing"

if os.path.exists(".env.testing"):
    load_dotenv(".env.testing")
elif os.path.exists(".env"):
    load_dotenv(".env")


@pytest.fixture
def engine(request):
    use_sample_data = request.node.get_closest_marker("use_sample_data")
    echo_marker = request.node.get_closest_marker("echo")

    def seed_sample_data(engine):
        with Session(engine) as session:
            session.add_all(sample_roaster_objects())
            session.add_all(sample_green_coffee_objects(engine))
            session.commit()

            session.add_all(sample_roasted_coffee_objects(engine))
            session.commit()

    echo = echo_marker and (echo_marker.args[0] is True)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=echo,
    )
    models.Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Seed country and origin tables
        session.add_all(generate_country_objects())
        session.add_all(generate_origin_objects())
        session.commit()

    if use_sample_data and (use_sample_data.args[0] is True):
        seed_sample_data(engine)

    yield engine

    models.Base.metadata.drop_all(engine)


@pytest.fixture
def client(engine):
    return TestClient(app(engine))

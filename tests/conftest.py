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
from bin.seed_sample_data import green_coffee_objects, roaster_object_and_associations

SAMPLE_DATA_PATH = "assets/sample-data.json"

# Set up environment
os.environ["APP_ENV"] = "testing"

if os.path.exists(".env.testing"):
    load_dotenv(".env.testing")
elif os.path.exists(".env"):
    load_dotenv(".env")


@pytest.fixture(scope="module")
def engine(request):
    use_sample_data = request.node.get_closest_marker("use_sample_data")
    echo_marker = request.node.get_closest_marker("echo")

    def seed_sample_data(engine):
        with open(SAMPLE_DATA_PATH) as file:
            data = json.load(file)

        # Seed sample data
        with Session(engine) as session:
            if green_coffee_data := data.get("green_coffees"):
                session.add_all(green_coffee_objects(engine, green_coffee_data))
                session.commit()

        for roaster_data in data.get("roasters"):
            with Session(engine) as session:
                r = roaster_object_and_associations(engine, roaster_data)

                roaster_object = r.get("roaster")
                session.add(roaster_object)

                coffee_objects = r.get("coffees", [])
                session.add_all(coffee_objects)

                component_objects = r.get("component_associations", [])
                session.add_all(component_objects)
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


@pytest.fixture(scope="module")
def client(engine):
    return TestClient(app(engine))

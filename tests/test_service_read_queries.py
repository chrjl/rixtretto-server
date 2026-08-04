import pytest

from sqlalchemy.orm import Session
from src.db import queries


@pytest.mark.use_sample_data(True)
class TestService:
    def test_engine(self, engine):
        with Session(engine) as session:
            result = session.scalars(queries.Service().select()).all()

        assert len(result) == 2

    @pytest.mark.parametrize(
        "location_filter, expected_count",
        [({"city": "Los"}, 2), ({"city": "Culver"}, 1)],
    )
    def test_filter_service(self, engine, location_filter, expected_count):
        query = queries.Service()

        with Session(engine) as session:
            result = session.scalars(
                query.filter_by_location(location_filter).select()
            ).all()

        assert len(result) == expected_count

    @pytest.mark.parametrize(
        "name, location_filter, expected_count",
        [
            ("Go Get Em Tiger", {"city": "Los"}, 6),
            ("Go Get Em Tiger", {"city": "Culver"}, 2),
            ("Go Get Em Tiger", {"city": "Venice"}, 0),
        ],
    )
    def test_filter_service_locations(
        self, engine, name, location_filter, expected_count
    ):
        query = queries.Service().filter_by_name({"starts_with": name})

        with Session(engine) as session:
            result = session.scalars(query.location_associations(location_filter)).all()

        assert len(result) == expected_count

    @pytest.mark.parametrize(
        "name, expected_count",
        [("go get em tiger", 8), ("cafe saratoga", 1)],
    )
    def test_location(self, engine, name, expected_count):
        query = queries.Service().filter_by_name({"starts_with": name}).get("locations")

        with Session(engine) as session:
            result = session.scalars(query).all()

        assert len(result) == expected_count


@pytest.mark.use_sample_data(True)
class TestMenuItem:
    def test_menu_item(self, engine):
        query = queries.MenuItem()

        with Session(engine) as session:
            result = session.scalars(query.select()).all()

        assert len(result) == 13

    def test_filters(self, engine):
        name_filter_query = (
            queries.MenuItem().filter_by_name({"starts_with": "l"}).select()
        )

        with Session(engine) as session:
            name_filter_result = session.scalars(name_filter_query).all()

            assert len(name_filter_result) == 3
            assert "lachepas" in [
                menu_item.normalized_name for menu_item in name_filter_result
            ]
            assert "lilsweetie" in [
                menu_item.normalized_name for menu_item in name_filter_result
            ]

        service_filter_query = (
            queries.MenuItem()
            .filter_by_service(
                queries.Service()
                .filter_by_name({"starts_with": "gogetem"})
                .select(["id"])
            )
            .select()
        )

        with Session(engine) as session:
            service_filter_result = session.scalars(service_filter_query).all()
            assert len(service_filter_result) == 4

            for menu_item in service_filter_result:
                assert menu_item.service.name == "Go Get Em Tiger"

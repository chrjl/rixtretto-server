import pytest

from sqlalchemy import select
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

    @pytest.mark.parametrize(
        "service_name, menu_item_name, ingredients",
        [
            ("Cafe Saratoga", "Americano", ["espresso", "water"]),
            (
                "Go Get Em Tiger",
                "Tumi",
                ["turmeric", "ginger", "honey", "blackpepper", "almondmacadamiamilk"],
            ),
            (
                "Go Get Em Tiger",
                "Lil Sweetie",
                ["espresso", "milk", "vanilla", "coldfoam"],
            ),
        ],
    )
    def test_relationship_ingredients(
        self, engine, service_name, menu_item_name, ingredients
    ):
        service_id_subq = (
            queries.Service()
            .filter_by_name({"starts_with": service_name})
            .select(["id"])
            .subquery()
        )

        query = (
            queries.MenuItem()
            .filter_by_service(select(service_id_subq))
            .filter_by_name({"starts_with": menu_item_name})
            .select()
        )

        with Session(engine) as session:
            result = [
                ingredient.normalized_name
                for ingredient in session.scalars(query).one().ingredients
            ]
            assert set(result) == set(ingredients)


@pytest.mark.use_sample_data(True)
class TestIngredient:
    def test_select_all(self, engine):
        with Session(engine) as session:
            result = session.scalars(queries.Ingredient().select()).all()
            assert len(result) == 32

    @pytest.mark.parametrize(
        "name_filter,expected_count",
        [
            ({"starts_with": "cold"}, 2),
            ({"contains": "milk"}, 2),
        ],
    )
    def test_filter_by_name(self, engine, name_filter, expected_count):
        with Session(engine) as session:
            query = queries.Ingredient().filter_by_name(name_filter).select()
            result = session.scalars(query).all()

            assert len(result) == expected_count

    @pytest.mark.parametrize(
        "parent_name, children_names",
        [
            ("coffee", ["espresso", "cold brew"]),
            ("espresso", ["single-origin espresso"]),
        ],
    )
    def test_parent_child_relationships(self, engine, parent_name, children_names):
        with Session(engine) as session:
            parent = session.scalar(
                queries.Ingredient()
                .filter_by_name({"starts_with": parent_name})
                .select()
            )

            assert parent
            assert set([child.name for child in parent.children]) == set(children_names)

            for child_name in children_names:
                child = session.scalar(
                    queries.Ingredient()
                    .filter_by_name({"starts_with": child_name})
                    .select()
                )

                assert child
                assert child.parent
                assert child.parent.name == parent_name

    @pytest.mark.parametrize(
        "ingredient_name, descendants",
        [
            ("coffee", ["espresso", "cold brew", "single-origin espresso"]),
            ("milk", []),
        ],
    )
    def test_descendants(self, engine, ingredient_name, descendants):
        query = (
            queries.Ingredient()
            .filter_by_name({"starts_with": ingredient_name})
            .get("descendants")
        )

        with Session(engine) as session:
            result = session.scalars(query).all()
            assert set([ingredient.name for ingredient in result]) == set(descendants)

    @pytest.mark.parametrize(
        "ingredient_name, ancestors",
        [
            ("single-origin espresso", ["espresso", "coffee"]),
            ("milk", []),
        ],
    )
    def test_ancestors(self, engine, ingredient_name, ancestors):
        query = (
            queries.Ingredient()
            .filter_by_name({"starts_with": ingredient_name})
            .get("ancestors")
        )

        with Session(engine) as session:
            result = session.scalars(query).all()
            assert set([ingredient.name for ingredient in result]) == set(ancestors)

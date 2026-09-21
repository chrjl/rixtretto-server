import json
import pytest

from db.utilities import normalized_text


@pytest.mark.use_sample_data(True)
class TestService:
    def test_get_all(self, client):
        query = """
            query {
                coffeeService {
                    name
                }
            }
        """

        response = client.post("/", json={"query": query})
        result = response.json()["data"]["coffeeService"]

        assert len(result) == 2

    @pytest.mark.parametrize("ids", [[1], [2]])
    def test_filter_by_ids(self, client, ids):
        query = """
            query($ids: [ID]) {
                coffeeService(ids: $ids) {
                    name
                }
            }
        """

        variables = {"ids": ids}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["coffeeService"]

        assert len(result) == len(ids)

    @pytest.mark.parametrize(
        "name,location_filter,expected_count",
        [
            ("Go Get Em Tiger", None, 8),
            ("Go Get Em Tiger", {}, 8),
            ("Go Get Em Tiger", {"neighborhood": "Valley"}, 0),
            ("Go Get Em Tiger", {"city": "Los"}, 6),
            ("Go Get Em Tiger", {"neighborhood": "Downtown"}, 2),
            ("Go Get Em Tiger", {"address": "Larchmont"}, 1),
        ],
    )
    def test_filter_by_location(self, client, name, location_filter, expected_count):
        query = """
            query($filter: Filter) {
                coffeeService(filter: $filter) {
                    name
                    locations {
                        name
                        description
                        location {
                            address
                            neighborhood
                            city
                            state
                            country {
                                name
                            }
                        }
                    }
                }
            }
        """

        variables = {
            "filter": {
                "name": {"starts_with": name},
                "location": location_filter,
            }
        }

        response = client.post("/", json={"query": query, "variables": variables})

        if result := response.json()["data"]["coffeeService"]:
            assert len(result[0]["locations"]) == expected_count
        else:
            assert expected_count == 0

        # print(json.dumps(result, indent=2))


@pytest.mark.use_sample_data(True)
class TestServiceRelationships:
    @pytest.mark.parametrize(
        "name_filter, expected_count",
        [
            ({"starts_with": "C"}, 1),
            ({"contains": "e"}, 2),
        ],
    )
    def test_roaster(self, client, name_filter, expected_count):
        query = """
            query($filter: Filter) {
                coffeeService(filter: $filter) {
                    id
                    name
                    roaster {
                        name
                    }
                }
            }
        """

        variables = {"filter": {"name": name_filter}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["coffeeService"]

        assert len(result) == expected_count

    @pytest.mark.parametrize(
        "name,coffee_names",
        [
            (
                "Go Get Em Tiger",
                ["Placer de la Tarde", "Minor Monuments", "Humbuggle: A Holiday Blend"],
            ),
        ],
    )
    def test_coffees(self, client, name, coffee_names):
        query = """
            query($filter: Filter) {
                coffeeService(filter: $filter) {
                    name
                    coffees {
                        name
                    }
                }
            }
        """

        variables = {"name": {"starts_with": name}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["coffeeService"][0]["coffees"]

        assert set([normalized_text(coffee["name"]) for coffee in result]) == set(
            [normalized_text(name) for name in coffee_names]
        )

    @pytest.mark.parametrize(
        "roasted_coffee_name, service_names",
        [
            ("Minor Monuments", ["Go Get Em Tiger"]),
            ("Tariku Kare", []),
        ],
    )
    def test_roasted_coffees_reverse(self, client, roasted_coffee_name, service_names):
        query = """
            query($filter: Filter) {
                roastedCoffees(filter: $filter) {
                    id
                    name
                    service {
                        name
                    }
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": roasted_coffee_name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["roastedCoffees"][0]

        assert [coffee["name"] for coffee in result["service"]] == service_names

    @pytest.mark.parametrize(
        "service_name,origin_names",
        [
            (
                "Go Get Em Tiger",
                ["Honduras", "Guatemala", "Colombia", "Kenya", "Huila"],
            ),
        ],
    )
    def test_origins(self, client, service_name, origin_names):
        query = """
            query($filter: Filter) {
                coffeeService(filter: $filter) {
                    name
                    coffees {
                        id
                        name
                    }
                    origins {
                        id
                        name
                    }
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": service_name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["coffeeService"][0]["origins"]

        assert set([normalized_text(origin["name"]) for origin in result]) == set(
            [normalized_text(name) for name in origin_names]
        )

    @pytest.mark.parametrize(
        "origin_name, service_names",
        [
            ("Colombia", ["Go Get Em Tiger"]),
            ("Papua New Guinea", ["Cafe Saratoga"]),
        ],
    )
    def test_origin_reverse(self, client, origin_name, service_names):
        query = """
            query($filter: Filter) {
                origins(filter: $filter) {
                    name
                    service {
                        name
                    }
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": origin_name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = [
            service["name"]
            for service in response.json()["data"]["origins"][0]["service"]
        ]

        assert set(result) == set(service_names)

    @pytest.mark.parametrize(
        "service_name, expected_processes",
        [
            ("Go Get Em Tiger", ["decaf", "sugarcane"]),
            ("Cafe Saratoga", ["natural", "washed"]),
        ],
    )
    def test_processes(self, client, service_name, expected_processes):
        query = """
            query($filter: Filter) {
                coffeeService(filter: $filter) {
                    name
                    processes
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": service_name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["coffeeService"][0]["processes"]

        assert set(result) == set(expected_processes)

    @pytest.mark.parametrize(
        "processes, service_names",
        [
            (["decaf"], ["Go Get Em Tiger"]),
            (["decaf", "sugarcane"], ["Go Get Em Tiger"]),
            (["decaf", "washed"], ["Go Get Em Tiger", "Cafe Saratoga"]),
            (["404"], []),
        ],
    )
    def test_process_reverse(self, client, processes, service_names):
        query = """
            query($filter: Filter) {
                roastedCoffees(filter: $filter) {
                    name
                    service {
                        name
                    }
                }
            }
        """

        variables = {"filter": {"processes": processes}}
        response = client.post("/", json={"query": query, "variables": variables})

        result = [
            service["name"]
            for coffee in response.json()["data"]["roastedCoffees"]
            for service in coffee["service"]
        ]

        assert set(result) == set(service_names)

    @pytest.mark.parametrize(
        "service_name, expected_varieties",
        [
            ("Go Get Em Tiger", []),
            ("Cafe Saratoga", ["Gesha", "Arusha", "Bourbon", "Typica"]),
        ],
    )
    def test_varieties(self, client, service_name, expected_varieties):
        query = """
            query($filter: Filter) {
                coffeeService(filter: $filter) {
                    name
                    varieties
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": service_name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["coffeeService"][0]["varieties"]

        assert set(result) == set(expected_varieties)

    @pytest.mark.parametrize(
        "varieties, service_names",
        [
            (["gesha"], ["Cafe Saratoga"]),
            (["gesha", "typica"], ["Cafe Saratoga"]),
            (["gesha", "sl28"], ["Cafe Saratoga"]),
        ],
    )
    def test_varieties_reverse(self, client, varieties, service_names):
        query = """
            query($filter: Filter) {
                roastedCoffees(filter: $filter) {
                    name
                    service {
                        name
                    }
                }
            }
        """

        variables = {"filter": {"varieties": varieties}}
        response = client.post("/", json={"query": query, "variables": variables})

        result = [
            service["name"]
            for coffee in response.json()["data"]["roastedCoffees"]
            for service in coffee["service"]
        ]

        assert set(result) == set(service_names)

    @pytest.mark.parametrize(
        "name, expected_count", [("go get em tiger", 8), ("cafe saratoga", 1)]
    )
    def test_location(self, client, name, expected_count):
        query = """
            query($filter: Filter) {
                coffeeService(filter: $filter) {
                    locations {
                        name
                        description
                        dateOpened
                        dateClosed
                        location {
                            name
                            address
                            address_detail
                            city
                            state
                            country {
                                id
                                name
                            }
                        }
                    }
                }
            }
        """

        variables = {"filter": {"name": {"contains": name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["coffeeService"][0]["locations"]

        # print(json.dumps(result, indent=2))
        assert len(result) == expected_count

    @pytest.mark.parametrize(
        "service_name, expected_count",
        [("Cafe Saratoga", 9), ("Go Get Em Tiger", 4)],
    )
    def test_menu(self, client, service_name, expected_count):
        query = """
            query($filter: Filter) {
                coffeeService(filter: $filter) {
                    id
                    name
                    menu {
                        name
                        variants
                    }
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": service_name}}}

        response = client.post("/", json={"query": query, "variables": variables})

        result = response.json()["data"]["coffeeService"][0]

        # print(json.dumps(result, indent=2))
        assert len(result["menu"]) == expected_count


@pytest.mark.use_sample_data(True)
class TestMenuItem:
    def test_all(self, client):
        query = """
            query {
                menuItems {
                    name
                    
                    service {
                        name
                    }

                    variants
                    dateAdded
                    dateRemoved
                    details
                }
            }
        """

        response = client.post("/", json={"query": query})
        result = response.json()["data"]["menuItems"]

        # print(json.dumps(result, indent=2))
        assert len(result) == 13

    @pytest.mark.parametrize(
        "name_filter, expected_result",
        [
            (
                {"contains": "latte"},
                ["Almond Macadamia Latte", "Iced Honey Matcha Latte", "Latte"],
            ),
            ({"starts_with": "lache"}, ["Lâche Pas"]),
            ({"starts_with": "t"}, ["Tumi", "The Janet", "The Renee"]),
        ],
    )
    def test_filter_by_name(self, client, name_filter, expected_result):
        query = """
            query($filter: Filter) {
                menuItems(filter: $filter) {
                    name
                    service {
                        id
                        name
                    }
                }
            }
        """

        variables = {"filter": {"name": name_filter}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["menuItems"]

        # print(json.dumps(result, indent=2))
        assert set([item["name"] for item in result]) == set(expected_result)

    @pytest.mark.parametrize(
        "service_name, menu_item_name, ingredient_names",
        [
            (
                "Go Get Em Tiger",
                "Almond Macadamia Latte",
                ["espresso", "almond macadamia milk"],
            ),
            (
                "Cafe Saratoga",
                "Jazzmin",
                ["espresso", "jasmine tea syrup", "orange blossom water", "soda"],
            ),
        ],
    )
    def test_recipe(self, client, service_name, menu_item_name, ingredient_names):
        query = """
            query($filter: Filter) {
                coffeeService(filter: $filter) {
                    name
                    menu {
                        name
                        recipe {
                            name
                        }
                    }
                }
            }
        """

        variables = {
            "filter": {
                "name": {"starts_with": service_name},
                "menu": {"starts_with": menu_item_name},
            }
        }

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["coffeeService"][0]["menu"][0]["recipe"]

        assert set([ingredient["name"] for ingredient in result]) == set(
            ingredient_names
        )


@pytest.mark.use_sample_data(True)
class TestIngredient:
    @pytest.mark.parametrize("count", (32,))
    def test_all(self, client, count):
        query = """
            query {
                ingredients {
                    name
                }
            }
        """

        response = client.post("/", json={"query": query})
        result = response.json()["data"]["ingredients"]

        assert len(result) == count

    @pytest.mark.parametrize(
        "search, name",
        [("steen", "Steen's syrup"), ("single o", "single-origin espresso")],
    )
    def test_filter_by_name(self, client, search, name):
        query = """
            query($filter: Filter) {
                ingredients(filter: $filter) {
                    name
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": search}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["ingredients"][0]

        assert result["name"] == name

    @pytest.mark.parametrize(
        "name, parent_name",
        [
            ("single-origin espresso", "espresso"),
            ("espresso", "coffee"),
        ],
    )
    def test_relationship_parent(self, client, name, parent_name):
        query = """
            query($filter: Filter) {
                ingredients(filter: $filter) {
                    name
                    parent {
                        name
                    }
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["ingredients"][0]

        assert result["name"] == name
        assert result["parent"]["name"] == parent_name

    @pytest.mark.parametrize(
        "name, children_names",
        [
            ("coffee", ["espresso", "cold brew"]),
            ("espresso", ["single-origin espresso"]),
            ("single-origin espresso", []),
        ],
    )
    def test_relationship_children(self, client, name, children_names):
        query = """
            query($filter: Filter) {
                ingredients(filter: $filter) {
                    name
                    children {
                        name
                    }
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["ingredients"][0]

        assert result["name"] == name
        assert set([ingredient["name"] for ingredient in result["children"]]) == set(
            children_names
        )

    @pytest.mark.parametrize(
        "name, ancestor_names",
        [
            ("single-origin espresso", ["espresso", "coffee"]),
            ("espresso", ["coffee"]),
        ],
    )
    def test_relationship_ancestors(self, client, name, ancestor_names):
        query = """
            query($filter: Filter) {
                ingredients(filter: $filter) {
                    name
                    ancestors {
                        name
                    }
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["ingredients"][0]

        assert result["name"] == name
        assert set([ingredient["name"] for ingredient in result["ancestors"]]) == set(
            ancestor_names
        )

    @pytest.mark.parametrize(
        "name, descendant_names",
        [
            ("coffee", ["cold brew", "espresso", "single-origin espresso"]),
            ("espresso", ["single-origin espresso"]),
        ],
    )
    def test_relationship_descendants(self, client, name, descendant_names):
        query = """
            query($filter: Filter) {
                ingredients(filter: $filter) {
                    name
                    descendants {
                        name
                    }
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["ingredients"][0]

        assert result["name"] == name
        assert set([ingredient["name"] for ingredient in result["descendants"]]) == set(
            descendant_names
        )

    @pytest.mark.parametrize(
        "name, menu_item_names",
        [
            (
                "espresso",
                [
                    "Jazzmin",
                    "Cherry Espresso Tonic",
                    "Latte",
                    "Espresso",
                    "Americano",
                    "Lil' Sweetie",
                    "Almond Macadamia Latte",
                ],
            ),
            (
                "nut",
                [
                    "Cherry Espresso Tonic",
                    "The Renee",
                    "Almond Macadamia Latte",
                    "Iced Honey Matcha Latte",
                    "Tumi",
                ],
            ),
        ],
    )
    def test_relationship_menu_items(self, client, name, menu_item_names):
        query = """
            query($filter: Filter) {
                ingredients(filter: $filter) {
                    name
                    menuItems {
                        name
                    }
                }
            }
        """

        variables = {"filter": {"name": {"starts_with": name}}}

        response = client.post("/", json={"query": query, "variables": variables})
        result = response.json()["data"]["ingredients"][0]

        assert result["name"] == name
        assert set([ingredient["name"] for ingredient in result["menuItems"]]) == set(
            menu_item_names
        )

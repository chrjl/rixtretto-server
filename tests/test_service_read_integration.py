import json
import pytest


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

    @pytest.mark.parametrize(
        "name_filter, expected_count",
        [
            ({"starts_with": "C"}, 1),
            ({"contains": "e"}, 2),
        ],
    )
    def test_relationship_roaster(self, client, name_filter, expected_count):
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
        "name, expected_count", [("go get em tiger", 8), ("cafe saratoga", 1)]
    )
    def test_relationship_location(self, client, name, expected_count):
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
    def test_relationship_menu(self, client, service_name, expected_count):
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

import pytest


@pytest.mark.use_sample_data(True)
class TestOriginColumns:
    query = """
    query($ids: [ID], $filter: Filter) {
        origins(ids: $ids, filter: $filter) {
            id
            type
            name
            processes
            varieties
            harvest_start
            harvest_end
            details
        }
    }
    """

    def test_all_origins(self, client):
        response = client.post("/", json={"query": self.query})
        result = response.json()["data"]["origins"]

        assert response.status_code == 200
        assert len(result) == 214

    def test_filter_by_name(self, client):
        filter = {"name": {"starts_with": "Hawaii"}}
        variables = {"filter": filter}

        response = client.post("/", json={"query": self.query, "variables": variables})
        result = response.json()["data"]["origins"]

        assert response.status_code == 200
        assert result[0]["name"] == "Hawaii"
        assert type(result[0]["processes"]) == list
        assert type(result[0]["varieties"]) == list
        assert type(result[0]["details"]) == dict


@pytest.mark.use_sample_data(True)
class TestOriginSelfRelationships:
    query = """
    query($filter: Filter) {
        origins(filter: $filter) {
            parent
            children
            descendants
        }
    }
    """

    def test_parent(self, client):
        query = """
        query($filter: Filter) {
            origins(filter: $filter) {
                parent {
                    name
                }
            }
        }
        """

        variables = {"filter": {"name": {"starts_with": "hawaii"}}}

        response = client.post("/", json={"query": query, "variables": variables})

        result = response.json()["data"]["origins"]
        assert result[0]["parent"]["name"] == "United States"

    def test_children(self, client):
        query = """
        query($filter: Filter) {
            origins(filter: $filter) {
                children {
                    name
                }
            }
        }
        """

        variables = {"filter": {"name": {"starts_with": "hawaii"}}}

        response = client.post("/", json={"query": query, "variables": variables})

        result = response.json()["data"]["origins"]
        assert len(result[0]["children"]) == 2

    @pytest.mark.parametrize(
        "origin_name, expected_count, expected_names",
        [
            (
                "United States",
                6,
                ["United States", "Hawaii", "Kona", "Ka'u", "Maui", "O'ahu"],
            ),
        ],
    )
    def test_suborigins(self, client, origin_name, expected_count, expected_names):
        query = """
        query($filter: Filter) {
            origins(filter: $filter) {
                suborigins {
                    name
                }
            }
        }
        """

        variables = {"filter": {"name": {"starts_with": origin_name}}}

        response = client.post("/", json={"query": query, "variables": variables})

        result = response.json()["data"]["origins"][0]
        suborigin_names = [suborigin["name"] for suborigin in result["suborigins"]]

        assert response.status_code == 200
        assert len(result["suborigins"]) == expected_count
        assert set(expected_names) == set(suborigin_names)


@pytest.mark.use_sample_data(True)
class TestOriginRelationships:
    @pytest.mark.parametrize(
        "origin_name,expected_country_name",
        [("Hawaii", "United States"), ("Caranavi", "Bolivia")],
    )
    def test_country(self, client, origin_name, expected_country_name):
        query = """
        query($filter: Filter) {
            origins(filter: $filter) {
                country {
                    id
                    name
                }
            }
        }
        """

        variables = {"filter": {"name": {"starts_with": origin_name}}}

        response = client.post("/", json={"query": query, "variables": variables})

        result = response.json()["data"]["origins"]

        assert result[0]["country"]["name"] == expected_country_name

    def test_roasters(self):
        """TODO"""
        pass

    def test_roasted_coffees(self):
        """TODO"""
        pass

    def test_green_coffees(self):
        """TODO"""
        pass

import pytest


@pytest.mark.use_sample_data(True)
class TestRoastedCoffeeColumns:
    query = """
    query($ids: [ID], $filter: Filter) {
        roastedCoffees(ids: $ids, filter: $filter) {
            id
            name
        }
    }
    """

    def test_all_roasted_coffees(self, client):
        response = client.post("/", json={"query": self.query})
        data = response.json()["data"]
        result = data["roastedCoffees"]

        assert response.status_code == 200
        assert len(result) == 7

        for green_coffee in result:
            assert "id" in green_coffee
            assert type(green_coffee.get("id")) == str

            assert "name" in green_coffee
            if name := green_coffee.get("name"):
                assert type(name) == str


@pytest.mark.use_sample_data(True)
class TestRoastedCoffeeFilters:
    query = """
    query($ids: [ID], $filter: Filter) {
        roastedCoffees(ids: $ids, filter: $filter) {
            id
            name
        }
    }
    """

    @pytest.mark.parametrize(
        "name",
        ["Privam Estate", "Minor Monuments"],
    )
    def test_filter_by_id(self, client, name):
        response = client.post(
            "/",
            json={
                "query": self.query,
                "variables": {"filter": {"name": {"starts_with": name}}},
            },
        )

        assert response.status_code == 200

        coffee_ids = [
            coffee["id"] for coffee in response.json()["data"]["roastedCoffees"]
        ]

        assert len(coffee_ids) == 1

        response = client.post(
            "/",
            json={"query": self.query, "variables": {"ids": coffee_ids}},
        )

        assert response.status_code == 200

        coffee_name = response.json()["data"]["roastedCoffees"][0]["name"]
        assert coffee_name.startswith(name)

    @pytest.mark.parametrize(
        "name,is_valid",
        [("Privam Estate", True), ("invalid", False)],
    )
    def test_filter_by_name(self, client, name, is_valid):
        filter = {"name": {"contains": name[1:]}}
        variables = {"filter": filter}

        response = client.post("/", json={"query": self.query, "variables": variables})
        result = response.json()["data"]["roastedCoffees"]

        assert response.status_code == 200
        if is_valid:
            assert result[0]["name"].startswith(name)
        else:
            assert result == []

    @pytest.mark.parametrize(
        "profiles,count",
        [
            (["single origin"], 5),
            (["blend"], 2),
            (["blend", "espresso"], 3),
            (["nothing"], 0),
        ],
    )
    def test_filter_by_profile(self, client, profiles, count):
        filter = {"coffeeDetail": {"profiles": profiles}}
        variables = {"filter": filter}

        response = client.post("/", json={"query": self.query, "variables": variables})
        assert response.status_code == 200

        result = response.json()["data"]["roastedCoffees"]
        assert len(result) == count

    @pytest.mark.parametrize(
        "tasting,count",
        [
            (["cherry"], 2),
            (["brown sugar"], 1),
            (["chocolate", "dark chocolate"], 2),
            (["nothing"], 0),
        ],
    )
    def test_filter_by_tasting(self, client, tasting, count):
        filter = {"coffeeDetail": {"tasting": tasting}}
        variables = {"filter": filter}

        response = client.post("/", json={"query": self.query, "variables": variables})
        assert response.status_code == 200

        result = response.json()["data"]["roastedCoffees"]
        assert len(result) == count

    @pytest.mark.parametrize(
        "processes,count",
        [
            (["washed"], 3),
            (["natural"], 1),
            (["washed", "natural"], 4),
            (["washed", "anaerobic"], 3),
        ],
    )
    def test_filter_by_process(self, client, processes, count):
        filter = {"coffeeDetail": {"processes": processes}}
        variables = {"filter": filter}

        response = client.post("/", json={"query": self.query, "variables": variables})
        assert response.status_code == 200

        result = response.json()["data"]["roastedCoffees"]
        assert len(result) == count

    @pytest.mark.parametrize(
        "varieties,count",
        [
            (["sl28"], 1),
            (["sl-28"], 1),
            (["sl28", "sl-28"], 1),
            (["bourbon", "heirloom", "sl28"], 3),
            (["caturra"], 0),
        ],
    )
    def test_filter_by_variety(self, client, varieties, count):
        filter = {"coffeeDetail": {"varieties": varieties}}
        variables = {"filter": filter}

        response = client.post("/", json={"query": self.query, "variables": variables})
        assert response.status_code == 200

        result = response.json()["data"]["roastedCoffees"]
        assert len(result) == count


@pytest.mark.use_sample_data(True)
class TestRoastedCoffeeRelationships:
    @pytest.mark.parametrize(
        "name,roaster_name",
        [
            ("Privam Estate", "Christopher L"),
            ("Placer de la Tarde", "Go Get Em Tiger"),
            ("Humbuggle", "Go Get Em Tiger"),
        ],
    )
    def test_roaster(self, client, name, roaster_name):
        query = """
        query($filter: Filter) {
            roastedCoffees(filter: $filter) {
                roaster {
                    name
                }
            }
        }
        """
        variables = {"filter": {"name": {"starts_with": name}}}

        response = client.post("/", json={"query": query, "variables": variables})

        assert response.status_code == 200

        result = response.json()["data"]["roastedCoffees"][0]

        assert result["roaster"]["name"] == roaster_name

    @pytest.mark.parametrize(
        "name,origin_names",
        [
            ("Privam Estate", ["Embu"]),
            ("Humbuggle", ["Colombia", "Guatemala", "Kenya"]),
        ],
    )
    def test_origins(self, client, name, origin_names):
        query = """
        query($filter: Filter) {
            roastedCoffees(filter: $filter) {
                origins {
                    name
                }
            }
        }
        """
        variables = {"filter": {"name": {"starts_with": name}}}

        response = client.post("/", json={"query": query, "variables": variables})

        result = response.json()["data"]["roastedCoffees"][0]
        assert set([origin["name"] for origin in result["origins"]]) == set(
            origin_names
        )

    @pytest.mark.parametrize(
        "name,profiles",
        [
            ("Privam Estate", ["single origin"]),
            ("Placer de la Tarde", ["decaf", "espresso", "single origin"]),
        ],
    )
    def test_profiles(self, client, name, profiles):
        query = """
        query($filter: Filter) {
            roastedCoffees(filter: $filter) {
                profiles
            }
        }
        """
        variables = {"filter": {"name": {"starts_with": name}}}

        response = client.post("/", json={"query": query, "variables": variables})

        assert response.status_code == 200

        result = response.json()["data"]["roastedCoffees"]

        assert len(result) == 1
        assert set(result[0]["profiles"]) == set(profiles)

    @pytest.mark.parametrize(
        "name,processes",
        [("Privam Estate", ["washed"]), ("Placer de la Tarde", ["decaf", "sugarcane"])],
    )
    def test_processes(self, client, name, processes):
        query = """
        query($filter: Filter) {
            roastedCoffees(filter: $filter) {
                processes
            }
        }
        """
        variables = {"filter": {"name": {"starts_with": name}}}

        response = client.post("/", json={"query": query, "variables": variables})

        assert response.status_code == 200

        result = response.json()["data"]["roastedCoffees"]

        assert len(result) == 1
        assert set(result[0]["processes"]) == set(processes)

    @pytest.mark.parametrize(
        "name,varieties",
        [
            ("Privam Estate", ["Batian", "Ruiru 11", "SL28"]),
            ("Tariku Kare", ["heirloom"]),
            ("Humbuggle", []),
        ],
    )
    def test_varieties(self, client, name, varieties):
        query = """
        query($filter: Filter) {
            roastedCoffees(filter: $filter) {
                varieties
            }
        }
        """
        variables = {"filter": {"name": {"starts_with": name}}}

        response = client.post("/", json={"query": query, "variables": variables})

        assert response.status_code == 200

        result = response.json()["data"]["roastedCoffees"]

        assert len(result) == 1
        assert set(result[0]["varieties"]) == set(varieties)

    @pytest.mark.parametrize(
        "name,tasting",
        [
            ("Privam Estate", []),
            ("Minor Monuments", ["brown sugar", "plum", "dark chocolate"]),
            ("Humbuggle", ["chocolate", "cherry", "geranium"]),
        ],
    )
    def test_tasting(self, client, name, tasting):
        query = """
        query($filter: Filter) {
            roastedCoffees(filter: $filter) {
                tasting
            }
        }
        """
        variables = {"filter": {"name": {"starts_with": name}}}

        response = client.post("/", json={"query": query, "variables": variables})

        assert response.status_code == 200

        result = response.json()["data"]["roastedCoffees"]

        assert len(result) == 1
        assert set(result[0]["tasting"]) == set(tasting)

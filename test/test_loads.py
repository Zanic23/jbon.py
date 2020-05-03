import jbon


def test_loads_dog_example():
    j = jbon.loads(
        """
        Dog {
            name,
            age,
            owner
        }
        Dog("Scruffles", 4, "Jonah")
        Dog("Lily", 4, "Izzy")
        """
    )

    dog_0 = j[0]
    assert dog_0["name"] == "Scruffles"
    assert dog_0["age"] == 4
    assert dog_0["owner"] == "Jonah"

    dog_1 = j[1]
    assert dog_1["name"] == "Lily"
    assert dog_1["age"] == 4
    assert dog_1["owner"] == "Izzy"

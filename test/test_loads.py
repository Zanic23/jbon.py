import jbon


def test_loads_dog_example():
    j = jbon.loads(
        r"""
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
    assert dog_0.name == "Scruffles"
    assert dog_0.age == 4
    assert dog_0.owner == "Jonah"

    dog_1 = j[1]
    assert dog_1["name"] == "Lily"
    assert dog_1["age"] == 4
    assert dog_1["owner"] == "Izzy"


def test_loads_more_types():
    j = jbon.loads(
        r"""
        Party {
            location,
            couples
        }
        Party( {x = 4, y = 3}, [<"John", "Penny">, <"Marry", "Joe">])
        """
    )
    party = j[0]
    assert party.location == {"x": 4, "y": 3}
    assert party.couples == [("John", "Penny"), ("Marry", "Joe")]


def test_loads_untyped():
    j = jbon.loads(
        r"""
        Mouse {
            position,
            click
        }
        Mouse({x = 2, y = 3}, true)
        Mouse({x = 2, y = 3}, "Nope")
        Mouse({x = 2, y = 3}, 324)
        """
    )

    assert j[0].click == True
    assert j[1].click == "Nope"
    assert j[2].click == 324

    assert j[0].position["x"] == 2
    assert j[0].position["y"] == 3


def test_loads_named_value():
    j = jbon.loads(
        r"""
        Button {
            position,
            color,
            text
        }
        Button:MainMenu( {x = 3, y = 10}, { r = 32, g = 34, b = 22}, "Play")
        """
    )

    assert j["MainMenu"].text == "Play"

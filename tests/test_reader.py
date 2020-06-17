from dataclasses import dataclass
from pcsd_cog.events import Rule
from pcsd_cog import reader

def test_mapping_generation():
    cell_range = "TESTS!A2:E9"
    values = reader.get_sheet(cell_range)
    mapping = reader.parse(values)
    print(mapping)


def test_distance():
    events = [
             Rule({"team": "ORDER", "killer": "Minion"}),
             Rule({"team": "ORDER"}),
             Rule({"team": "CHAOS", "killer": "Minion"}),
             Rule({"team": "CHAOS"}),
             Rule({}),
             ]
    
    expected_scores = [2, 1, 0, 0, 0]

    cell_range = "TESTS!A1:E9"
    values = reader.get_sheet(cell_range)
    mapping = reader.parse(values)["EventInhibKilled"]

    rule = list(mapping.keys())[0]
    scores = [rule.distance(r) for r in events]
    assert scores == expected_scores

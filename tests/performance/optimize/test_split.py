from pytest_cases import parametrize_with_cases

from athena.performance.optimize.split import (
    create_cross_validation_divisions,
    division_to_split,
    Split,
)


def test_create_cross_validation_divisions():
    assert create_cross_validation_divisions(nb_divisions=1, nb_test=1) == [[1]]
    assert create_cross_validation_divisions(nb_divisions=3, nb_test=1) == [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]
    assert create_cross_validation_divisions(nb_divisions=4, nb_test=2) == [
        [1, 1, 0, 0],
        [1, 0, 1, 0],
        [1, 0, 0, 1],
        [0, 1, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 1],
    ]
    assert create_cross_validation_divisions(nb_divisions=5, nb_test=3) == [
        [1, 1, 1, 0, 0],
        [1, 1, 0, 1, 0],
        [1, 1, 0, 0, 1],
        [1, 0, 1, 1, 0],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 1, 1],
        [0, 1, 1, 1, 0],
        [0, 1, 1, 0, 1],
        [0, 1, 0, 1, 1],
        [0, 0, 1, 1, 1],
    ]


class DivisionToSplitCases:
    """Generate cases for `division_to_split` function

    Cases:

    - classical, 20% test at the end, no index purged

    """

    def case_no_purge(self):
        return (
            [0, 0, 0, 0, 1],
            100,
            0,
            Split(
                train_indexes=list(range(0, 80)),
                test_indexes=list(range(80, 100)),
            ),
        )


@parametrize_with_cases(
    "division, total_size, purge_size, expected_split", cases=DivisionToSplitCases
)
def test_division_to_split(division, total_size, purge_size, expected_split):
    new_split = division_to_split(
        division=division, total_size=total_size, purge_size=purge_size
    )
    assert new_split.train_indexes == expected_split.train_indexes
    assert new_split.test_indexes == expected_split.test_indexes

from pytest_cases import parametrize_with_cases

from athena.core.fluctuations import Fluctuations
from athena.performance.optimize.split import (
    _create_cross_validation_divisions,
    _division_to_split,
    Split,
    create_ccpv_splits,
)


def test_create_cross_validation_divisions():
    assert _create_cross_validation_divisions(nb_divisions=1, nb_test=1) == [[1]]
    assert _create_cross_validation_divisions(nb_divisions=3, nb_test=1) == [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]
    assert _create_cross_validation_divisions(nb_divisions=4, nb_test=2) == [
        [1, 1, 0, 0],
        [1, 0, 1, 0],
        [1, 0, 0, 1],
        [0, 1, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 1],
    ]
    assert _create_cross_validation_divisions(nb_divisions=5, nb_test=3) == [
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

    def case_simple_split(self):
        return (
            [0, 0, 0, 0, 1],
            100,
            0,
            Split(
                train_indexes=list(range(0, 80)),
                test_indexes=list(range(80, 100)),
            ),
        )

    def case_test_in_middle(self):
        return (
            [0, 0, 1, 0, 0],
            100,
            0,
            Split(
                train_indexes=list(range(0, 40)) + list(range(60, 100)),
                test_indexes=list(range(40, 60)),
            ),
        )

    def case_multiple_tests(self):
        return (
            [0, 0, 1, 0, 1],
            100,
            0,
            Split(
                train_indexes=list(range(0, 40)) + list(range(60, 80)),
                test_indexes=list(range(40, 60)) + list(range(80, 100)),
            ),
        )

    def case_purge(self):
        return (
            [0, 0, 1, 0, 1],
            100,
            5,
            Split(
                train_indexes=list(range(0, 35)) + list(range(65, 75)),
                test_indexes=list(range(40, 60)) + list(range(80, 100)),
            ),
        )

    def case_total_size_not_even(self):
        return (
            [0, 0, 1, 0, 1],
            256,
            5,
            Split(
                train_indexes=list(range(0, 51 * 2 - 5))
                + list(range(51 * 3 + 5, 51 * 4 - 5)),
                test_indexes=list(range(51 * 2, 51 * 3)) + list(range(51 * 4, 51 * 5)),
            ),
        )


@parametrize_with_cases(
    "division, total_size, purge_size, expected_split", cases=DivisionToSplitCases
)
def test_division_to_split(division, total_size, purge_size, expected_split):
    new_split = _division_to_split(
        division=division, total_size=total_size, purge_size=purge_size
    )
    assert new_split.train_indexes == expected_split.train_indexes
    assert new_split.test_indexes == expected_split.test_indexes


def test_create_ccpv_splits(generate_candles):
    split_generator = create_ccpv_splits(
        fluctuations=Fluctuations.from_candles(
            generate_candles(
                size=1000,
                timeframe="1h",
            )
        ),
        test_size=0.2,
        test_samples=3,
        purge_factor=0.01,
    )
    assert len(split_generator.splits) == 455
    assert (
        len(split_generator.splits[0].test_indexes) == 0.2 * 1000 - 2
    )  # should theoretically be 200, but 198 is fine

    train_fluctuations, test_fluctuations = split_generator.get_split(0)
    assert (
        len(train_fluctuations.candles) == 1000 - 198 - 0.01 * 1000
    )  # size - test_size - purge_size
    assert len(test_fluctuations.candles) == 198  # same value as test_indexes length

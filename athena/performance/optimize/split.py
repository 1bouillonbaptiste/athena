from dataclasses import dataclass

import numpy as np

from athena.core.fluctuations import Fluctuations


@dataclass
class Split:
    """Stores indexes for train and validation splits."""

    train_indexes: list[int]
    test_indexes: list[int]


class SplitManager:
    """Stores a collection of `Split` associated to an instance of `Fluctuations`.`"""

    def __init__(self, fluctuations: Fluctuations, splits: list[Split]):
        self.fluctuations = fluctuations
        self.splits = splits


def create_cross_validation_divisions(
    nb_divisions: int, nb_test: int
) -> list[list[int]]:
    """Generate the different combinations of cross validation splits.

    The generated arrays can be interpreted as portions of any collection to be put in test.
    [0, 0, 0, 0, 1] -> last 20% are reserved.
    [0, 1, 1, 0, 0] -> portion from 20% to 40% are reserved.
    [1, 0, 0, 0, 1] -> portions from 0% to 20% and from 80% to 100% are reserved.

    Cross-validation splits for an array of size 4 with 2 test samples are
    [1, 1, 0, 0]
    [1, 0, 1, 0]
    [1, 0, 0, 1]
    [0, 1, 1, 0]
    [0, 1, 0, 1]
    [0, 0, 1, 1]

    Args:
        nb_divisions: size of the array to split (4 in the above example)
        nb_test: number of test samples (2 in the above example)

    Returns:
        cross-validation splits of an array of size `size` as a list of lists.
    """
    if nb_test == 1:
        return [row.tolist() for row in np.eye(nb_divisions, dtype=int)]
    else:
        all_splits = []
        for ii in range(nb_divisions - nb_test + 1):
            base_split = [0] * ii + [1]
            tail_splits = create_cross_validation_divisions(
                nb_divisions - len(base_split), nb_test - 1
            )
            new_splits = [base_split + new for new in tail_splits]
            all_splits.extend(new_splits)
        return all_splits


def division_to_split(division: list[int], total_size: int, purge_size: int):
    """Convert a cross-validation division to a cross-validation split.

    The division is a list of samples indexes to put in test, [0, 0, 0, 0, 1] -> last 20% are reserved for test
    The split is an object containing actual train indexes and test indexes.

    Args:
        division: list of cross-validation divisions
        total_size: the size of the time sereis to split
        purge_size: the size of indexes to purge between train and test

    Returns:
        an instance of `Split` containing train and test data indexes
    """
    division_size = total_size // len(division)
    purged_indexes = []
    test_indexes = []
    for sample_index in np.argwhere(division)[0]:
        sample_from = division_size * sample_index
        sample_to = sample_from + division_size
        purge_from = sample_from - purge_size
        purge_to = sample_to + purge_size
        test_indexes.extend(list(range(sample_from, sample_to)))
        purged_indexes.extend(list(range(purge_from, purge_to)))

    return Split(
        train_indexes=sorted(list(set(range(total_size)) - set(purged_indexes))),
        test_indexes=sorted(test_indexes),
    )


def create_ccpv_splits(
    fluctuations: Fluctuations,
    test_size: float,
    test_samples: int,
    purge_factor: float = 0.01,
) -> SplitManager:
    """Create the Combinatorial Purged Cross Validation Splits of the fluctuations.

    Args:
        fluctuations: market data
        test_size: the overall ratio of candles to be put in test
        test_samples: number of test samples
        purge_factor: the ratio of purged indexes before and after test split to avoid leakage between train and test

    Returns:
        an instance of SplitManager
    """

    nb_divisions = round(test_samples / test_size)
    purge_size = round(len(fluctuations) * purge_factor)

    all_splits = [
        division_to_split(
            division=division, total_size=len(fluctuations), purge_size=purge_size
        )
        for division in create_cross_validation_divisions(
            nb_divisions=nb_divisions, nb_test=test_samples
        )
    ]

    return SplitManager(fluctuations=fluctuations, splits=all_splits)

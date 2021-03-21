import json
from pathlib import Path
from typing import Dict, List, Tuple


def load_data_results(base_filename: str, only_data: bool = False) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Load the data and results for the tests. 

    Parameters
    ----------
    base_filename : str
        the base filename shared by the data and result files.
    only_data : bool, optional
        flag to skip the loading of the results, by default False

    Returns
    -------
    Tuple[List[str], List[Dict[str, str]]]
        the data and the results.
    """

    path_test_data = Path(f"test/data/{base_filename}.json")
    with open(path_test_data) as f:
        test_data = json.loads(f.read())
    test_data = [json.dumps(data) for data in test_data]

    if only_data:
        return test_data

    path_test_results = Path(f"test/data/{base_filename}_readable.json")
    with open(path_test_results) as f:
        test_data_results = json.loads(f.read())

    return test_data, test_data_results

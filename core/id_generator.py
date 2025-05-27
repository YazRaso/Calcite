import pickle
import os
import uuid


def generate_id() -> str:
    """
    generate_id() produces a UUID
    checks pickle to see if UUID was previously generated else returns the UUID
    :return str:
    """
    # load past UUIDs
    ids = set()
    pickle_path = "../assets/ids.pkl"
    if os.path.exists(pickle_path):
        with open(pickle_path, "rb") as id_file:
            ids = pickle.load(id_file)
    unique_id = str(uuid.uuid4())
    # Loop until we find an id not used before
    while unique_id in ids:
        unique_id = str(uuid.uuid4())
    ids.add(unique_id)
    with open(pickle_path, "wb") as id_file:
        pickle.dump(ids, id_file)
    return unique_id

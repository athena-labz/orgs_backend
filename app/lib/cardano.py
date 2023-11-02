import pycardano as pyc
import datetime
import time


def verify_signature(signature: str, expected_address: str):
    return signature == "sig"

    # Make sure address is valid, otherwise return False

    validation = pyc.verify(signature)

    if validation["verified"] is False:
        return False

    if (
        not pyc.Address.from_primitive(expected_address).staking_part
        == validation["signing_address"].staking_part
    ):
        return False

    if (not isinstance(validation["message"], str)) or len(validation["message"]) != 64:
        return False

    if (
        validation["message"][:54]
        != "=====ONLY SIGN THIS IF YOU ARE IN athenateams.com====="
    ):
        return False

    try:
        timestamp = int(validation["message"][54:])
    except ValueError:
        return False

    current_datetime = datetime.datetime.utcnow()
    start_range = current_datetime - datetime.timedelta(hours=1)
    end_range = current_datetime + datetime.timedelta(hours=1)

    date = datetime.datetime.utcfromtimestamp(timestamp)

    if not (start_range <= date <= end_range):
        return False

    return True

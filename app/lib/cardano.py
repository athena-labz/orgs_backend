import pycardano as pyc
import datetime
import logging


from app.lib import environment


def current_network():
    network = environment.get("NETWORK")

    if network == "MAINNET":
        return pyc.Network.MAINNET
    elif network == "TESTNET":
        return pyc.Network.TESTNET
    else:
        raise ValueError(f"NETOWORK not recognised: {network}")


def verify_signature(signature: str, expected_address: str):
    parsed = signature.split("H1+DFJCghAmokzYG")
    if len(parsed) != 2:
        logging.info("Signature formatted incorrectly, wrong split!")
        return False

    parsed_signature = {
        "key": parsed[0],
        "signature": parsed[1],
    }

    try:
        validation = pyc.verify(parsed_signature)
    except Exception as e:
        logging.info(e)
        logging.info("Invalid signature, got exception while verifying it!")
        return False

    if validation["verified"] is False:
        logging.info("Invalid signature, not verified!")
        return False

    if (
        not pyc.Address.from_primitive(expected_address).staking_part
        == validation["signing_address"].staking_part
    ):
        logging.info("Invalid signature, wrong stake address!")
        return False

    if (not isinstance(validation["message"], str)) or len(validation["message"]) != 64:
        logging.info(
            "Signature formatted incorrectly, not found message with 64 characters!"
        )
        return False

    if (
        validation["message"][:54]
        != "======ONLY SIGN IF YOU ARE IN app.athenalabo.com======"
    ):
        logging.info("Invalid signature, wrong message!")
        return False

    try:
        timestamp = int(validation["message"][54:])
    except ValueError:
        logging.info("Signature formatted incorrectly, no timestamp given!")
        return False

    current_datetime = datetime.datetime.utcnow()
    start_range = current_datetime - datetime.timedelta(hours=1)
    end_range = current_datetime + datetime.timedelta(hours=1)

    date = datetime.datetime.utcfromtimestamp(timestamp)

    if not (start_range <= date <= end_range):
        logging.info("Signature expired!")
        return False

    return True

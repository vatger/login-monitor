def split_compare(cs1: str, cs2: str) -> bool:
    """
    Compares two callsigns only by prefix and suffix while replacing DEP->APP, such that EDDF_1_DEP ~ EDDF_N_APP.
    This allows to match connection to endorsement
    :param cs1: Callsign 1
    :param cs2: Callsign 2
    :return:
    """
    return cs1.split('_')[0] == cs2.split('_')[0] and cs1.split('_')[-1].replace('DEP', 'APP') == cs2.split('_')[-1].replace('DEP', 'APP')

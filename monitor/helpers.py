def split_compare(cs1: str, cs2: str) -> bool:
    """
    Compares two callsigns only by prefix and suffix while replacing DEP->APP, such that EDDF_1_DEP ~ EDDF_N_APP.
    This allows to match connection to endorsement
    :param cs1: Callsign 1
    :param cs2: Callsign 2
    :return:
    """
    return cs1.split('_')[0] == cs2.split('_')[0] and cs1.split('_')[-1].replace('DEP', 'APP') == cs2.split('_')[-1].replace('DEP', 'APP')


def string_multiple(fam: str) -> str:
    out = ""
    if '+' in fam:
        sub_reqs = [r.strip() for r in fam.split("+")]
        for i in range(len(sub_reqs) - 1):
            out += sub_reqs[i] + " AND "
        out += sub_reqs[-1]
    else:
        return fam
    return out


def stringify_fams(required_fams):
    out = ""
    for j in range(len(required_fams) - 1):
        print(required_fams[j])
        out += string_multiple(required_fams[j])
        out += " OR "
    out += string_multiple(required_fams[-1])
    return out


def check_user_familiarisations(user_fams, required_fams):
    """
    Checks if a user meets familiarisation requirements where list items
    represent ALTERNATIVES (OR), and items separated by '+' represent JOINT requirements (AND).
    """
    user_fams_set = set(user_fams)

    if not required_fams:
        return True

    for req in required_fams:
        # Split by '+' to handle requirements where multiple fams are needed together (AND)
        sub_reqs = [r.strip() for r in req.split("+")]

        # If the user has ALL components for this specific option, they qualify
        if all(sub in user_fams_set for sub in sub_reqs):
            return True

    return False
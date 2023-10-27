import re


def separate_number(whole_string) :
    match = re.search(r'\d+', whole_string)
    return int(match.group()) if match else 0

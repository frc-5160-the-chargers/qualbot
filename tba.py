import tbapy

def get_event_id(event, year=2019):
    '''get a tba formatted event id'''
    return f"{year}{event}"

def get_match_ids(tba_client: tbapy.TBA, event_name, year=2019, comp_level="qm"):
    '''get all match ids in a dict in order of how they were played'''
    event_id = get_event_id(event_name, year)
    return {m["match_number"]: m for m in tba_client.event_matches(event_id, simple=True) if m["comp_level"] == comp_level}

def get_next_unplayed(tba_client: tbapy.TBA, event, year=2019, comp_level="qm", return_first=False):
    '''get the next unplayed match at an event. will return the first match using the obvious parameter'''
    matches = get_match_ids(tba_client, event, year, comp_level)
    for match in [matches[i+1] for i in range(0, len(matches))]:
        if match["actual_time"] < 1000000000: # lol this is bad
            return match
        elif return_first:
            return match
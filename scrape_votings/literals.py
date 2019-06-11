quote_page = "https://www.bundestag.de/ajax/filterlist/de/" \
             "parlament/plenum/abstimmung/484422-484422/" \
             "h_6810466be65964217012227c14bad20f" \
             "?limit=10&noFilterSet=true{}"

path_voting_dir = "votings"
path_individual_votings_dir = path_voting_dir + "/individual"

path_logging_file = "scrape_log.log"

# TODO: get list of factions from html select field
factions = [("CDU/CSU", "CDU%2FCSU"), ("SPD", "SPD"), ("AFD", "AfD"), ("FDP", "FDP"),
            ("Die Linke", "DIE+LINKE."), ("Bündnis90/Grüne", "B90%2FGR%C3%9CNE"),
            ("Fraktionslose", "fraktionslose")]

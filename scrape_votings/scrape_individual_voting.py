from scrape_votings.scrape_dashboard import get_votings
import json
import os
from scrape_votings.helper import try_open, json_dump, print_progress, setup_custom_logger
from bs4 import BeautifulSoup
from scrape_votings.entities import Politician, CustomEncoder
from scrape_votings.literals import path_voting_dir, path_individual_votings_dir, factions


logger = setup_custom_logger('scrape')

# get overview of votings - necessary for further individual votings!
get_votings()

if not os.path.isdir(path_individual_votings_dir):
    os.mkdir(path_individual_votings_dir)

with open(path_voting_dir + "/votings.json", "r", encoding="utf8") as f:
    data = json.load(f)

# list of votings
votings = data.get("votings")
if votings is None:
    raise ValueError("imported json file does not exhibit the correct structure")

url = "https://www.bundestag.de/apps/na/na/namensliste.form?" \
      "id={}&ajax=true&letter=&fraktion={}&bundesland=&plz" \
      "=&geschlecht=&alter="

# dict supposed to hold (faction - list of politican)-pairs
all_votings = {}
l = len(votings)

for idx, voting in enumerate(votings):
    if os.path.isfile(path_voting_dir + "/individual/" + str(voting["id"]) + ".json"):
        log_str = "File ", str(voting.get("id")), ".json found. Skipping crawl."
        logger.info(log_str)
        continue  # TODO check for latest voting to use break instead of continue - not necessary though
    print("New VOTING!!!! --- ID: ", str(voting.get("id")))
    for faction in factions:
        if voting.get("id"):
            # restart from there in case of a timeout
            page = try_open(url.format(voting["id"], faction[1]))
            soup = BeautifulSoup(page, "html.parser")

            # get all divs (politicians)
            divs = soup.find_all("div", attrs={"class": "bt-slide"})

            all_votings[faction[0]] = []

            for i in divs:
                # TODO: save politicians as an entity
                text = i.div.find("div", attrs={"class": "bt-teaser-person-text"})
                full_name = text.h3.text
                comma_pos = full_name.find(",")
                name = full_name[:comma_pos]
                pre_name = full_name[comma_pos+2:]
                vote = text.find("p", attrs={"class": "bt-person-abstimmung"}).text.strip()
                vote = vote.replace("\n", "")

                # add current politician
                all_votings[faction[0]].append(Politician(pre_name, name, vote))
            if len(all_votings[faction[0]]) == 0:
                all_votings.pop(faction[0])
            politician_count = len(divs)

    json_dump("votings/individual/{}.json".format(voting["id"]), all_votings, cls=CustomEncoder)
    print_progress(idx+1, l, prefix="Progress:", suffix="Complete", bar_length=50)

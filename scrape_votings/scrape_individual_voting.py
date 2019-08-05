from scrape_votings.scrape_dashboard import get_votings
import json
import os
from scrape_votings.helper import try_open, json_dump, print_progress, setup_custom_logger
from bs4 import BeautifulSoup
from scrape_votings.entities import Politician, CustomEncoder
from scrape_votings.literals import path_voting_dir, path_individual_votings_dir, factions

# create log file
logger = setup_custom_logger('scrape')

# get overview of votings - necessary for further individual votings!
get_votings()

# automate file creation/overwrite
if not os.path.isdir(path_individual_votings_dir):
    os.mkdir(path_individual_votings_dir)

# load scraped data
with open(path_voting_dir + "/votings.json", "r", encoding="utf8") as f:
    data = json.load(f)

# list of votings
votings = data.get("votings")
if votings is None:
    raise ValueError("imported json file does not exhibit the correct structure")

url = "https://www.bundestag.de/apps/na/na/namensliste.form?" \
      "id={}&ajax=true&letter=&fraktion={}&bundesland=&plz" \
      "=&geschlecht=&alter="

# dict supposed to hold (faction: list of politican)-pairs
all_votings = {}
l = len(votings)

for idx, voting in enumerate(votings):
    if os.path.isfile(path_voting_dir + "/individual/" + str(voting["voting_id"]) + ".json"):
        log_str = "File ", str(voting.get("voting_id")), ".json found. Skipping crawl."
        logger.info(log_str)
        continue
    print("New VOTING!!!! --- ID: ", str(voting.get("voting_id")))
    for faction in factions:
        if voting.get("voting_id"):
            # restart from here in case of a timeout
            page = try_open(url.format(voting["voting_id"], faction[1]))
            soup = BeautifulSoup(page, "html.parser")

            # get all divs (politicians)
            divs = soup.find_all("div", attrs={"class": "bt-slide"})

            all_votings[faction[0]] = []

            # get politician meta- and vote data
            for i in divs:
                text = i.div.find("div", attrs={"class": "bt-teaser-person-text"})
                full_name = text.h3.text
                comma_pos = full_name.find(",")
                name = full_name[:comma_pos]
                pre_name = full_name[comma_pos+2:]
                vote = text.find("p", attrs={"class": "bt-person-abstimmung"}).text.strip()
                vote = vote.replace("\n", "")

                # add current politician
                all_votings[faction[0]].append(Politician(pre_name, name, vote))
            # remove factions that did not have any politician partake in the current voting
            if len(all_votings[faction[0]]) == 0:
                all_votings.pop(faction[0])
            politician_count = len(divs)

    json_dump("votings/individual/{}.json".format(voting["voting_id"]), all_votings, cls=CustomEncoder)
    print_progress(idx+1, l, prefix="Progress:", suffix="Complete", bar_length=50)

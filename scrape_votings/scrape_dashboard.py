from bs4 import BeautifulSoup
import re
from scrape_votings.entities import Vote, CustomEncoder
from scrape_votings.helper import try_open, json_dump, print_progress
import json
import os
from scrape_votings.literals import quote_page, path_voting_dir


def get_votings():
    # progress bar
    print_progress(0, 1, prefix="Article description crawled:", suffix="Complete", bar_length=50)

    file_exists = False
    if os.path.isdir(path_voting_dir):
        file_exists = os.path.isfile(path_voting_dir + "/votings.json")
    else:
        os.mkdir(path_voting_dir)

    latest_voting_id = None
    if file_exists:
        # get existing dict of votings
        with open(path_voting_dir + "/votings.json",
                  "r", encoding="utf8") as f:
            data = json.load(f)
            # data structure is dependent on 'data["ids"]' to be sorted descending
            latest_voting_id = data["ids"][0]
        if not data.get("votings"):
            raise KeyError("No key 'votings'")
    else:
        data = {"votings": [], "ids": []}

    changes = []

    start, limit = 0, 600
    for idx in range(start, limit, 10):

        offset = "&offset={}"
        page = try_open(quote_page.format(offset.format((str(idx)))))

        soup = BeautifulSoup(page, "html.parser")

        if soup.find("div", attrs={"class": "bt-slide-error"}):
            print("no more votings")
            votings_changed(changes)
            return

        # get all div-elements that hold information about votings
        divs = soup.find_all("div", attrs={"class": "bt-slide"})

        new_vote_list = []
        new_id_list = []
        print("Number of votings in dict: ", len(data["votings"]))
        # scrape information for each voting (div)
        print("offset(" + str(idx) + ") | #articles in current request(" + str(len(divs)) + ")")
        for i in divs:

            # TODO - typechecking str vs. int
            digits = 4
            vote_id = None
            while digits > 0:
                if vote_id is None:
                    try:
                        vote_id = int(i.find_next("a")["href"][-digits:])
                    except ValueError:
                        pass
                digits -= 1

            # TODO: check if any older votings have been added by checking all past votings (maybe once a day)
            #  - check whether older votings may even be missing in the list of scraped votings or whether it
            #  is a continuous list
            # checks presence of voting with the highest id in the list of crawled votings
            # no insurance for older votings that may have been added after a more recent crawl
            if latest_voting_id is not None and latest_voting_id >= vote_id:
                if len(new_vote_list) == 0:
                    print("Latest voting id: ", latest_voting_id)
                    print(vote_id)
                    print("No new votings since last crawl")
                    print_progress(1, 1, prefix="Article description crawled:", suffix="Complete", bar_length=50)
                    return
                else:
                    print("Some new votings since last crawl")

            changes.append(vote_id)

            data["ids"].append(vote_id)
            new_id_list.append(vote_id)

            vote_tag = i.find("div", attrs={"class": "bt-teaser-text-chart"})

            vote_yes = vote_tag.ul.find("li",attrs={"class": "bt-legend-ja"}).span.text
            vote_no = vote_tag.ul.find("li", attrs={"class": "bt-legend-nein"}).span.text
            vote_abstained = vote_tag.ul.find("li", attrs={"class": "bt-legend-enthalten"}).span.text
            vote_not_turned_in = vote_tag.ul.find("li", attrs={"class": "bt-legend-na"}).span.text

            vote_total = vote_tag.h3.contents[len(vote_tag.h3.contents) - 1].strip()
            vote_total = re.sub(r"\D", "", vote_total)

            votes = {"total": vote_total, "yes": vote_yes, "no": vote_no, "abstained": vote_abstained,
                     "not_turned_in": vote_not_turned_in}

            meta_data_tag = i.find("div", attrs={"class": "bt-teaser-text"})
            vote_date = meta_data_tag.find("span", attrs={"class": "bt-date"}).text

            # some votings do not have a genre assigned
            if meta_data_tag.h3.span is None:
                vote_genre = None
            else:
                vote_genre = meta_data_tag.h3.span.text.strip()

            # TODO: topic length will be cut when derived from the overview page as in this case
            #  get it from the individual voting instead!
            vote_topic = meta_data_tag.h3.contents[len(meta_data_tag.h3.contents) - 1].strip()
            vote_description = i.find("div", attrs={"class": "bt-teaser-haupttext"}).text.strip()

            vote = Vote()
            vote.id = vote_id
            vote.votes = votes
            vote.date = vote_date
            vote.genre = vote_genre
            vote.topic = vote_topic
            vote.description = vote_description
            new_vote_list.append(vote.dict_repr())

        # add new votes
        data["votings"].extend(new_vote_list)

        # sort ids
        data["ids"] = sorted(data["ids"], reverse=True)
        # sort voting
        data["votings"] = sorted(data["votings"], key=lambda x: x["id"], reverse=True)

        # save to file
        json_dump(path_voting_dir + "/votings.json", data, cls=CustomEncoder)

        print_progress(start + idx, limit, prefix="Progress:", suffix="Complete", bar_length=50)

    votings_changed(changes)


def votings_changed(changes):
    if len(changes) == 0:
        print("There are no new votings")
    else:
        print("Crawled {} new votings.".format(len(changes)))
        print("List of changes: ", changes)


if __name__ == "__main__":
    get_votings()

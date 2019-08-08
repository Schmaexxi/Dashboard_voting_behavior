from typing import Union, Dict, List
from bs4 import BeautifulSoup, element
import re
from scrape_votings.entities import Vote, CustomEncoder
from scrape_votings.helper import try_open, json_dump, print_progress
import json
import os
from scrape_votings.literals import quote_page, path_voting_dir
from http.client import HTTPResponse


def get_votings():
    """
    creates a json file or alters it (if already existing)
    the file holds information about votings/bills from the bundestag
    https://www.bundestag.de/abstimmung
    :return: None
    """
    # progress bar
    print_progress(0, 1, prefix="Article description crawled:", suffix="Complete", bar_length=50)

    # automate file creation/overwrite
    file_exists: bool = False
    if os.path.isdir(path_voting_dir):
        file_exists = os.path.isfile(path_voting_dir + "/votings.json")
    else:
        os.mkdir(path_voting_dir)

    latest_voting_id: Union[int, None] = None
    if file_exists:
        # get existing dict of votings
        with open(path_voting_dir + "/votings.json",
                  "r", encoding="utf8") as f:
            data: Dict[str, List[Union[Dict[str, Union[str, int]], int]]] = json.load(f)
            # continue scraping from latest_voting
            # data structure is dependent on 'data["ids"]' to be sorted descending
            latest_voting_id = data["ids"][0]
        if not data.get("votings"):
            raise KeyError("No key 'votings'")
    else:
        data: Dict[str, List[Union[Dict[str, Union[str, int]], int]]] = {"votings": [], "ids": []}

    # document new votings
    changes: List[int] = []

    # set limits of of voting id range to be scraped
    start: int = 0
    limit: int = 2000
    for idx in range(start, limit, 10):
        offset: str = "&offset={}"
        # TODO: type of page
        page: HTTPResponse = try_open(quote_page.format(offset.format((str(idx)))))

        soup: BeautifulSoup = BeautifulSoup(page, "html.parser")

        # stop condition once the latest voting id has been scraped
        if soup.find("div", attrs={"class": "bt-slide-error"}):
            print("no more votings")
            votings_changed(changes)
            return

        # get all div-elements that hold information about votings
        divs: element.ResultSet = soup.find_all("div", attrs={"class": "bt-slide"})

        new_vote_list: List[Dict[str, Union[int, str]]] = []
        new_id_list: List[int] = []
        print("Number of votings in dict: ", len(data["votings"]))
        # scrape information for each voting (div)
        print("offset(" + str(idx) + ") | #articles in current request(" + str(len(divs)) + ")")
        for i in divs:

            # get voting id
            digits: int = 4
            vote_id: Union[int, None] = None
            while digits > 0:
                if vote_id is None:
                    try:
                        vote_id = int(i.find_next("a")["href"][-digits:])
                    except ValueError:
                        pass
                digits -= 1

            # checks presence of voting with the highest id in the list of crawled votings
            # no insurance for older votings that may have been added after a more recent crawl
            if latest_voting_id is not None and latest_voting_id >= vote_id:
                if len(new_vote_list) == 0:
                    print("Latest voting id: ", latest_voting_id)
                    print("Voting id: ", vote_id)
                    print("Votings reached that have already been crawled. Stopping.")
                    print_progress(1, 1, prefix="Article description crawled:", suffix="Complete", bar_length=50)
                    votings_changed(changes)
                    return
                else:
                    print(f"continue for {vote_id}")
                    continue


            # scrape necessary information

            changes.append(vote_id)

            data["ids"].append(vote_id)
            new_id_list.append(vote_id)

            vote_tag: str = i.find("div", attrs={"class": "bt-teaser-text-chart"})

            vote_yes: str = vote_tag.ul.find("li", attrs={"class": "bt-legend-ja"}).span.text
            vote_no: str = vote_tag.ul.find("li", attrs={"class": "bt-legend-nein"}).span.text
            vote_abstained: str = vote_tag.ul.find("li", attrs={"class": "bt-legend-enthalten"}).span.text
            vote_not_turned_in: str = vote_tag.ul.find("li", attrs={"class": "bt-legend-na"}).span.text

            vote_total: str = vote_tag.h3.contents[len(vote_tag.h3.contents) - 1].strip()
            vote_total: str = re.sub(r"\D", "", vote_total)

            votes: Dict[str, str] = {"Summe": vote_total, "Ja": vote_yes, "Nein": vote_no, "Enthalten": vote_abstained,
                                     "Nicht abgegeben": vote_not_turned_in}

            meta_data_tag: element.Tag = i.find("div", attrs={"class": "bt-teaser-text"})
            vote_date: str = meta_data_tag.find("span", attrs={"class": "bt-date"}).text

            # some votings do not have a genre assigned
            if meta_data_tag.h3.span is None:
                vote_genre = "Ohne Genre"
            else:
                vote_genre = meta_data_tag.h3.span.text.strip()

            # weird multiline strings -> need to be stripped
            vote_topic: str = meta_data_tag.h3.contents[len(meta_data_tag.h3.contents) - 1].strip()
            vote_description: str = i.find("div", attrs={"class": "bt-teaser-haupttext"}).text.strip()
            # create instance & assign attributes
            vote: Vote = Vote()
            vote.id: str = vote_id
            vote.votes: Dict[str, str] = votes
            vote.date: str = vote_date
            vote.genre: str = vote_genre
            vote.topic: str = vote_topic
            vote.description: str = vote_description
            new_vote_list.append(vote.dict_repr())

        # add new votes
        data["votings"].extend(new_vote_list)

        # sort ids
        data["ids"] = sorted(data["ids"], reverse=True)
        # sort voting
        data["votings"] = sorted(data["votings"], key=lambda x: x["voting_id"], reverse=True)

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

# Dashboard_voting_behavior

A Django application for getting voting data from [Bundestagsabstimmungen](https://www.bundestag.de/abstimmung) and resupplying it.

## Getting Started

Download or clone the repository to your local machine.

### Prerequisites
Make sure you have a running PostgreSQL server and Python3 installed. You may also need to install some python packages. Run
```
pip install -r requirements.txt
```

### Installing and Deployment

Navigate to the downloaded/cloned repository. To execute the scraping scripts that will get the data from [Bundestagsabstimmungen](https://www.bundestag.de/abstimmung) run:

```
python scrape_voting/scrape_individual_voting.py
```

Set database config in settings.py to match your PostgreSQL instance. Make sure a database exists and a connection can be established before the next steps.
If the name, user or his password of your database deviates from the predefined ones in lines **152** to **154** of *fill_database.py*, change them accordingly.

The following command creates the SQL code for creating or altering the database tables:
```
python manage.py makemigrations
```

Which is then executed by running:
```
python manage.py migrate
```

Next, we fill the database with the scraped data by running:
```
python fill_database.py
```

Finally, we can start the app on your specified port with:
```
python manage.py runserver <port>
```

## Built With

* [Django](https://www.djangoproject.com/) - The web framework used
* [Chart.js](https://www.chartjs.org/) - A JavaScript framework for creating graphs
* [Daterangepicker](http://www.daterangepicker.com/) - A JavaScript framework for date selection

## Author

* **Maximilian Langknecht**



import json

with open('/Users/maximilianlangknecht/PycharmProjects/Scrape_votings/votings/votings.json') as in_file:
   data = json.load(in_file)

print(json.dumps(data, indent=4))

c = 0
with open('./database/queries/insert_json.sql', 'w+') as out_file:
    out_file.write('INSERT INTO votings.public.dashboard_votings (json) VALUES')
    for voting in data['votings']:
        if c != 0:
            out_file.write(',')
        out_file.write("('")
        out_file.write(json.dumps(voting))
        out_file.write("')")
        c += 1

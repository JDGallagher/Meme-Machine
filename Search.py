from tinydb import TinyDB, Query

db = TinyDB('data/20220779.json')
m = Query()
result = db.search(m.user_id == '35715989')
msg_names = [item['name'] for item in result]
names = []
for x in msg_names:
    if x not in names:
        names.append(x)
print(names)

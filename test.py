# import json
from datetime import datetime


a = {
    'name': 'hieu',
    'age': 18
}

b = {
    'name': 'ha',
    'age': 16
}

c = {
    'name': 'minh',
    'age': 20
}

# obj = {
#     'name': 'hieu',
#     'age': 18
# }
# obj2 = {
#     'infor': obj
# }

# j = json.dumps(obj2)
# print(j)
f = open("/home/x6hdm/Code/client/system_status.txt", "r")
lines = f.readlines()
a = []
for ln in lines:
    a.append(ln.strip())
x = []
for u in range(0, int(a[0])):
    x.append(str(a[u + 1]).split())
print(x)
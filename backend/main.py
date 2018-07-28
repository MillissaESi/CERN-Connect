from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
from flask import send_from_directory
import os
import threading

app = Flask(__name__)
CORS(app)

def ical_extract(text):
    name = ""
    time = ""
    for line in text.splitlines():
        if line.startswith("SUMMARY:"):
            name = line[len("SUMMARY:"):]
        if line.startswith("DTSTART;VALUE=DATE-TIME:"):
            time = line[len("DTSTART;VALUE=DATE-TIME:"):]
    return name, datetime.strptime(time, "%Y%m%dT%H%M%SZ")


class User:
    def __init__(self, username, coordinates, event_ids):
        self.username = username
        self.coordinates = coordinates #tuple
        self.events = event_ids

    def __eq__(self, other):
        return self.username == other.username
    
    def __hash__(self):
        return self.username.__hash__()
    
    def get_dict(self):
        return {
            "username": self.username,
            "coordinates": self.coordinates,
            "events": self.events
        }

class Event:
    new_id = 100
    def __init__(self, id, name, coordinates, dt):
        self.id = id
        self.name = name
        self.coordinates = coordinates #tuple
        self.datetime = dt #datetime
    
    def get_simple_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "count":len(self.get_members_dict()),
            "time": self.datetime.time()
        }

    def get_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.coordinates,
            "members": self.get_members_dict(),
            "time": self.datetime.time()
        }

    def get_members_dict(self):
        return [ user.get_dict() for user in users if self.id in user.events]

    @staticmethod
    def from_ical_text(ical_text):
        name, dt = ical_extract(ical_text)
        id = Event.new_id
        Event.new_id += 1
        location = [0,0] #FIXME B500 coords

        #Add event
        events[id] = Event(id, name, location, dt)





events = dict() #key = id, value = event
users = set()

events = {
    "1" : Event(1,"lol",[[46.232072, 6.058441],[46.232130, 6.058508]],datetime(2018,2,1,12,0)),
    "2" : Event(2,"openlab",[[46.229984, 6.054055],[46.229980, 6.054084]],datetime(2018,2,1, 13)) ,
    "3" : Event(3,"summerstudent",[[46.231674, 6.054388],[46.231652, 6.054393]],datetime(2018,2,1, 14)),
    "4" : Event(4,"zipline",[[46.237948, 6.036273],[46.237889, 6.036799]],datetime(2018,3,1, 16))
    }
"""
    5 : Event(1,"lecture",[[46.229602, 6.053840],[46.229984, 6.054055]],datetime(2018,2,1,12,0)),
    6 : Event(2,"physics show",[[46.229984, 6.054055],[46.229984, 6.054055]],datetime(2018,2,1, 13)) ,
    7 : Event(3,"coffee break",[[46.229984, 6.054055],[46.237599, 6.038118]],datetime(2018,2,1, 14)),
    8 : Event(4,"IT barbacue",[[46.237948, 6.036273],[46.237889, 6.036799]],datetime(2018,3,1, 16)),
    9 : Event(1,"Something",[[46.229602, 6.053840],[46.229984, 6.054055]],datetime(2018,2,1,12,0)),
"""
 #key = id, value = event

users = set()
u1 = User("millissa",[46.232587,6.045946],[1,2])
u2 = User("filipe",[46.235088,6.047212],[1,3])
u3 = User("varsha",[46.237889, 6.036799],[3,2])
u4 = User("Sinclert",[46.233286, 6.052623],[1,4])
users.add(u1)
users.add(u2)
users.add(u3)
users.add(u4)

def move_users():
    threading.Timer(3, move_users).start()
    print(u4.coordinates)
    if u1.coordinates[0] > 46.229984 and u1.coordinates[1] < 6.054055 :
        u1.coordinates[0] -= 0.000185929 #0.0003718571
        u1.coordinates[1] += 0.000579214 #0.0011584286
    if u2.coordinates[0] > 46.229984 and u2.coordinates[1] < 6.054055 :
        u2.coordinates[0] -= 0.0007291429
        u2.coordinates[1] += 0.000977571
    if u3.coordinates[0] > 46.229984 and u4.coordinates[1] < 6.054055 :
        u3.coordinates[0] -= 0.001129286
        u3.coordinates[1] +=0.002465143
    if u4.coordinates[0] > 46.229984 and u4.coordinates[1] < 6.054055 :
        u4.coordinates[0] -=0.000471714
        u4.coordinates[1] +=0.000204571

move_users()


@app.route('/')
def ep_hello():
    return app.send_static_file('index.html')
    #return 'Hello, World!'

@app.route('/upload/', methods=['POST'])
def ep_upload():
    input = json.loads(request.data)

    user = User(**input)
    users.add(user)
    print(input)

    return jsonify({"res": "OK"}), 200  #request.data #echo


@app.route('/events/', methods=['GET'])
def ep_events():
    output = []
    for event in events.values():
        output.append(event.get_simple_dict())

    return json.dumps(output, indent=4, sort_keys=True, default=str)


@app.route('/fetch/', methods=['POST'])
def ep_fetch():
    input = json.loads(request.data)

    print(input)

    output = []
    for ev_id in input:
        output.append( events[ev_id].get_dict() )
    res = json.dumps(output, indent=4, sort_keys=True, default=str)
    #print(res)
    return res

@app.route('/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'static', 'js'), filename)

if __name__ == '__main__':
    app.run(host = "127.0.0.1", port = 8080, debug = True)

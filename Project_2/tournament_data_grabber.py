import requests
import json
import os


# Moxfield Connection
class Moxfield:
    def __init__(self):
        self.api_key = os.getenv("MOXFIELD_KEY")
        self.domain = "https://api.moxfield.com/v2/decks/all/"

    def make_request(self, deck_id : str):
        url = self.domain + deck_id
        req = requests.get(url, headers={'User-Agent': self.api_key})
        if req.status_code == 200:
            jsonObj = json.loads(req.text)
            return jsonObj
        else:
            raise Exception(f"Bad Status Code for Moxfield, {req.status_code}")

    def make_plaintext_list(self, jsResponse):
        decklist = list()
        decklist.append(jsResponse["main"]["name"]) #Add Commander
        for i in jsResponse["mainboard"].keys(): # Add The Maindeck
            for _ in range(0,int(jsResponse["mainboard"][i]["quantity"])):
                decklist.append(str(i))
        return decklist

class topdeckgg:
    def __init__(self):
        self.api_key = os.getenv("TOPDECK_KEY")
        self.domain = f"https://topdeck.gg/api/v2/tournaments"

    def get_cedh_tournaments(self):
        url = self.domain
        req = requests.post(url, \
                headers={'Authorization' : self.api_key}, data={"last":10, "game":"Magic: The Gathering", "format": "EDH", "participantMin" : 20})
        if req.status_code == 200:
            tournaments = json.loads(req.text)
            tid_list = list()
            for i in tournaments:
                tid_list.append(i["TID"])
            return tid_list
        else:
            raise Exception(f"Bad Status Code for Topdeck, {req.status_code}")

    def get_tournament_results(self, TID):
        tournament = dict()
        url = self.domain + f"/{TID}/rounds"
        req = requests.get(url, headers={'Authorization': self.api_key})
        tournament = json.loads(req.text)
        return tournament

topdeck = topdeckgg()
tourneys = topdeck.get_cedh_tournaments()
for i in tourneys:
    print(json.dumps(topdeck.get_tournament_results(i), indent=4))

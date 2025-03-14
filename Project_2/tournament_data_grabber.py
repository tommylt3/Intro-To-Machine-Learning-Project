import requests
import json
import os

class Moxfield:
    def __init__(self):
        self.api_key = os.getenv("MOXFIELD_KEY")
        self.domain = "https://api.moxfield.com/v2/decks/all/"

    def make_request(self, deck_id : str):
        url = self.domain + deck_id
        req = requests.get(url, headers={'User-Agent': self.api_key})
        jsonObj = json.loads(req.text)
        return jsonObj

    def make_plaintext_list(self, jsResponse):
        decklist = list()
        decklist.append(jsResponse["main"]["name"]) #Add Commander
        for i in jsResponse["mainboard"].keys(): # Add The Maindeck
            for _ in range(0,int(jsResponse["mainboard"][i]["quantity"])):
                decklist.append(str(i))
        return decklist

class topdeckgg:
    def __init__(self):
        pass

mox = Moxfield()
deckThing = mox.make_request('OQd1CWtuFUinDEpepZfC3g')
print(mox.make_plaintext_list(deckThing), sep='\n')

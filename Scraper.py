import requests
from bs4 import BeautifulSoup
import json
import os
import re
import concurrent.futures
import threading

def jsonPopper():
    while True:
        try:
            with item_ids_lock:
                item_id = item_ids.pop()
        except IndexError:
            print("List is empty")
            break
        return item_id  # Return the item_id

def scraper():
    item_id = jsonPopper()
    if item_id is None:
        return  # No more items to process

    url = f"https://universalis.app/market/{item_id}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        item_name_element = soup.find('div', class_="item_info").h1
        item_name = item_name_element.get_text(strip=True)
        cleanData = re.sub(r"^\d+", "", item_name)
        with item_names_lock:
            item_names[item_id] = cleanData
        print(f"{item_id}:{cleanData} Has been added to the list")
    else:
        print(f"Failed to retrieve data for item ID {item_id}")



item_ids_lock = threading.Lock() # Create a lock to synchronize access to item_ids
json_file_path = os.path.join(os.getcwd(), 'json', 'items.json')

with open(json_file_path, 'r') as file:
    item_ids = json.load(file)

item_names = {}
item_names_lock = threading.Lock()  # Lock for synchronizing access to item_names

max_threads = 15
with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
    futures = [executor.submit(scraper) for _ in range(len(item_ids))]

# Wait for all threads to finish
concurrent.futures.wait(futures)
jsonfile = threading.Lock()
try:
    with open(json_file_path, 'w') as file:
        with jsonfile:
            json.dump(item_names, file)
    print("Item names saved to items.json")
except Exception as e:
    print(f"Failed to save item names to items.json: {e}")

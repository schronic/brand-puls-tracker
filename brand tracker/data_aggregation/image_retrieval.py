from serpapi import GoogleSearch
import requests
import os

from dotenv import load_dotenv
load_dotenv()

# Google Images provides a way to filter by size, image type, and more. This information is encoded in the tbs parameter. E.g., tbs=itp:photos,isz:l selects only large photos.

def google_image_search(keyword):

    GS_API_KEY = os.environ['GS_API_KEY']

    params = {
    "q": keyword,
    "tbm": "isch",
    "ijn": "0",
    "api_key": GS_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    images_results = results['images_results']

    return images_results

def bing_image_search(keyword):

    BING_API_KEY = os.environ['BING_API_KEY']
    search_url = "https://api.bing.microsoft.com/v7.0/images/search"
    search_term = keyword

    headers = {"Ocp-Apim-Subscription-Key" : BING_API_KEY}
    params  = {"q": search_term, "license": "public", "imageType": "photo"}

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    images_results = [[img["name"], img["datePublished"], img["hostPageUrl"], img["thumbnailUrl"]] for img in search_results["value"]]

    return images_results


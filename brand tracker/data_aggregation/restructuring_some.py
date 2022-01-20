from geopy.geocoders import Nominatim
from shapely.geometry import box

# REDDIT
def cleaning_reddit(reddit_list):

    for i in reddit_list: 
        unwanted = set(list(i.keys())) - set(['title', 'url', 'source', 'image_url', 'created_utc', 'selftext', 'comments'])
        for unwanted_key in unwanted: del i[unwanted_key]
        i['comments'] = list(filter(lambda a: a != ('[deleted]' and '[removed]'), i['comments']))
        
        i['text'] = i['selftext'] + '. '.join(i['comments'])
        del i['selftext']
        del i['comments']
        
        i['created'] = i.pop('created_utc')
    
    return reddit_list

# TWITTER
def cleaning_twitter(twitter_list):

    for i in twitter_list: 
        for n in ['coordinates', 'place', 'user_location']:
            if n in i.keys():
                location = n
                break
                
        if location == 'coordinates': 
            coordinates = i['coordinates']
        elif location == 'place':
            location = location['coordinates'][0]
            bounds = (location[0][0], location[0][1], location[2][0], location[2][1])
            polygon = box(*bounds)
            coordinates = [polygon.centroid.x, polygon.centroid.y]
        elif location == 'user_location':
            try: 
                locator = Nominatim(user_agent='myGeocoder')
                raw_location = locator.geocode(i['user_location'])
                coordinates = [raw_location.latitude, raw_location.longitude]
            except: 
                coordinates = None
        else: 
            coordinates = None
            
        # geo seems to be deprecated 
                
        unwanted = set(list(i.keys())) - set(['source', 'url', 'image_url', 'user_profile_image_url', 'user_screen_name', 'text', 'created_at', 'user_name', 'retweet_count', 'favorite_count'])
        for unwanted_key in unwanted: del i[unwanted_key]

        if coordinates is None: coordinates = 0
        i['location'] = coordinates
        
        for key in [('user_profile_image_url', 'profile_image_url'), ('user_screen_name', 'username'), ('created_at', 'created'), ('user_name', 'name')]:
            try: 
                i[key[1]] = i.pop(key[0])
            except: 
                pass
    
    return twitter_list

# INSTAGRAM
def cleaning_instagram(instagram_list):

    for i in instagram_list: 
        
        try: 
            locator = Nominatim(user_agent='myGeocoder')
            raw_location = locator.geocode(i['locationName'])
            coordinates = [raw_location.latitude, raw_location.longitude]
        except: 
            coordinates = None
        
        unwanted = set(list(i.keys())) - set(['source', 'displayUrl', 'caption', 'timestamp', 'alt'])
        for unwanted_key in unwanted: del i[unwanted_key] 
            
        for key in [('displayUrl', 'image_url'), ('caption', 'text'), ('timestamp', 'created')]:
            try: 
                i[key[1]] = i.pop(key[0])
            except: 
                pass
            
        i['location'] = coordinates
    
    return instagram_list
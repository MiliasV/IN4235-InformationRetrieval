import json
import geopandas as gpd
import geojson


with open("airbnb/airbnb_listings.json") as json_file:
    airbnb_listings = json.load(json_file)

#convert airbnb listings from json to geojson and normalize the prices
fc = {
    "type": "FeatureCollection",
    "features": [
    {
        "type": "Feature",
        "geometry" : {
            "type": "Point",
            "coordinates": [airbnb_listing["listing_lng"], airbnb_listing["listing_lat"]],
            },
        "properties":{
        "price_per_person": airbnb_listing['price']/float(airbnb_listing['person_capacity']),
        "total_price": airbnb_listing['price'],
        "room_type": airbnb_listing['room_type'],
        "capacity": airbnb_listing['person_capacity']
        }
     } for airbnb_listing in airbnb_listings]
}

with open('airbnb.geojson', 'w') as f:
    f.write(geojson.dumps(fc))

#exclude accommodations that are outside the official boundaries of Amsterdam
df = gpd.read_file('airbnb.geojson')
ams = gpd.read_file('airbnb/Amsterdam.GeoJson')
ams_boundary = ams.ix[0].geometry

ams_airbnb = df[df.geometry.within(ams_boundary)]
with open('airbnb_filter.geojson', 'w') as f:
    f.write(ams_airbnb.to_json())


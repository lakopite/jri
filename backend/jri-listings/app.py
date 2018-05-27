from chalice import Chalice
import os

import requests,simplejson,datetime,uuid

app = Chalice(app_name='jri-listings')

access_token = os.environ.get('ACCESS_TOKEN')
space_id = os.environ.get('SPACE_ID')
url = "https://cdn.contentful.com/spaces/"+space_id+"/entries?access_token="+access_token+"&content_type=listings" if access_token and space_id else None

category_map = {
 "Farm & Land": "farmandland",
 "Residential": "residential",
 "Multi-Residential": "multiresidential",
 "Commercial": "commercial",
 "For Lease/Rent": "forleaserent"
}

def status_sorter(s):
	return {
	 "For Sale": 7,
	 "In Escrow": 6,
	 "For Lease": 5,
	 "For Rent": 4,
	 "Sold": 3,
	 "Leased": 2,
	 "Rented": 1,
	 "Off Market": 0
	}.get(s,-1)

@app.route('/listings', methods=['GET'], cors=True, api_key_required=True)
def index():
	result = {
	 "farmandland": [],
	 "residential": [],
	 "multiresidential": [],
	 "commercial": [],
	 "forleaserent": [],
	 "ready": False,
	 "error": False
	}
	try:
		if not url:
			raise ValueError("URL not available, please make sure the contentful environment variables are set")
		r = requests.get(url)
		payload = r.json()
		assets = {i['sys']['id']: i["fields"]["file"] for i in payload["includes"]["Asset"]} if "includes" in payload else {}
		for i in payload['items']:
			i['fields']['id'] = i['sys']['id']
			i['fields']['photos'] = [assets[j['sys']['id']] for j in i['fields']['photos']] if "photos" in i['fields'] else []
			i['fields']['downloads'] = [assets[j['sys']['id']] for j in i['fields']['downloads']] if "downloads" in i['fields'] else []
			if i['fields']['category'] in category_map:
				result[category_map[i['fields']['category']]].append(i['fields'])
				result[category_map[i['fields']['category']]].sort(key=lambda x: status_sorter(x.get('status','N/A')), reverse=True)
	except Exception as e:
		print "ERROR: %s" % str(e)
		result['error'] = True
	return simplejson.dumps(result)

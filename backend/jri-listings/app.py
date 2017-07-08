from chalice import Chalice

import requests,simplejson,datetime,uuid

app = Chalice(app_name='jri-listings')

access_token = "<INSERT HERE>"
space_id = "<INSERT HERE>"
url = "https://cdn.contentful.com/spaces/"+space_id+"/entries?access_token="+access_token+"&content_type=listings"

category_map = {
 "Farm & Land": "farmandland",
 "Residential": "residential",
 "Multi-Residential": "multiresidential",
 "Commercial": "commercial",
 "For Lease/Rent": "forleaserent"
}

@app.route('/listings', methods=['GET'], cors=True)
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
		r = requests.get(url)
		payload = r.json()
		assets = {i['sys']['id']: i["fields"]["file"] for i in payload["includes"]["Asset"]} if "includes" in payload else {}
		for i in payload['items']:
			i['fields']['id'] = i['sys']['id']
			i['fields']['photos'] = [assets[j['sys']['id']] for j in i['fields']['photos']] if "photos" in i['fields'] else []
			i['fields']['downloads'] = [assets[j['sys']['id']] for j in i['fields']['downloads']] if "downloads" in i['fields'] else []
			if i['fields']['category'] in category_map:
				result[category_map[i['fields']['category']]].append(i['fields'])
	except:
		result['error'] = True
	return simplejson.dumps(result)

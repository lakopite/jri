var fs = require('fs');
var Request = require('request');
var _ = require('lodash');
var file = "./build/default/index.html";
var endpoint = _BACKEND_URL_;
var apiKey = _CHALICE_KEY_;

var host = _HOST_;

var urlMap = {
  "residential": "residential",
  "commercial": "commercial",
  "farmandland": "farm-and-land",
  "multiresidential": "multi-residential",
  "forleaserent": "for-lease-rent"
}

function parseStructuredData(items) {
  var itemlist = {
    "@context": "http://schema.org",
    "@type": "ItemList",
    "url": host,
    "name": "Current Listings",
    "numberOfItems": items.length,
    "ItemListOrder": "Unordered",
    "itemListElement": _.map(items, function(i,index_) {
      var item_ = {
        "@type": "ListItem",
        "position": index_ + 1,
        "item": {
          "@type": "SingleFamilyResidence",
          "url": host + "listing/" + i.slug,
          "name": i.title
        }
      }
      if ("photos" in i && i.photos.length > 0) {item_.item.image = i.photos[0].url};
      return item_
    })
  }
  return JSON.stringify(itemlist)
}

fs.readFile(file, 'utf8', function (err,data) {
  if (err) {
    return console.log(err);
  }
  Request.get({'uri': endpoint, 'headers': {'x-api-key': apiKey}}, function (error, response, body) {
      if (error) {
          throw error;
      }
      var b = JSON.parse(body);
      var structuredData = '\n\t<script type="application/ld+json">\n\t\t' + parseStructuredData(_.concat(b.residential,b.commercial,b.farmandland,b.multiresidential,b.forleaserent)) + "\n\t</script>"
      var result = data.replace('<!-- dynamic structured data -->', structuredData);

      fs.writeFile(file, result, 'utf8', function (err) {
         if (err) return console.log(err);
      });
  });
});

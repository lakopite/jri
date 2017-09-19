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

function parseStructuredData(key,items) {
  var itemlist = {
    "@context": "http://schema.org",
    "@type": "ItemList",
    "url": host + urlMap[key],
    "numberOfItems": items.length,
    "ItemListOrder": "Unordered",
    "itemListElement": _.map(items, function(i,index_) {
      var item_ = {
        "@type": "Product",
        "position": index_ + 1,
        "url": host + i.slug,
        "name": i.title
      }
      if ("photos" in i && i.photos.length > 0) {item_.image = i.photos[0].url};
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
      var respData = JSON.parse(body);
      var structuredData = "";
      for (var k in urlMap) {
          if (k in respData && respData[k].length > 0) {structuredData += '\n\t<script type="application/ld+json">\n\t\t' + parseStructuredData(k,respData[k]) + "\n\t</script>"}
      }
      var payload = JSON.stringify(respData);
      var result = data.replace('<!-- dynamic structured data -->', structuredData);

      fs.writeFile(file, result, 'utf8', function (err) {
         if (err) return console.log(err);
      });
  });
});

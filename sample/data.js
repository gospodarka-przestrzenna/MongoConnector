conn = new Mongo();
db = conn.getDB("mongoConnectorSampleDB");
db.mongoConnectorSampleCollection.insert({"ID":1,"anydata":[6,"dog"],"Name":"streetname1","linestring":[[0,0],[0,1]]})
db.mongoConnectorSampleCollection.insert({"ID":2,"anydata":[7],"Name":"streetname2","linestring":[[0,0],[1,0]]})
db.mongoConnectorSampleCollection.insert({"ID":3,"anydata":["cat","dog"],"Name":"streetname","linestring":[[1,0],[1,1]]})
db.mongoConnectorSampleCollection.insert({"ID":4,"anydata":[],"Name":"streetname3","linestring":[[0,1],[1,1]]})
db.mongoConnectorSampleCollection.insert({"ID":5,"anydata":[9,"cat"],"Name":"Ōńć©ķüĶć√ļ","linestring":[[1,1],[2,4],[5,1]]})

db.mongoConnectorSampleGeoJsonCollection.insert(
{ "ID":1,
  "type": "Feature",
  "geometry":
  { "type": "Point", "coordinates": [ 5825988.674041865393519, 5585671.816971934400499 ] }
})

db.mongoConnectorSampleGeoJsonCollectionPolygon.insert(
{ "ID":1,
  "properties":
 { "src": 81 , "dst": 13095, "sd_id": 59, "sel": 3.500000 },
 "geometry": { "type": "Polygon",
    "coordinates": [
      [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],
      [ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]
      ]
   }

})
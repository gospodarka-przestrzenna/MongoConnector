conn = new Mongo();
db = conn.getDB("mongoConnectorSampleDB");
db.mongoConnectorSampleCollection.insert({"ID":1,"anydata":[6,"dog"],"Name":"streetname1","linestring":[[0,0],[0,1]]})
db.mongoConnectorSampleCollection.insert({"ID":2,"anydata":[7],"Name":"streetname2","linestring":[[0,0],[1,0]]})
db.mongoConnectorSampleCollection.insert({"ID":3,"anydata":["cat","dog"],"Name":"streetname","linestring":[[1,0],[1,1]]})
db.mongoConnectorSampleCollection.insert({"ID":4,"anydata":[],"Name":"streetname3","linestring":[[0,1],[1,1]]})
db.mongoConnectorSampleCollection.insert({"ID":5,"anydata":[9,"cat"],"Name":"Ōńć©ķüĶć√ļ","linestring":[[1,1],[2,4],[5,1]]})
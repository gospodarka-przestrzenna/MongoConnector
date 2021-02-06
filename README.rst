MongoConnector
==============

This Qgis plugin imports data from Mongodb database into layer.
Choose database, collection and geometry field
to import whole collection as layer with data.

Requires pymongo>=3.7 and
mongodb>=3.0 ( https://www.mongodb.org/ )

Features:
    - Connecting to mongo
    - Errors handling
    - Adding features
    - It supports all geometry types if they are in geojson format
    - Otherwise new layer with "point" or with "lines" can be added
    - Geojson "properties" features are also supported

Usage:
    - Hit connect button to view all Your databases
    - Choose database
    - Choose collection in database
    - Choose if geometry is in geojson format or ...
    - Choose geometry field in collection

Please refer data example for more details.


Currently we look for changes made by https://github.com/soohwan-hyun/MongoConnector

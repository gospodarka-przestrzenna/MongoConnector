MongoConnector
==============

This Qgis plugin imports data from Mongodb database into layer.
Choose database, collection and geometry field
to import whole collection as layer with data.

Requires pymongo>=3.7 and
mongodb>=3.0 ( https://www.mongodb.org/ )

Features:
    - Connecting to mongo (also with connection string)
    - saving connection string in local file
    - Errors handling
    - Adding features
    - It supports all geometry types if they are in geojson format
    - Otherwise new layer with "point" or with "lines" can be added
    - Geojson "properties" features are also supported

Usage:
    - Alter connection string to meet your needs
    - Hit connect button to view all Your databases
    - Choose database
    - Choose collection in database
    - Choose if geometry is in geojson format or ( ordinar type ex. gemometry: [x,y])
    - Choose geometry field in collection

Please refer data example for more details.


Special thanks to contributors: 
    - fernando.passe@ufv.br
    - soohwan-hyun

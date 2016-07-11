MongoConnector
==============

This Qgis plugin imports data from Mongodb database into layer.
Choose database, collection and geometry field
to import whole collection as layer with data.

Requires pymongo>=3.0 and
mongodb>=3.0 ( https://www.mongodb.org/ )

Features:
    - connecting to mongo
    - Errors handling
    - It supports all geometry types if they are in geojson format
    - Adding new layer with "point" and with "lines"

Usage:
    - Hit connect button to view all Your databases
    - Choose database
    - Choose collection in database
    - Choose if geometry is in geojson format or ...
    - Choose geometry field in collection


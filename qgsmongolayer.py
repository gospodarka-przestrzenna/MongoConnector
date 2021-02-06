# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2018 Maciej Kamiński (kaminski.maciej@gmail.com) Politechnika Wrocławska
#                    Fernando Passe (fernando.passe@ufv.br) Universidade Federal de Viçosa
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
###############################################################################
__author__ = 'Maciej Kamiński Politechnika Wrocławska and Fernando Ferreira Passe'

from qgis.core import *
from PyQt5.QtCore import  QVariant
import uuid


class QgsMongoLayer(QgsVectorLayer):

    def __init__(self,mongoConnector,database,collection,geometryField,geometryFieldType):
        self.mongoConnector=mongoConnector
        self.database=database
        self.collection = collection
        self.geometryField=str(geometryField)
        self.geometryFieldType=geometryFieldType
        if self.geometryField == '_id':
            raise TypeError(" _id field may not be geometry")
        # I hope it fits into memory
        self.data=list(mongoConnector[database][collection].find())
        self.idFieldCheck(self.data[0])
        self.reference_item_id=self.data[0]["_id"]
        self.reference_item=self.data[0]

        self.featuresKeys=self.getFeatureKeys(self.data[0])
        print(self.featuresKeys)

        if not all([(type(key)==str or type(key)==unicode) for key in self.featuresKeys]):
            raise TypeError("All attribute names in feature must be string."+
                      "Check object "+str(self.reference_item_id))

        if "_id" in self.featuresKeys:
            self.featuresKeys.remove("_id")

        if geometryField in self.featuresKeys:
            self.featuresKeys.remove(geometryField)

        # We don't know geometry Yet
        self.geometryType=None
        self.geometryType=self.getGeometryType(self.data[0])

        #lets keep types and QVariants in one place
        self.featuresKeyType=dict([(key,self.getKeyType(key)[0])
                                   for key in self.featuresKeys])
        self.featuresKeyQVariant=dict([(key,self.getKeyType(key)[1])
                                   for key in self.featuresKeys])


        # We take first item geometry as layer geometry (as reference)

        self.addLayer()

        self.startEditing()

        self.setLayerAttributes()

        # add layer features
        for feature in self.data:
            qfeature=QgsFeature()

            self.idFieldCheck(feature)

            if not self.geometryType == self.getGeometryType(feature):
                raise ValueError("Check geometry in object "+
                                 str(feature["_id"])+
                                 " or "+str(self.reference_item_id))

            if geometryFieldType=="geojson":
                geometryList=feature[geometryField]["coordinates"]
            else:
                geometryList=feature[geometryField]


            if self.geometryType=="Point":
                qfeature.setGeometry(QgsGeometry.fromPointXY(
                    QgsPointXY(*geometryList)
                ))
            elif self.geometryType== "LineString":
                qfeature.setGeometry(QgsGeometry.fromPolylineXY([
                    QgsPoint(*pt) for pt in geometryList
                ]))
            elif self.geometryType== "Polygon":
                qfeature.setGeometry(QgsGeometry.fromPolygonXY([
                    [QgsPointXY(*pt) for pt in ring]
                        for ring in geometryList
                ]))
            elif self.geometryType== "MultiPoint":
                qfeature.setGeometry(QgsGeometry.fromMultiPointXY([
                    QgsPointXY(*pt) for pt in geometryList
                ]))
            elif self.geometryType== "MultiLineString":
                qfeature.setGeometry(QgsGeometry.fromMultiPolylineXY([
                    [QgsPointXY(*pt) for pt in line]
                        for line in geometryList
                ]))
            elif self.geometryType== "MultiPolygon":
                qfeature.setGeometry(QgsGeometry.fromMultiPolygonXY([
                    [[QgsPointXY(*pt) for pt in ring]
                        for ring in polygon]
                            for polygon in geometryList
                ]))
            else:
                raise TypeError("Unknown geometry in feature "+str(feature["_id"]))

            qfeature.setAttributes(self.createAttributes(feature))

            self.addFeature(qfeature)

        # we don't need all those data
        del(self.data)

        self.commitChanges()


    def idFieldCheck(self,feature):
        """
        Checks if feature has _id field witch is mandatory. Throws Error.
        :param feature: feature to chceck
        :return: None
        """
        if "_id" not in feature.keys():
            raise ValueError("'_id' field must be an objects identifier."+
                             "Not found in "+str(self.data[0]))

    def addLayer(self):
        """
        Creates described layer point/line...
        :return: None
        """

        super(QgsMongoLayer,self).\
            __init__(self.geometryType,
                     self.collection+'-'+str(uuid.uuid4())[0:4],
                     "memory")

    def setLayerAttributes(self):
        """
        Writes attributes to layer. Writes required fields
        :return:None
        """
        for key in self.featuresKeys:
            self.addAttribute(QgsField(key,self.featuresKeyQVariant[key]))

    def getKeyType(self,key):
        """
        checks type of element get by key
        :param key: key
        :return: tuple (base type , QVariant type)
        """

        if type(self.getFeatureValue(self.data[0],key)) is int:
            return (int,QVariant.Int)

        if type(self.getFeatureValue(self.data[0],key)) is float:
            return (float,QVariant.Double)

        # we try to put lists and other strange objects to str
        return (str,QVariant.String)

    def getFeatureKeys(self,feature):
        #print(self.geometryFieldType,feature.keys())
        if self.geometryFieldType=="geojson" and "properties" in feature.keys():
            return list(feature["properties"].keys())
        else:
            return list(feature.keys())

    def getFeatureValue(self,feature,key):
        if self.geometryFieldType=="geojson" and "properties" in feature.keys():
            return feature["properties"][key]
        else:
            return feature[key]


    def createAttributes(self,feature):
        """
        Manage attribute of features
        :param feature: feature for witch we obtain geometry
        :return: prepared list of attributes
        """
        #check keys existence
        featureKeys=self.getFeatureKeys(feature)
        for field_key in self.featuresKeys:
            if field_key not in featureKeys:
                raise ValueError("Field "+field_key+
                                 " missing in object "+str(feature["_id"]))

        attributes=[]
        for key in self.featuresKeys:
            try:

                attrib=self.featuresKeyType[key](self.getFeatureValue(feature,key))
            except UnicodeEncodeError as e:
                # if unicode we simply pass it (it's a string)
                attrib = self.getFeatureValue(feature,key)
            except:
                raise TypeError("Can't cast attribute "+key+
                                " in object "+str(feature['_id'])+
                                " to type "+str(self.featuresKeyType[key]))

            attributes.append(attrib)
        return attributes

    def getGeometryType(self,feature):
        """
        Try to recognize geometry
        :param feature: one feature for witch we try to recognize geometry
        :return: 'point' for point geometry 'line' for line geometry
        """
        if self.geometryField not in feature.keys():
            raise IndexError("No geometry in object "+str(feature["_id"]))
        if self.geometryFieldType == "geojson":
            if "type" not in feature[self.geometryField]:
                raise ValueError("Unknown geojson geometry type in object "+str(feature["_id"]))
            if feature[self.geometryField]["type"] == "GeometryCollection":
                raise ValueError("Due to QGIS limitations GeometryCollection is unsupported type in object "+str(feature["_id"]))
            return feature[self.geometryField]["type"]
        else:
            try:
                if len(feature[self.geometryField])==2 and ((
                                isinstance(feature[self.geometryField][0],int) or
                                isinstance(feature[self.geometryField][0],float)) and (
                                isinstance(feature[self.geometryField][1],int) or
                                isinstance(feature[self.geometryField][1],float))):
                    return "Point"

                if isinstance(feature[self.geometryField],list) and \
                    all([(isinstance(element,list) or isinstance(element,tuple)) and
                            len(element)==2 and ((
                            isinstance(element[0],int) or
                            isinstance(element[0],float)) and (
                            isinstance(element[1],int) or
                            isinstance(element[1],float)))
                         for element in feature[self.geometryField]]):
                    return "LineString"
            except:
                pass


        raise ValueError("Unknown geometry in object "+str(feature["_id"]))

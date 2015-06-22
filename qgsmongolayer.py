# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2015 Maciej Kamiński (kaminski.maciej@gmail.com) Politechnika Wrocławska
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
__author__ = 'Maciej Kamiński Politechnika Wrocławska'

from qgis.core import QgsVectorLayer,QgsField,QgsFeature,QgsGeometry,QgsPoint,QgsMapLayerRegistry
from PyQt4.QtCore import  QVariant

class QgsMongoLayer(QgsVectorLayer):

    def __init__(self,mongoConnector,database,collection,geometryField):
        self.mongoConnector=mongoConnector
        self.database=database
        self.collection = collection
        self.geometryField=geometryField
        # I hope it fits into memory
        self.data=list(mongoConnector[database][collection].find())

        # get all keys as columns in layer data
        self.keysOrder=self.data[0].keys()
        self.keysOrder.remove("_id")
        self.keysOrder.remove(geometryField)

        if not self.checkCollection():
            raise TypeError("Improper collection")

        self.recognizedGeometry=self.getGeometryType(self.data[0][self.geometryField])
        if self.recognizedGeometry=="point":
            gtype="Point"
        elif self.recognizedGeometry== "line":
            gtype="LineString"
        else:
            pass

        super(QgsMongoLayer,self). \
            __init__(gtype,'mongo-'+self.collection,"memory")

        self.startEditing()

        for key in self.keysOrder:
            self.addAttribute(QgsField(str(key),self.getKeyQVariant(key)))

        for feature in self.data:

            qfeature=QgsFeature()

            if self.recognizedGeometry=="point":
                qfeature.setGeometry(QgsGeometry.fromPoint(
                    QgsPoint(*feature[geometryField])
                ))
            elif self.recognizedGeometry== "line":
                qfeature.setGeometry(QgsGeometry.fromPolyline([
                    QgsPoint(*pt) for pt in feature[geometryField]
                ]))
            else:
                pass
            attributes=[]

            for key in self.keysOrder:

                if self.getKeyQVariant(key) == QVariant.Int:
                    attrib = int(feature[key])
                if self.getKeyQVariant(key) == QVariant.Double:
                    attrib = float(feature[key])
                if self.getKeyQVariant(key) == QVariant.String:
                    try:
                        # we try to put lists and other strange objects to str
                        attrib = str(feature[key])
                    except UnicodeEncodeError as e:
                        # if unicode we simply pass it
                        attrib = feature[key]
                    except:
                        raise NotImplemented()

                attributes.append(attrib)

            qfeature.setAttributes(attributes)

            self.addFeature(qfeature)
        # we tnt need all those data
        del(self.data)
        self.commitChanges()


    def getKeyQVariant(self,key):

        if type(self.data[0][key]) is int:
            return QVariant.Int

        if type(self.data[0][key]) is float:
            return QVariant.Double

        return QVariant.String

    def checkCollection(self):
        """
        Checks if keys in each mongo document are same
        Checks if geometry in each document is same
        :return: Thru if ok False otherwise
        """
        if len(self.data)>0 and \
            all([set(self.data[0].keys())==set(element.keys())
                for element in self.data]) and \
            all([self.getGeometryType(self.data[0][self.geometryField])==
                self.getGeometryType(element[self.geometryField])
                for element in self.data]):
            return True
        return False

    def analyzeFieldType(self,field):
        pass

    def getGeometryType(self,featureGeometry):
        """
        Try to recognize geometry
        :param featureGeometry: one feature for witch we try to recognize geometry
        :return: 'point' for point geometry 'line' for line geometry
        """
        if len(featureGeometry)==2 and (
                        isinstance(featureGeometry[0],int) or
                        isinstance(featureGeometry[0],float) or
                        isinstance(featureGeometry[1],int) or
                        isinstance(featureGeometry[1],float)):
            return "point"

        if isinstance(featureGeometry,list) and \
            all([(isinstance(element,list) or isinstance(element,tuple)) and
                    len(element)==2 and (
                    isinstance(element[0],int) or
                    isinstance(element[0],float) or
                    isinstance(element[1],int) or
                    isinstance(element[1],float))
                 for element in featureGeometry]):
            return "line"

        raise TypeError("Improper Geometry")
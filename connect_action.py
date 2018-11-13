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
__author__ = 'Maciej Kamiński Politechnika Wrocławska'

from PyQt5.QtWidgets import QAction,QMessageBox,QApplication
from PyQt5.QtCore import Qt, QBasicTimer
from .maindialog import MongoConnectorDialog
from .qgsmongolayer import QgsMongoLayer
from qgis.core import *
from pymongo import MongoClient

class ConnectAction(QAction):
    """
    Action for opening dock widget for database connections
    """
    def __init__(self,plugin):
        super(ConnectAction,self).__init__(plugin.qicon,"Connect",plugin.iface.mainWindow())
        self.triggered.connect(self.run)

        self.plugin=plugin
        self.iface=plugin.iface
        self.dlg=MongoConnectorDialog()
        self.mongo_client=MongoClient(serverSelectionTimeoutMS=2000)

        # binding frontend actions with logic
        self.dlg.connectButton.clicked.connect(self.reconnect)
        self.dlg.databaseBox.activated[str].connect(self.database_box_change)
        self.dlg.collectionBox.activated[str].connect(self.collection_box_change)
        self.dlg.geometryFieldBox.activated[str].connect(self.geometry_field_box_change)
        self.dlg.geojsonCheckBox.stateChanged.connect(self.geojson_check_box_changed)

    def reconnect(self):
        """
        Fill available databases to combobox
        :return:
        """
        self.dlg.databaseBox.setEnabled(False)
        self.dlg.databaseBox.clear()
        self.clearComboBoxData()

        dbs = self.get_info()
        if dbs:
            self.dlg.databaseBox.addItems(dbs)
            self.dlg.databaseBox.setEnabled(True)


    def database_box_change(self,text):
        """
        Fill available collections in database to combobox
        :param text:
        :return:
        """
        self.dlg.collectionBox.setEnabled(False)
        self.dlg.collectionBox.clear()
        self.dlg.geometryFieldBox.setEnabled(False)
        self.dlg.geometryFieldBox.clear()
        colls = self.get_info()
        if colls:
            self.dlg.collectionBox.addItems(colls)
            self.dlg.collectionBox.setEnabled(True)


    def collection_box_change(self,text):
        """
        Show fields in collection.
        :param text:
        :return:
        """
        self.dlg.geometryFieldBox.setEnabled(False)
        self.dlg.geometryFieldBox.clear()
        fields = self.get_info()
        if fields:
            self.dlg.geometryFieldBox.addItems(fields)
            self.dlg.geometryFieldBox.setEnabled(True)
        if "geometry" in fields:
            self.dlg.geojsonCheckBox.setEnabled(True)

    def geojson_check_box_changed(self,check_state):
        print("state changed")
        if Qt.Checked==self.dlg.geojsonCheckBox.checkState():
            self.geometry_field_box_change("")

    def geometry_field_box_change(self,_):
        """
        When geometry field chose add new layer. Print message when unsuccessful
        :param text:
        :return:
        """
        try:
            layer_info=self.get_info()
            print(layer_info)
            self.clearComboBoxData()
            layer=QgsMongoLayer(*layer_info)
            QgsProject.instance().addMapLayer(layer)
        except Exception as e:
            #print sys.exc_info()[0]
            QMessageBox.warning(self.dlg,
                            "Can't add layer",
                            "Error: " + str(e),
                            QMessageBox.Ok)

    def get_info(self):
        """
        Get proper info depending on what has been selected
        :return:
        it might be databases list
        it might be collections if db is set
        it might be fields if two previous are set
        it might be tuple with all above if everything is set
        """
        self.dlg.connectionStatus.setText("Connecting...")
        # repainting without delay
        QApplication.processEvents()

        output=None
        # we try that all because database connection can fail anytime
        try:
            mc=self.mongo_client
            if not self.dlg.databaseBox.isEnabled():
                output = mc.list_database_names()
            else:
                db=self.dlg.databaseBox.currentText()
                if not self.dlg.collectionBox.isEnabled():
                    output = mc[db].list_collection_names()

                else:
                    coll=self.dlg.collectionBox.currentText()
                    if not self.dlg.geometryFieldBox.isEnabled():
                        # we assume that geometry field is in every document
                        output = mc[db][coll].find_one().keys()
                    else:
                        if not Qt.Checked == self.dlg.geojsonCheckBox.checkState():
                            geom_field=self.dlg.geometryFieldBox.currentText()
                            output=(mc,db,coll,geom_field,"default")
                        else:
                            output=(mc,db,coll,"geometry","geojson")

            self.dlg.connectionStatus.setText("Connected")
        except:
            # on fail we clear all gathered data connection has to be reestablished first
            self.dlg.connectionStatus.setText("Unable to connect")
            self.dlg.databaseBox.setEnabled(False)
            self.dlg.databaseBox.clear()
            self.clearComboBoxData()
        return output

    def clearComboBoxData(self):
        self.dlg.collectionBox.setEnabled(False)
        self.dlg.collectionBox.clear()
        self.dlg.geometryFieldBox.setEnabled(False)
        self.dlg.geometryFieldBox.clear()
        self.dlg.geojsonCheckBox.setEnabled(False)
        self.dlg.geojsonCheckBox.setCheckState(Qt.Unchecked)


    def run(self):
        """
        Just show/dock Widget
        """
        self.iface.addDockWidget(Qt.LeftDockWidgetArea,self.dlg)


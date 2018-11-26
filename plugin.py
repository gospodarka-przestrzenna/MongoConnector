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

from os import path
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from .connect_action import ConnectAction

class MongoConnectorPlugin(object):
    def __init__(self,iface):
        self.iface=iface
        self.plugin_path=path.dirname(path.abspath(__file__))
        self.icon_path=path.join(self.plugin_path,'images','icon.png')
        self.qicon=QIcon(self.icon_path)
        self.plugin_menu_entry="&Mongo Connector"
        self.menu_actions=[]
        # test requirements
        try:
            from pymongo import MongoClient
        except ImportError as e:
            QMessageBox.critical(iface.mainWindow(),
                            "Missing module",
                            "Pymongo module is required",
                            QMessageBox.Ok)
            return
        #adding actions
        self.menu_actions.append(ConnectAction(self))



    def initGui(self):
        """
        Gui initialization and actions adding
        """
        for action in self.menu_actions:
            self.iface.addPluginToDatabaseMenu(self.plugin_menu_entry,action)
            self.iface.addDatabaseToolBarIcon(action)

    def unload(self):
        """
        Gui purge
        """
        for action in self.menu_actions:
            self.iface.removePluginDatabaseMenu(self.plugin_menu_entry,action)
            self.iface.removeDatabaseToolBarIcon(action)

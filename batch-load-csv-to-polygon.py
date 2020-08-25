# Copy and paste this script directly into QGIS Python Console (Ctrl+Alt+P).
# This script loads latitude/longitude pairs .csv files as polygons.
# Lines in the file are treated as individual points to serve as bounds for the polygon.
# The fill colors of the polygons are random.
# Algorithms used are "qgis:pointstopath" and "qgis:linestopolygons".
# EPSG:4326 is WGS-84 and should be changed to suit your dataset (https://epsg.io/)
# The layer is loaded into memory only. User must export layers manually.
# A label is added to the polygon. User must enable the label manually.
# The label consists of the file's name, with the .csv extension removed.
# Input files must have a header describing the columns.
#
# Example input file:
#
# latitude,longitude
# -15.55155125152125,-37.978509719587123
# -15.51251251213123,-37.857192873412312
# -15.51254151231232,-37.123897123987123

import os, glob
from qgis import processing
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor

basePath = '/cpgeo_database/20/ENP/Sismicas_3D/csv'
baseUri = "file://"+basePath

instance = QgsProject.instance()

ext = ".csv"

for file in glob.glob(os.path.join(basePath, "*%s" % ext)):
    line = ".".join(file.split("/")[-1].split(".")[:-1])
    uri = os.path.join(baseUri, "%s%s?encoding=%s&delimiter=%s&xField=%s&yField=%s&crs=%s" % (line, ext, "UTF-8",",", "longitude", "latitude","epsg:4326"))
    points = QgsVectorLayer(uri, line, "delimitedtext")
    points.addExpressionField('abs($id)', QgsField('index', QVariant.Int))
    paths = processing.run('qgis:pointstopath', {'INPUT':points, 'ORDER_FIELD':'index', 'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
    polygon = processing.run('qgis:linestopolygons',{'INPUT': paths, 'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
    polygon.setName(line)
    polygon.setLabelsEnabled(True)
    layer_settings  = QgsPalLayerSettings()
    text_format = QgsTextFormat()
    text_format.setFont(QFont("Arial", 8))
    text_format.setSize(8)
    buffer_settings = QgsTextBufferSettings()
    buffer_settings.setEnabled(True)
    buffer_settings.setSize(0.10)
    buffer_settings.setColor(QColor("black"))
    text_format.setBuffer(buffer_settings)
    layer_settings.setFormat(text_format)
    layer_settings.fieldName = "@layer_name"
    layer_settings.placement = 4
    layer_settings.enabled = True
    layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
    polygon.setLabeling(layer_settings)
    instance.addMapLayer(polygon)

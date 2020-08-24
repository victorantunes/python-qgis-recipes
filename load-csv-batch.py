# Copy and paste this script directly into QGIS Python Console (Ctrl+Alt+P).
# This script loads latitude/longitude .csv files as red line layers.
# Lines in the file are treated as individual points.
# The algorithm "qgis:pointstopath" converts your points to a single path.
# A label will be added to each layer, but it must be applied manually on the UI.
# EPSG:4326 is WGS-84 and should be changed to suit your dataset (https://epsg.io/)
# Files must have a header describing the columns.
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

basePath = '<basepath>'
baseUri = "file://"+basePath

instance = QgsProject.instance()

ext = ".csv"


for file in glob.glob(os.path.join(basePath, "*%s" % ext)):
    line = ".".join(file.split("/")[-1].split(".")[:-1])
    uri = os.path.join(baseUri, "%s%s?encoding=%s&delimiter=%s&xField=%s&yField=%s&crs=%s" % (line, ext, "UTF-8",",", "longitude", "latitude","epsg:4326"))
    points = QgsVectorLayer(uri, line, "delimitedtext")
    path = processing.run('qgis:pointstopath', {'INPUT':points, 'ORDER_FIELD':'latitude', 'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
    path.setName(line)
    symbolLayer = path.renderer().symbol().symbolLayer(0)
    symbolLayer.setWidth(1)
    symbolLayer.setColor(QColor('#ff0000'))
    path.setLabelsEnabled(True)
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
    path.setLabeling(layer_settings)
    path.triggerRepaint()
    instance.addMapLayer(path)

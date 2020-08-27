# Copy and paste this script directly into QGIS Python Console (Ctrl+Alt+P).
# This script loads latitude/longitude .csv files as polygons.
# Each line in the file must have a single latitude/longitude pair.
# Points are converted into a single path, then into a polygon.
# Layers are loaded onto memory only.
# Each layer is assigned a label containing the name of the file, minus the extension.
# Labels are not toggled on by default. User must enable them manually on the QGIS GUI.
# CRS is EPSG:4326 (WGS-84) and should be changed to suit your dataset (https://epsg.io/)
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

basePath = '<basePath>'
baseUri = "file://"+basePath

instance = QgsProject.instance()

ext = ".csv"

for file in glob.glob(os.path.join(basePath, "*%s" % ext)):
    # remove .csv extension
    line = ".".join(file.split("/")[-1].split(".")[:-1])
    # encoding, delimiter, xField, yField, crs
    uri = os.path.join(
      baseUri,
       "%s%s?encoding=%s&delimiter=%s&xField=%s&yField=%s&crs=%s" 
       % (line, ext, "UTF-8",",", "longitude", "latitude","epsg:4326"))
    points = QgsVectorLayer(uri, line, "delimitedtext")
    # order by feature id
    points.addExpressionField('abs($id)', QgsField('index', QVariant.Int))
    # vertices into single path, loaded onto memory
    paths = processing.run('qgis:pointstopath',
      {'INPUT': points,
        'ORDER_FIELD':'index',
        'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
    # path into polygon, loaded onto memory
    polygon = processing.run('qgis:linestopolygons', 
      {'INPUT': paths,
       'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
    polygon.setName(line)
    # label styling
    polygon.setLabelsEnabled(True)
    text_format = QgsTextFormat()
    text_format.setFont(QFont("Arial", 8))
    text_format.setSize(8)
    buffer_settings = QgsTextBufferSettings()
    buffer_settings.setEnabled(True)
    buffer_settings.setSize(0.10)
    buffer_settings.setColor(QColor("black"))
    text_format.setBuffer(buffer_settings)
    layer_settings  = QgsPalLayerSettings()
    layer_settings.setFormat(text_format)
    layer_settings.fieldName = "@layer_name"
    layer_settings.placement = 4
    layer_settings.enabled = True
    layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
    polygon.setLabeling(layer_settings)
    # add to map
    instance.addMapLayer(polygon)

# exif2gis

## What is this tool? 
An application to read EXIF data from images and extract the longitude and latitude from GPS information.  This data is then stored as a geospatial vector file for use in GIS applications such as QGIS or ArcGIS.

Language: Python 3 

## How do I run the program? 
Python 3 must be installed on your system to run this application. You must also then install the following dependencies using pip or another method: 

- [Fiona](https://pypi.org/project/Fiona/)
- [Shapely](https://pypi.org/project/Shapely/)
- [ExifRead](https://pypi.org/project/ExifRead/)

Once these are dependencies are satisfied, you can configure the application parameters detailed below or run the application from current directory as follows: 

```python
python3 exif2gis.py 
```

## How do I change the application settings? 
Open exif2gis.py in a text editor and search for the following lines: 
```python
#####PARAMS##### 
# Specify the parameters for your search. You'll probably want to change these. 
# Supported GIS formats: GPKG, ESRI Shapefile, MapInfo File. 
photo_directory = '/path/to/photos' 
layer_out = '/path/to/output.gpkg' 
layer_out_format = 'GPKG' 
################ 
```

You can safely change these parameters as needed, just remember to keep your changes wrapped in quotation marks. 

To change the location where the application will scan for photos, change the ```python photo_directory ``` variable like the example below: 
```python
photo_directory = '/home/user/Pictures' 
```

Similarly, you can change the location where the output geospatial file is saved by changing the ```python layer_out ``` variable as below: 
```python
layer_out = '/home/user/Documents/GIS/myphotos.gpkg' 
```
 
[By default, the application saves information as a OGC GeoPackage file.](http://switchfromshapefile.org/)  If you would like to change this, you can change the ```python layer_out_format ``` to either ESRI Shapefile, MapInfo File or GPKG as needed.  
```python
layer_out_format = 'ESRI Shapefile' 
```

## What formats are supported? 

The following image formats are supported: 

- JPEG 
- TIFF 

The following geospatial file types are supported: 

- OGC GeoPackage 
- ESRI Shapefile 
- MapInfo File (.TAB) 

## Can I change the projection of the output file? 

No. This application saves files in WGS84 (EPSG: 4326) as it a standard coordinate system for the earth. It is not possible to change the projection system as the application does not convert latitude and longitude to different formats.  

You can easily change the projection of the output file through the use of GIS software after running this program.  

## Why can't I use my images in other formats (PNG, BMP, GIF)? 

These formats do not store GPS information, making it impossible to plot them as a spatial vector.  

## My device shoots in HEIC/HEIF format. Can I use these photos? 

No, or at least, not yet. The library we are using to extract EXIF information (ExifRead) does not yet support the HEIC/HEIF format. If support is ever added or if another library offers support, I will look into updating this application accordingly. 

In the meantime, you must first convert your images to JPEG using the many available tools on Google.  

## To do/Missing features 

Add in other information from EXIF data including: 
- Date/time taken 
- Camera model 

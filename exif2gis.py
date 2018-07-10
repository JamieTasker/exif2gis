##########
# EXIF2GIS V1.0
# Read photo EXIF data and output GPS coordinates to geospatial vector file.
# Created by Jamie Tasker: https://www.github.com/jamietasker
##########

import fiona
from fiona.crs import from_epsg
from shapely.geometry import Point, mapping
import os
import sys
import exifread
from datetime import datetime

# To do - IMG Exif class to extract bits of information. Similar structure to Metadata script.
#		- Finish and make notes more concise
#		- Clean code.

class Logging_file(object):
    """This class just deals with logging. It's nothing too exciting."""
    
    def __init__(self, filepath):

        self.logfile = open(filepath, "w")
        self.get_logging_time()
        self.get_logging_time_epoch()
        self.start_time = self.logging_time
        self.start_time_epoch = self.logging_time_epoch

        self.logfile.writelines("Output log file from: " + sys.argv[0] + "\n")
        self.logfile.writelines("Ran on: " + self.start_time + "\n")

    def get_logging_time(self):
        """Get the current time."""

        self.logging_time = datetime.strftime(
            datetime.now(), "%d/%m/%y %H:%M:%S")

    def get_logging_time_epoch(self):
        """Get the current time in epoch."""

        self.logging_time_epoch = datetime.now()

    def write_line(self, line):
        """Write lines to the logging file."""

        self.get_logging_time()
        self.logfile.writelines(self.logging_time + " - " + line + "\n")

    def close_log(self):
        """Write a final time and close the log file."""

        self.get_logging_time()
        self.get_logging_time_epoch()
        self.end_time = self.logging_time
        self.end_time_epoch = self.logging_time_epoch
        self.time_taken = self.end_time_epoch - self.start_time_epoch

        self.logfile.writelines(
            "Script completed in: " + str(self.time_taken) + "\n")
        self.logfile.writelines(self.end_time + " - log file closed.")
        self.logfile.close()

def get_photos_from_dir(directory):
    """Get all photos from a given directory. Includes sub-folders."""

    supported_formats = ('.jpg', '.jpeg', '.png', '.gif', '.tiff', '.bmp')
    
    photos = list()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(supported_formats): 
                photos.append(root + '/' + file)
    
    return photos
        
def exif_2_longlat(photo):
    """Extract longitude and latitude in decimal format from photo EXIF data."""
    
    # Open the photo and extract the EXIF data to img_exif.
    img = open(photo, "rb")
    img_exif = exifread.process_file(img)
    photo_dict = dict()

    try:
        # Get the raw GPS data from the EXIF data, This stuff is a mess and cannot be used for GIS
        # just yet. We need to go through a rather long conversion process.
        longituderef, longitude = img_exif['GPS GPSLongitudeRef'], img_exif['GPS GPSLongitude']
        latituderef, latitude = img_exif['GPS GPSLatitudeRef'], img_exif['GPS GPSLatitude']
        # Format longitude and latitude degrees, minutes and seconds from EXIF data in a python 
        # friendly way. This involves removing characters, splitting strings and dividing the 
        # seconds.
        latitudedegrees, latitudemins, latitudesecs = (str(latitude).replace(']', '')
        	.replace('[', '').split(','))
        if '/' in latitudesecs:
            latitudedms = (str(latituderef), int(latitudedegrees), int(
                latitudemins), int(latitudesecs.split('/')[0])/int(latitudesecs.split('/')[1]))
        else:
            latitudedms = (str(latituderef), int(latitudedegrees), int(
                latitudemins), int(latitudesecs))
                
        longitudedegrees, longitudemins, longitudesecs = (str(longitude).replace(']', '')
            .replace('[', '').split(','))
        if '/' in longitudesecs:
            longitudedms = (str(longituderef), int(longitudedegrees), int(
                longitudemins), int(longitudesecs.split('/')[0])/int(longitudesecs.split('/')[1]))
        else:
            longitudedms = (str(longituderef), int(longitudedegrees), int(
                longitudemins), int(longitudesecs))


        # Convert degrees, minutes and seconds to decimal using the following formula:
        # decimal = degrees + minutes/60 + degrees/3600
        latitudedd = latitudedms[1] + latitudedms[2]/60 + latitudedms[3]/3600
        longitudedd = longitudedms[1] + longitudedms[2]/60 + longitudedms[3]/3600
        # If latitude is south or longitude is west, make negative.
        if latitudedms[0].lower() == "s":
            latitudedd *= -1
        if longitudedms[0].lower() == 'w':
            longitudedd *= -1

        # Create a dictionary. Key = photo file path, value = dictionary with longitude and latitude.
        lat_long_dict = {'latitude': latitudedd, 'longitude': longitudedd}
        photo_dict[photo] = lat_long_dict

        return photo_dict

    # if the GPS data cannot be extracted, we replace with None values.
    except KeyError:
        lat_long_dict = {'latitude': None, 'longitude': None}
        photo_dict[photo] = lat_long_dict

        return photo_dict

def create_points_layer(name, format, coord_sys, fields):
    """Create a new points GIS layer"""
    
    # Create the layer schema using data passed to the function.
    this_schema = {'geometry': 'Point',
                   'properties': fields}
    # Create the layer itself. 
    layer = fiona.open(layer_out, 'w', crs=from_epsg(coord_sys), driver=format, schema=this_schema)

    return layer

def add_points_to_layer(layer, x, y, fields):
    """Add points to a GIS layer"""

    # Add the points and properties to the layer passed to the function
    point = Point(x, y)
    layer.write({'properties': fields, 'geometry': mapping(point)})

# Main
print ('EXIF2GIS v1.0')
print ('Created by Jamie Tasker: https://www.github.com/jamietasker')
# Create and initialise a log file.
logfile = Logging_file(sys.path[0] + '/exif2gislog.txt')

#####PARAMS#####
# Specify the parameters for your search. You'll probably want to change these.
# Supported GIS formats: GPKG, ESRI Shapefile, MapInfo File.
photo_directory = '/home/example/photodir'
layer_out = '/home/example/out.gpkg'
layer_out_format = 'GPKG'
################

# Get the photos from the specified directory.
print ('\nGetting photos from directory: ' + photo_directory)
photos = get_photos_from_dir(photo_directory)
print ('Found ' + str(len(photos)) + ' photos.')
logfile.write_line('Found ' + str(len(photos)) + ' photos within ' + photo_directory)

# Pass photos to EXIF extractor function and begin reading.
print ('\nStarting search for GPS coordinates within EXIF data.')
logfile.write_line('Starting search for GPS coordinates within EXIF data.')
photo_data = dict()
current_photo_no = 1
for photo in photos:
    print ("Getting GPS coordinates for photo " + str(current_photo_no) + " of " + str(len(photos)))
    logfile.write_line("Getting GPS coordinates for photo " + photo)
    photo_exif_dict = exif_2_longlat(photo)
    photo_data[photo] = list(photo_exif_dict.values())[0]
    current_photo_no += 1

# Create a new geospatial vector file to save results to.
print ('\nCreating file: ' + layer_out)
# Define layer projection
layer_out_epsg = 4326
# Define layer fields.
layer_out_fields = {'photo_filename': 'str:255', 'x': 'float:10.6', 'y': 'float:10.6'}
logfile.write_line('File: ' + layer_out + ' created.')

# Begin adding points to file.
print ('Adding points to file: ' + layer_out)
logfile.write_line('Adding points to file: ' + layer_out)
errors = list()
success_count = 0
error_count = 0
out_layer = create_points_layer(layer_out, layer_out_format, layer_out_epsg, layer_out_fields)
for keys, values in photo_data.items():
	# If EXIF read was unsuccessful, do not add to layer.
    if values['longitude'] == None or values['latitude'] == None:
        errors.append(keys)
        logfile.write_line('Error: Cannot map ' + keys +
                           '. Reason: Missing or invalid GPS data.')
        error_count += 1
	# If EXIF read is successful, add point to layer.
    else:
        fields = {'photo_filename': os.path.split(keys)[1], 'x': values['longitude'], 
        'y': values['latitude']}
        add_points_to_layer(out_layer, values['longitude'], values['latitude'], fields)
        logfile.write_line('Successfully added ' + keys + ' to output file.')
        success_count += 1

# Give a final count of plotted points.
print('\nSuccessfully plotted: ' +  str(success_count) + ' - Unsuccessfully plotted: ' 
	+ str(error_count))
print('Check logfile for more information.')
logfile.write_line('Successfully plotted: ' + str(success_count) +
                   ' - Unsuccessfully plotted: ' + str(error_count))
print('\n\nDone!')
logfile.close_log()

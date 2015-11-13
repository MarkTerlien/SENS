#! /usr/bin/python

# standard library imports 
import sys
import os
import stat
import time
import math
#import glob
import shutil
#import zipfile
import operator
import logging
import subprocess
import xml.dom.minidom

# related third party imports
import _winreg
import win32api 
import win32con

# local application/library specific imports
import BathyDbLib
import BathyExecutablesLib

# For Geoserver API
from geoserver.catalog import Catalog, FailedRequestError

__author__="Terlien"
__date__ ="$28-mei-2010 11:49:39$"

# Module name
MODULE_NAME = "BathyToolsLib"

# Default file name
DEFAULT_FILE_NAME = "mtj"

# EMODNET UPLOAD HOST
# EMODNET_UPLOAD_HOST = "192.168.1.30"
EMODNET_UPLOAD_HOST = "164.138.25.165"

# Time to poll if process if finished (in seconds)
POLL_TIME = 5

# Assume that input is in meters when value is larger than DEGREE_TO_METER_SWITCH
# Hack in Makegrid 
DEGREE_TO_METER_SWITCH = 0.1

# Bathyspace separator
BATHYSPACE_SEP = ";"
SPACE_SEP      = " "

# Attribute name tag
ATTRIBUTE_COL_TAG  = 'ATTR_COLUMN'

# Attrbute names in parameter XML
ID              = "id"
DBUSER          = "dbuser"
DBPASSWORD      = "dbpassword"
DBCONNECT       = "dbconnect"
LOGLEVEL        = "loglevel"
OUTPUTDIRECTORY = "outputdirectory"
OUTPUTFILE      = "outputfile"
TEMPDIR         = "tempdirectory"
PROCESSID       = "ProcessObjectId"
TASKID          = "TaskId"

# Parameter names
PARAMETER_IM_ID          = "InstanceId"
PARAMETER_SEP_FILE_ID    = "InstanceId"
PARAMETER_SURVEY_ID      = "SurveyId"
PARAMETER_STARTDATE      = "StartDate"
PARAMETER_ENDDATE        = "EndDate"
PARAMETER_SURVEYTYPE     = "SurveyType"
PARAMETER_CM_ID          = "CmId"
PARAMETER_CM_ID_COMPARE  = "CmIdCompare"
PARAMETER_FILE_OUT       = "OutputFile"
PARAMETER_PRODUCT_AREA   = "ProductArea"
PARAMETER_INPUT_FILE     = "FileIn"
PARAMETER_FILE_FORMAT    = "FileFormat"
PARAMETER_FILE_MASK      = "FileMask"
PARAMETER_PROD_FORMAT    = "ProductFormat"
PARAMETER_XYZ_FORMAT     = "XyzFormat"
PARAMETER_COORD_SYS      = "CoordSysId"
PARAMETER_VERT_REF       = "VerticalRefId"
PARAMETER_VERDAT_PROD    = "VerDatProduct"
PARAMETER_VERDAT_SOURCE  = "VerDatSource"
PARAMETER_EPSGCODEOUT    = "EPSGCodeOut"
PARAMETER_VERDATOUT      = "VerDatOut"
PARAMETER_GRIDSIZE       = "GridSize"
PARAMETER_METHOD         = "Method"
PARAMETER_ETRSYEAR       = "EtrsYear"
PARAMETER_ASCII_IMP      = "AsciiImporter"
PARAMETER_PROCESS_ID     = "ProcessObjectId"
PARAMETER_OBJ_CLASS_ID   = "ObjectClassId"
PARAMETER_TRACKLINES     = "TrackLineList"
PARAMETER_DEPTH_ATTR     = "DepthAttributeName"
PARAMETER_DONARIMPORTER  = "DonarImporter"
PARAMETER_TL_FORMAT      = "TracklineFormat"
PARAMETER_TL_TYPE        = "TracklineType"
PARAMETER_METADATAMAPPER = "MetadataMapper"
PARAMETER_BAGIMPORTER    = "BagImporter"
PARAMETER_MAPSCALE       = "MapScale"
PARAMETER_CONTOURDEFTYPE = "ContourDefType"
PARAMETER_PREDEFINEDSET  = "PreDefinedSet"
PARAMETER_BEGIN          = "Begin"
PARAMETER_INCREMENT      = "Increment"
PARAMETER_LEVELS         = "Levels"
PARAMETER_RESAMPLE       = "Resample"
PARAMETER_GRIDSIZE       = "GridSize"
PARAMETER_NEIGHBOUR      = "NeighbourPercentage"
PARAMETER_INTERPOL       = "FillGridGaps"
PARAMETER_POINTS_USED    = "PostPoints"
PARAMETER_WEIGHT_FAC     = "PostPower"
PARAMETER_SEARCH_DIS     = "PostSearchDepth"
PARAMETER_SMOOTH         = "PostSmoothing"
PARAMETER_PP_SAMPLE      = "Method"
PARAMETER_VIS_TF         = "GenVisualizationFile"
PARAMETER_VIS_GRIDSIZE   = "Gridsize"
PARAMETER_PRODUCTFORMAT  = "ProductFormat"
PARAMETER_NULLVALUE      = "NullValue"
PARAMETER_GEN_CONTOURS   = "GenerateContours"
PARAMETER_GEN_SPOTS      = "GenerateSpotSounding"
PARAMETER_CONT_INTERVAL  = "ContourIntervalOpt"
PARAMETER_CONT_OUTPUTFT  = "ContourOutputFormat"
PARAMETER_MAPSCALE       = "MapScale"
PARAMETER_SPOTSOUND_TYPE = "SpotSoundingType"
PARAMETER_PERC_SPACING   = "PercentageSpacing"
PARAMETER_COLOR_MAP      = "ColorMap"
PARAMETER_NAME           = "NAME"
PARAMETER_DESCRIPTION    = "DESCRIPTION"
PARAMETER_SEP_MODEL_ID   = "SeparationModelId"
PARAMETER_HULL_FILE      = "FileIn"
PARAMETER_IS_GRID        = "Grid"
PARAMETER_DATAFILE_IN    = "DataFileIn"
PARAMETER_ALGORITHM      = "Algorithm"
PARAMETER_AUTHORITY      = "Authority"
PARAMETER_MULTI_FACTOR   = "Factor"
PARAMETER_TO_NETCDF      = "ConvertToNetCDF"
PARAMETER_COL_DEFS       = "ColumnDefinitions"
PARAMETER_COL_NUM        = "ColumnNumeric"

# Log levels
LOGLEVELS = {'debug': logging.DEBUG,
             'info': logging.INFO,
             'warning': logging.WARNING,
             'error': logging.ERROR,
             'critical': logging.CRITICAL}

DEFAULT_LOG_LEVEL = "info"
#DEFAULT_LOG_LEVEL = "debug"

# Earth perimeter (in meters)
EARTH_PERIMETER     = 40068000.0
MIN_EARTH_PERIMETER = 1

# Depth multiplication factor (by default depth is negative)
DEPTH_MULTIPLICATION_FACTOR = 1

# Missing value (used in bathyspace generation)
MISSING_VALUE = "-32767"

# BAG metadata tags to be extracted from BAG metadata XML
BAG_PROJECTION        = 'projection'
BAG_ELLIPSOID         = 'ellipsoid'
BAG_DATUM             = 'datum'
BAG_PROJECTION_PARAMS = 'projectionParameters'
BAG_CODE              = 'code'
BAG_ZONE              = 'zone'

# Mapping from BAG metadata items to columns in SDB_EPSGCODE table
BAG_EPSG_DB_MAPPING = { 'projection': 'SYS003', 'ellipsoid': 'SYS004', 'projectionParameters': 'SYS005' }
BAG_VERD_DB_MAPPING = { 'datum': 'SYS001' }

# EPSG code ETRS89
EPSGCODE_ETRS89    = 4258

# Parameters for estimation of link distance
# - A grid for hull generation msut have at least 100 grid cells
# - A gridcell in the grid must have as least 8 points
MIN_NR_GRIDCELLS = int(100)
MIN_NR_POINTS    = int(10)

# Registry entries
REGISTRY_KEY_PATH = r"Software\ATLIS\SENS"
REGISTRY_KEY_BATHYSPACE = "BathyspacePath"

def get_key_value_from_registry( value_name ) :
    """Function read key values from registry"""
    l_root    = _winreg.HKEY_CURRENT_USER
    l_keypath = REGISTRY_KEY_PATH
    l_hKey    = _winreg.OpenKey (l_root, l_keypath, 0, _winreg.KEY_READ)
    l_value, l_type  = _winreg.QueryValueEx (l_hKey, value_name)
    l_bathyspace_dir = unicode(l_value)
    return l_bathyspace_dir

def read_input_from_command_line(argv):
    """Function read command line arguments"""
    try :

        argc = len(sys.argv)
        if argc != 3:
            print "usage: <exectable> taskId parameterFile"
        else :
            return sys.argv[1], sys.argv[2]

    except Exception, err:
        os.sys.exit("Reading commandline parameters failed: ERROR: %s\n" % str(err))
        raise

def generate_parameter_value_list_from_object ( DbConnection, object_class_id, object_instance_id ) :
    """Function to build a parameter value list from object"""

    try :
        # Initialize parameter value list
        parameter_list = {}

        # Get object class def
        parameter_def_xml_db = DbConnection.get_object_def( object_class_id )
        parameter_def_xml    = str(parameter_def_xml_db)
        parameterDefDom      = xml.dom.minidom.parseString( parameter_def_xml )

        # Get object instance
        parameterValueDom  = DbConnection.get_obj_attributes_xml ( object_class_id, object_instance_id )

        # Process attributes, extract value from parameter file and write value to parameter value list
        attributes      = parameterDefDom.getElementsByTagName( ATTRIBUTE_COL_TAG )
        for attribute in attributes :
            attribute_column     = str(attribute.childNodes[0].nodeValue)
            attribute_value_tag = parameterValueDom.getElementsByTagName(attribute_column)[0]
            try :
                attribute_value     = attribute_value_tag.childNodes[0].nodeValue
            except :
                attribute_value = ""
            # Get attribute name for column
            attribute_name = DbConnection.get_attribute_name ( object_class_id, attribute_column )
            # Add key-value pair to list
            # print str(attribute_name) + " ( " + str(attribute_column) + " ) : " + str(attribute_value)
            parameter_list [ attribute_name ] = str(attribute_value)

        # garbage collection
        parameterValueDom.unlink()
        parameterDefDom.unlink()

        # Return parameter value list
        return parameter_list

    except Exception, err:
        os.sys.exit("Build a parameter value list from object failed: ERROR: %s\n" % str(err))

def generate_parameter_value_list_from_file (parameter_file_name, task_id):
    """Function to build a parameter value list from parameter file"""
    
    #<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ns2:task id="146337" xmlns:ns2="http://sens.atlis.nl/schema/tasks">
    #<config dbconnect="//10.20.0.54/senst"
    #dbpassword="SENS_PRODUCTCONTROLLER"
    #dbuser="SENS_PRODUCTCONTROLLER"
    #outputfile=""
    #outputdirectory="C:\DOCUME~1\terlien\LOCALS~1\Temp\SENS_PRODUCTCONTROLLER\146337\"
    #tempdirectory="C:\DOCUME~1\terlien\LOCALS~1\Temp\SENS_PRODUCTCONTROLLER\146337\"
    #/>
    #</ns2:task>

    try :
        # Initialize parameter value list
        parameter_list = {}

        # Parse XML file
        ParameterValueDom = xml.dom.minidom.parse(parameter_file_name)

        # Process environment parameters

        # Process task parameters
        task_parameters = ParameterValueDom.getElementsByTagName("task")
        for parameter in task_parameters :

            # Add to parameter value list
            parameter_list [ ID ]              = parameter.getAttribute(ID)

        # Process config parameters
        config_parameters = ParameterValueDom.getElementsByTagName("config")
        for parameter in config_parameters :

            # Add to parameter value list
            parameter_list [ TASKID ]          = task_id
            parameter_list [ OUTPUTFILE ]      = parameter.getAttribute(OUTPUTFILE)
            parameter_list [ OUTPUTDIRECTORY ] = parameter.getAttribute(OUTPUTDIRECTORY)
            parameter_list [ TEMPDIR ]         = parameter.getAttribute(TEMPDIR)

            # If no outputfile is given used default name
            if not parameter_list [ OUTPUTFILE ] :
                parameter_list [ OUTPUTFILE ] = DEFAULT_FILE_NAME

            # Make directory when it does not exist
            if not os.path.isdir( parameter_list [ OUTPUTDIRECTORY ] ) :
                os.mkdir( str( parameter_list [ OUTPUTDIRECTORY ] ) )

            # Add database connect parameters to parameter value list
            parameter_list [ DBUSER ]     = str(parameter.getAttribute( DBUSER ))
            parameter_list [ DBPASSWORD ] = str(parameter.getAttribute( DBPASSWORD ))
            db_connect_java               = str(parameter.getAttribute( DBCONNECT ))
            #db_connect_items              = db_connect_java.rstrip().split(":")
            #db_connect_python             = db_connect_items[0] + ":" + db_connect_items[1] + "/" + db_connect_items[2]
            if db_connect_java[:2] == "//" :
                db_connect_python = db_connect_java[2:] # remove first two //
            else :
                db_connect_python = db_connect_java
            parameter_list [ DBCONNECT ]  = db_connect_python
            parameter_list [ LOGLEVEL ]   = parameter.getAttribute( LOGLEVEL )

            # Check for log level
            if not parameter_list [ LOGLEVEL ] :
                parameter_list [ LOGLEVEL ] = DEFAULT_LOG_LEVEL

        # Extract process id parameter from parameter XML

        # Build Oracle connection to get list of parameters for process ID
        dbuser     = parameter_list [ DBUSER ]
        dbpassword = parameter_list [ DBPASSWORD ]
        dbconnect  = parameter_list [ DBCONNECT ]
        try :
            DbConnection = BathyDbLib.DbConnection ( dbuser, dbpassword, dbconnect, False, MODULE_NAME )
        except Exception, err:
            os.sys.exit("Can not establish connection with database: Execution stopped")
            os.sys.exit(str(err))

        # Now get the parameter object class (process_id) and parameter instance ID
        order_id     = parameter_list [ ID ]
        attributes   = [ BathyDbLib.PARAMETER_CLASS_COL, BathyDbLib.PARAMETER_INSTANCE_COL ]
        values       = DbConnection.get_obj_attributes ( BathyDbLib.PRODUCTORDER_CLASS_ID, order_id, attributes )
        process_id   = values[0]
        instance_id  = values[1]
        # print "ProcessId = " + str(process_id) + " instanceId = " + str(instance_id)

        # Get object class def
        # print "Get object class def"
        parameter_def_xml_db = DbConnection.get_object_def( process_id )
        parameter_def_xml    = str(parameter_def_xml_db)
        parameterDefDom      = xml.dom.minidom.parseString( parameter_def_xml )

        # Get object instance
        # print "Get object instance"
        parameterValueDom  = DbConnection.get_obj_attributes_xml ( process_id, instance_id ) 

        # Process attributes, extract value from parameter file and write value to parameter value list
        # print "Parse process attributes"

        attributes      = parameterDefDom.getElementsByTagName( ATTRIBUTE_COL_TAG )
        for attribute in attributes :
            attribute_column     = str(attribute.childNodes[0].nodeValue)
            attribute_value_tag = parameterValueDom.getElementsByTagName(attribute_column)[0]
            try :
                attribute_value     = attribute_value_tag.childNodes[0].nodeValue
            except :
                attribute_value = ""
            # Get attribute name for column
            attribute_name = DbConnection.get_attribute_name ( process_id, attribute_column )
            # print str(attribute_name) + " ( " + str(attribute_column) + ") : " + str(attribute_value)
            # Add key-value pair to list
            parameter_list [ attribute_name ] = str(attribute_value)

        # garbage collection
        ParameterValueDom.unlink()
        parameterDefDom.unlink()

        # Close db connection
        DbConnection.commit_close()

        # Return parameter value list
        return parameter_list

    except Exception, err:
        os.sys.exit("Build a parameter list for ProcessId = " + str(process_id) + " instanceId = " + str(instance_id) + " failed: ERROR: %s\n" % str(err))

def calculate_distance_on_sphere (lon1, lat1 ,lon2, lat2):

    # Calculates the distance between two points given their (lat, lon) co-ordinates.
    # It uses the Spherical Law Of Cosines (http://en.wikipedia.org/wiki/Spherical_law_of_cosines):
    #
    # cos(c) = cos(a) * cos(b) + sin(a) * sin(b) * cos(C)                        (1)
    #
    # In this case:
    # a = lat1 in radians, b = lat2 in radians, C = (lon2 - lon1) in radians
    # and because the latitude range is  [-?/2, ?/2] instead of [0, ?]
    # and the longitude range is [-?, ?] instead of [0, 2?]
    # (1) transforms into:
    #
    #  x = cos(c) = sin(a) * sin(b) + cos(a) * cos(b) * cos(C)
    #
    # Finally the distance is arccos(x)

    nautical_miles_per_lat_degree = float(60)
    meters_in_a_mile              = float(1852)

    if ((lat1 == lat2) and (lon1 == lon2)):
           return 0
    else :
        delta = lon2 - lon1
        a = math.radians(lat1)
        b = math.radians(lat2)
        C = math.radians(delta)
        x = math.sin(a) * math.sin(b) + math.cos(a) * math.cos(b) * math.cos(C)
        distance = math.acos(x) # in radians
        distance  = math.degrees(distance) # in degrees
        distance  = distance * nautical_miles_per_lat_degree # 60 nautical miles / lat degree
        distance = distance * meters_in_a_mile # 1852conversion to meters
        distance  = distance
        return distance

def bounds_file_up_to_date (logger, bathyspace_file, im_id ) :
    try :
        logger.info ("Check if bathyspace is version 1.3")
        bathyspace_dir         = os.path.dirname(bathyspace_file)
        bounds_file_tmp        = get_bounds_file_name ( logger, bathyspace_dir, im_id )
        bounds_file_up_to_date = False
        # First check if a boundary file exists
        if os.path.exists ( bounds_file_tmp ) :
            # Open bounds file
            fIn       = open(bounds_file_tmp, 'r')
            for line in fIn :
                if "nrps" in str(line) :
                    bounds_file_up_to_date = True
                    break
            fIn.close()
        return bounds_file_up_to_date
    except Exception, err:
        logger.critical("Check if boundary file has to be updated failed: ERROR: %s\n" % str(err))
        raise

def get_link_distance_limits ( DbConnection, logger, im_id, coord_sys_id, coord_sys_class_id, bathyspace_file) :
    """Function to check if link distance is correct"""
    try :
        logger.info ( "Get link distance limits for file" )

        # Get dimensions from boundary file (corrected for dataline)
        bathyspace_dir    = os.path.dirname(bathyspace_file)
        
        # For old bathyspaces boundaries may be missing so generate boundary file and store in database
        if not bounds_file_up_to_date ( logger, bathyspace_file, im_id ) :
            logger.info ("Generate SENS version 1.3 bathyspace")
            write_bounds_file ( logger, bathyspace_file, im_id, coord_sys_class_id )
            x_min, x_max, y_min, y_max, z_min, z_max = get_bathyspace_dimensions ( logger, bathyspace_dir, im_id )
            store_bathyspace_dimensions ( logger, DbConnection, BathyDbLib.IM_CLASS_ID, bathyspace_dir, im_id, coord_sys_class_id )
        else :
            x_min, x_max, y_min, y_max, z_min, z_max = get_bathyspace_dimensions ( logger, bathyspace_dir, im_id )

        # Now requery dimensions from database for nr of points
        attributes = [ BathyDbLib.IM_NR_PS_SOURCE, BathyDbLib.IM_INPUT_FORMAT_COL, BathyDbLib.IM_GRID_CELL_SIZE_COL ]
        values     = DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, im_id, attributes )
        if values[0] :
            nr_points = int(values[0])
        else :
            nr_points = int(get_nr_points_source ( logger, bathyspace_dir, im_id ))
        input_file_type_id = values[1]
        gridcell_size_in   = values[2]
        x_min              = float(x_min)
        x_max              = float(x_max)
        y_min              = float(y_min)
        y_max              = float(y_max)
        z_min              = float(z_min)
        z_max              = float(z_max)

        # Link distance is always in meters so calculate IM dimensions in meters
        if int( coord_sys_class_id ) == int( BathyDbLib.GEOGRAPHIC ) :
            
            # Get degrees for circle in pi
            attributes           = [ BathyDbLib.GEOUNIT_COL ]
            values               = DbConnection.get_obj_attributes ( BathyDbLib.GEODETIC_HORIZ_CLASS_ID, coord_sys_id, attributes )
            degree_circle_pi_id  = int(values[0])
            attributes           = [ BathyDbLib.DEGREES_PI_COL ]
            values               = DbConnection.get_obj_attributes ( BathyDbLib.GEOUNIT_CLASS_ID, degree_circle_pi_id, attributes )
            degrees_circle_pi    = float(values[0])
            degrees_circle       = round ( ( 2 * math.pi )/( degrees_circle_pi ) )
            logger.debug ( "Degrees circle: "  + str(degrees_circle) )
            
            # Convert to 360 degrees circle
            circle = float(360)
            x_min = x_min * ( circle / degrees_circle )
            x_max = x_max * ( circle / degrees_circle )
            y_min = y_min * ( circle / degrees_circle )
            y_max = y_max * ( circle / degrees_circle )
            
            # Calculate distance on sphere
            dx = calculate_distance_on_sphere ( x_max, y_min, x_min, y_min )
            dy = calculate_distance_on_sphere ( x_min, y_max, x_min, y_min )

        else :
            
            # Get the conversion factor
            attributes           = [ BathyDbLib.PROJUNIT_COL ]
            values               = DbConnection.get_obj_attributes ( BathyDbLib.GEODETIC_HORIZ_CLASS_ID, coord_sys_id, attributes )
            conversion_factor_id = int(values[0])
            attributes           = [ BathyDbLib.CONV_FACTOR_COL ]
            values               = DbConnection.get_obj_attributes ( BathyDbLib.PROJUNIT_CLASS_ID, conversion_factor_id, attributes )
            conversion_factor    = float(values[0])
            
            # Calculate distance direct
            dx = ( x_max - x_min ) * conversion_factor
            dy = ( y_max - y_min ) * conversion_factor

        logger.info( "Size of MBR is " + str( round(dx) )  + " m. by " + str( round(dy) ) + " m.")

        # Calculate min and max link distances
        max_link_distance = round ( math.sqrt( ( dx * dy ) / MIN_NR_GRIDCELLS ) )
        min_link_distance = round ( math.sqrt( ( dx * dy * MIN_NR_POINTS ) / nr_points  ) )

        logger.info("Maximum link distance = " + str(max_link_distance))
        logger.info("Minimum link distance = " + str(min_link_distance))

        # For Esri Ascii grid min link distance is gridsize
        # Correct if grid has very little data points:
        if int(input_file_type_id) == int(BathyDbLib.ESRI_ASCII_GRID_TYPE) :
            # Get grid info
            attributes = [ BathyDbLib.IM_GRID_NCOLS, BathyDbLib.IM_GRID_NROWS ]
            values     = DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, im_id, attributes )
            nr_grid_cells      = int(values[0]) * int(values[1])
            avg_y              = ( float(y_max) - float(y_min) ) / float(2.0)
            min_link_distance_grid = float ( convert_degrees_to_meters ( logger, coord_sys_class_id, gridcell_size_in, avg_y ) )
            min_link_distance_grid = round ( min_link_distance_grid )
            logger.info("Minimum link distance      : " + str(min_link_distance))
            logger.info("Minimum link distance_grid : " + str(min_link_distance_grid))
            logger.info("Number of points           : " + str(nr_points))
            logger.info("Number of gridcells        : " + str(nr_grid_cells))
            if int(min_link_distance_grid) < int(min_link_distance) :
                min_link_distance = round ( min_link_distance - (( min_link_distance - min_link_distance_grid ) * float( nr_points/nr_grid_cells )))
                logger.info("Link distance corrected " + str(min_link_distance))

        # Return min and max boundaries
        return min_link_distance, max_link_distance

    except Exception, err:
        logger.critical("Check link distance failed: ERROR: %s\n" % str(err))
        raise

def sort_table(table, cols):
    """ sort a table by multiple columns
        table: a list of lists (or tuple of tuples) where each inner list
               represents a row
        cols:  a list (or tuple) specifying the column numbers to sort by
               e.g. (1,0) would sort by column 1, then by column 0
    """
    for col in reversed(cols):
        table = sorted(table, key=operator.itemgetter(col))
    return table

def write_metadata_file ( DbConnection, logger, file_name, object_class_id, object_instance_id ) :
    """Function to generate file with metadata"""
    try :
        logger.info ( "Get metadata attributes for instance " + str(object_instance_id) )

        # Get list of attributes with values
        AttributeList = generate_parameter_value_list_from_object ( DbConnection, object_class_id, object_instance_id )

        # Write visible attribute and values to file, for domains
        # Write domain value and not domain ID
        output_table = []
        attribute_group_id_current = 0
#        for attribute_name in AttributeList :
#            attribute_type  = DbConnection.get_attribute_type ( object_class_id, str(attribute_name) )
#            attribute_is_visible, attribute_label, attribute_group_id, order_in_group = DbConnection.get_attribute_properties ( object_class_id, attribute_name )
#            if attribute_is_visible :
#                if int(attribute_type) == int(BathyDbLib.ATYPE_DOMAIN) and AttributeList [ attribute_name ] :
#                    attribute_value = DbConnection.get_domain_value ( object_class_id, str(attribute_name), int(AttributeList [ attribute_name ] ) )
#                else :
#                    attribute_value =  AttributeList [ attribute_name ]
#                output_line  = str(attribute_label) + " = " + str(attribute_value)
#                output_table.append( (str(attribute_group_id), str(order_in_group), str(output_line)) )

        for attribute_name in AttributeList :
            attribute_group_id, order_in_group, attribute_label, attribute_type = DbConnection.get_attribute_param_list ( object_class_id, str(attribute_name) )
            if attribute_group_id :
                if int(attribute_type) == int(BathyDbLib.ATYPE_DOMAIN) and AttributeList [ attribute_name ] :
                    attribute_value = DbConnection.get_domain_value ( object_class_id, str(attribute_name), int(AttributeList [ attribute_name ] ) )
                else :
                    attribute_value =  AttributeList [ attribute_name ]
                output_line  = str(attribute_label) + " = " + str(attribute_value)
                output_table.append( (str(attribute_group_id), str(order_in_group), str(output_line)) )

        # Write to file
        logger.info ( "Write metadata to file " + str(file_name) )
        fOut = open(file_name,'w')
        for line in sort_table(output_table, (0,1)):
            attribute_group_id = int(line[0])
            if attribute_group_id <> int(attribute_group_id_current) :
                # Get attribute group name
                attributes  = [ BathyDbLib.ATTR_GR_NAME_COL ]
                values      = DbConnection.get_obj_attributes ( BathyDbLib.ATTR_GROUP_CLASS_ID, attribute_group_id, attributes )
                group_name  = str(values[0])
                attribute_group_id_current = attribute_group_id
                fOut.write( "\n" )
                fOut.write( "-- " + str(group_name) + "--" + "\n" )
                fOut.write( "\n" )
            fOut.write ( line[2] + "\n" )
        fOut.close

    except Exception, err:
        logger.critical("Write metadata to file failed: ERROR: %s\n" % str(err))
        raise

# Function to filter out db connect into from parameterfile
def remove_db_parameter_values ( logger, output_file ) :
    try :
        parameterfile_name = output_file + BathyExecutablesLib.FILE_EXT_PAR
        parameterfile_tmp  = output_file + BathyExecutablesLib.FILE_EXT_TMP
        dbuser1 = str.lower(BathyExecutablesLib.MG_DBUSER)
        dbpass1 = str.lower(BathyExecutablesLib.MG_DBPASS)
        dbctx1  = str.lower(BathyExecutablesLib.MG_DBCNXT)
        dbuser2 = str.lower(DBUSER)
        dbpass2 = str.lower(DBPASSWORD)
        dbctx2  = str.lower(DBCONNECT)
        if os.path.exists ( parameterfile_name ) :
            fIn  = open(parameterfile_name ,'r')
            fOut = open(parameterfile_tmp  ,'w')
            for line in fIn :
                lline = str.lower(line)
                if dbuser1 not in lline and dbpass1 not in lline and dbctx1 not in lline :
                    if dbuser2 not in lline and dbpass2 not in lline and dbctx2 not in lline :
                        fOut.write( line )
            fIn.close()
            fOut.close()
            os.remove(parameterfile_name)
            shutil.copyfile(parameterfile_tmp, parameterfile_name)
            os.remove(parameterfile_tmp)
    except Exception, err:
        logger.critical("Remove db parameters from file failed: ERROR: %s\n" % str(err))
        raise

def zip_files ( logger, output_file ) :
    try :
        remove_db_parameter_values ( logger, output_file )
#        nr_of_files = 0
#        zip_file_name = output_file + BathyExecutablesLib.FILE_EXT_ZIP
#        if os.path.exists ( zip_file_name ) :
#            os.remove( zip_file_name )
#        output_file = output_file.encode("latin-1")
#        logger.info ( "Zip files " + str(output_file)  + " to " + str(zip_file_name))
#        file_list  = glob.glob(output_file + '*')
#        first_file = True
#        # Zip all files in file list
#        os.chdir ( os.path.dirname(output_file) )
#        for file in file_list :
#            if first_file :
#                # Create and open zipfile
#                zipFile  = zipfile.ZipFile(zip_file_name, 'w')
#                first_file = False
#            if not first_file :
#                nr_of_files = nr_of_files + 1
#                #zipFile.write(file)
#                zipFile.write( os.path.basename( file ) )
#        if file_list and zipFile :
#            zipFile.close()
#        # Now delete all files in file list
#        for file in file_list :
#            os.remove(file)
#        logger.info ( str(nr_of_files) + " files added to zipfile" )
    except Exception, err:
        logger.critical("Zip files failed: ERROR: %s\n" % str(err))
        raise

def get_working_dir ( logger, working_directory ) :

        try :
            logger.info ("Get working directory")

            # Check working directory and if not exists create directory
            if not os.path.isdir( working_directory ) :
                # Now make directory
                os.mkdir( working_directory )
                # Set directory to r/w
                os.chmod( working_directory, stat.S_IWUSR)

            # Return directory name
            return working_directory

        except Exception, err:
            logger.critical("Get working directory failed: ERROR: %s\n" % str(err))
            raise

def run_oscommand ( logger, os_command ) :
    """Function to run an operating system command"""

    def killSubProcesses(p):
        if sys.stdin.readline()[:4] == "KILL":
            p.terminate()
            os._exit(1)

    try :
        logger.info ( "Run os command " + str(os_command) )
        executable_name = os_command.rstrip().split( " " )[0]
        start_time = time.clock()
        # Start sub process
        p = subprocess.Popen( os_command )
        # Start thread to listen for KILL signal
        # thread.start_new_thread( killSubProcesses, (p,) )
        # Wait for process to finish (wait POLL_TIME seconds to prevent extensive cpu use)
        # First wait one second for fast tasks to complete
        while True :
            time.sleep( 1 )
            if p.poll() != None:
                break
            time.sleep( POLL_TIME )
        exit_code = p.returncode
        logger.info("Running executable in " + str( time.clock() - start_time ) + " secönds" )
        logger.info("Exit code os command: " + str(exit_code) )

        # Hack: for Makegrid exit code 4 is OK, but give warning
        # Hack: -1073741819 is exitcode sdsoverplot but execution is ok, so skip
        if str(executable_name) == str(BathyExecutablesLib.MAKEGRID) and int(exit_code) == int(4) :
            logger.warning("No data in IM segments")
        elif str(executable_name) == str(BathyExecutablesLib.SDSOVERPLOT) and int(exit_code) == int(-1073741819) :
            None
        elif int(exit_code) <> int(0) :
            logger.critical("Running os command failed")
            raise

        # Return
        return exit_code

    except Exception, err:
        logger.critical("Running os command failed: ERROR: %s\n" % str(err))
        raise

def check_value ( value ) :
    """Function to check whether value is None"""
    if value == MISSING_VALUE :
        return None
    elif value :
        return value
    else :
        return MISSING_VALUE

def add_file_ext (full_path, file_ext) :
    # Function to add file extension
    file_name, extension = os.path.splitext( full_path )
    if file_name and not extension :
        # Add file extension
        file_name = file_name + "." + file_ext.rstrip().split( "." )[1]
    else :
        file_name = full_path
    return file_name


def get_nr_of_lines ( logger, file_name ) :
    """Function to count number of lines in file"""
    try :
        logger.info ( "Count number of lines in file" )
        file = open(file_name,'r')
        nr_of_lines = 0
        for line in file :
            nr_of_lines = nr_of_lines + 1
            if nr_of_lines % 10000000 == 0 :
                logger.info(str(nr_of_lines) + " counted")
        file.close()
        logger.info("Total number of lines in file: " + str(nr_of_lines))
        return nr_of_lines
    except Exception, err:
        logger.critical("Count number of lines in file: ERROR: %s\n" % str(err))
        raise

def get_epsg_code ( DbConnection, logger, coord_sys_id) :
    """Function to get epsg_code from database"""
    try :
        logger.info ( "Get EPSG code from database" )    
        attributes = [ BathyDbLib.EPSG_CODE_COL ]
        values     = DbConnection.get_obj_attributes ( BathyDbLib.GEODETIC_HORIZ_CLASS_ID, coord_sys_id, attributes )
        epsg_code  = values[0]
        logger.info ( "EPSG code is " + str(epsg_code) )
        return epsg_code
    except Exception, err:
        logger.critical("Get EPSG code from database failed: ERROR: %s\n" % str(err))
        raise

def get_etrs_year ( DbConnection, logger, im_id) :
    """Function to get etrs_year for IM"""
    try :
        logger.info ( "Function to get etrs_year for IM" )
        attributes = [ BathyDbLib.IM_ETRSYEAR_COL ]
        values     = DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, im_id, attributes )
        etrs_year  = values[0]
        logger.info ( "ETRS year is " + str(etrs_year) )
        return etrs_year
    except Exception, err:
        logger.critical("Get EPSG code from database failed: ERROR: %s\n" % str(err))
        raise


def get_separation_model ( DbConnection, logger, vert_ref_id) :
    """Function to get makegrid verdat in and verdat out codes from database"""
    try :
        logger.info ( "Get separation model from database" )

        # Get separation model
        attributes    = [ BathyDbLib.SEP_MODEL_ID_COL, BathyDbLib.OFFSET_COL, BathyDbLib.M_FACTOR_COL, BathyDbLib.S_FACTOR_ID_COL ]
        values        = DbConnection.get_obj_attributes ( BathyDbLib.GEODETIC_VERTI_CLASS_ID, vert_ref_id, attributes )
        sep_model_id  = values[0]
        offset_val    = values[1]

        # Check on empty multiplication factor
        if not values[2] :
            m_factor_val = float(1.0)
        else :
            m_factor_val = float(values[2])
        s_facor_id    = values[3]

        # Get standard factor
        if s_facor_id :
            attributes    = [ BathyDbLib.S_FACTOR_COL ]
            values        = DbConnection.get_obj_attributes ( BathyDbLib.VD_MULTIFACTOR_CLASS_ID, s_facor_id, attributes )
            s_factor_val  = float(values[0])
            #m_factor_val  = m_factor_val * s_factor_val
            m_factor_val  = s_factor_val

        # Get vertical datum in/out references
        if sep_model_id :
            attributes    = [ BathyDbLib.VERDAT_IN_COL, BathyDbLib.VERDAT_OUT_COL ]
            values        = DbConnection.get_obj_attributes ( BathyDbLib.SEP_MOD_CLASS_ID, sep_model_id, attributes )
            verdat_in_id  = values[0]
            verdat_out_id = values[1]

            # Get vertical datum in
            attributes     = [ BathyDbLib.NAME_COL, BathyDbLib.MAKEGRID_COL ]
            values         = DbConnection.get_obj_attributes ( BathyDbLib.VERDATIN_CLASS_ID, verdat_in_id, attributes )
            verdat_in_name = values[0]
            verdat_in      = values[1]
            logger.info ( "Vertical datum in: " + str(verdat_in_name) )

            # Get vertical datum out
            attributes      = [ BathyDbLib.NAME_COL, BathyDbLib.MAKEGRID_COL ]
            values          = DbConnection.get_obj_attributes ( BathyDbLib.VERDATIN_CLASS_ID, verdat_out_id, attributes )
            verdat_out_name = values[0]
            verdat_out      = values[1]
            logger.info ( "Vertical datum out: " + str(verdat_out_name) )
        else :
            # No separation model so make verdat_in = verdat_out so that Makegrid does not apply a separation model
            verdat_in  = BathyDbLib.VERDAT_UNKNOWN
            verdat_out = verdat_in

        return verdat_in, verdat_out, offset_val, m_factor_val

    except Exception, err:
        logger.critical("Get separation model from database failed: ERROR: %s\n" % str(err))
        raise

def get_verdat_multiplication_factor ( DbConnection, logger, im_id ) :
    """Function to get multiplication factor for separation model"""
    try :
        logger.info ( "Get multiplication factor from separation model" )
        attributes  = [ BathyDbLib.IM_SEP_MODEL_COL ]
        values      = DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, im_id, attributes )
        vert_ref_id = int(values[0])
        ver_dat_in, ver_dat_out, offset, m_factor = get_separation_model ( DbConnection, logger, vert_ref_id )
        return m_factor
    except Exception, err:
        logger.critical("Get separation model from database failed: ERROR: %s\n" % str(err))
        raise

def convert_degrees_to_meters ( logger, coord_sys_class_id, grid_size, y ) :
    try :
        logger.info ( "Convert degree to meters" )
        if int(coord_sys_class_id) == int( BathyDbLib.GEOGRAPHIC ) :
            earth_perimeter = EARTH_PERIMETER * math.cos(math.radians(y))
            if earth_perimeter == 0 :
                earth_perimeter = MIN_EARTH_PERIMETER
            grid_size_meters = ( float(grid_size)/ float(360.0) ) * float(earth_perimeter)
        else :
            grid_size_meters = grid_size
        return grid_size_meters
    except Exception, err:
        logger.critical("Convert degree to meters failed: ERROR: %s\n" % str(err))
        raise

def convert_cell_size ( logger, coord_sys_class_id, cell_size, y ) :
    """Function to convert metres to decimal degrees when coord system is geographic"""

    try:
        if int(coord_sys_class_id) == int( BathyDbLib.GEOGRAPHIC ) :
            logger.info ( "Convert cellsize " + str(cell_size) + " m. at latitude " + str(y) )
            earth_perimeter = EARTH_PERIMETER * math.cos(math.radians(y))
            if earth_perimeter == 0 :
                earth_perimeter = MIN_EARTH_PERIMETER
            cell_size_new = ( float(cell_size) /earth_perimeter ) * 360
        else :
            cell_size_new = cell_size

        logger.info ( "Cellsize is " + str(cell_size_new) )
        return cell_size_new

    except Exception, err:
        logger.critical("Convert cellsize for coordinate system failed: ERROR: %s\n" % str(err))
        raise

def get_coord_sys_class ( DbConnection, logger, coord_sys_id ) :
    """Function to get coordinate system class (geographic or projected from database"""
    try :
        logger.info ( "Check coordinate system is projected or geographic" )
        attributes         = [ BathyDbLib.COORD_CLASS_COL ]
        values             = DbConnection.get_obj_attributes ( BathyDbLib.GEODETIC_HORIZ_CLASS_ID, coord_sys_id, attributes )
        coord_sys_class_id = values[0]
        return coord_sys_class_id
    except Exception, err:
        logger.critical("Check coordinate system is projected or geographic: ERROR: %s\n" % str(err))
        raise

def get_x_y ( logger, file_in ) :
    """Function to get x,y coordinate from file"""
    try :
        logger.info ( "Get x,y coordinate from file" )
        fCheck = open(file_in, 'r')
        line = fCheck.readline()
        coordinates = line.rstrip().split()
        x = float(coordinates[0])
        y = float(coordinates[1])
        fCheck.close()
        return x,y
    except Exception, err:
        logger.critical("Get x,y coordinate from file failed: ERROR: %s\n" % str(err))
        raise

def get_minimum_gap_area ( logger, l_cell_size ) :
    try :
        logger.info ( "Calculate minimum gap area" )
        l_gap_radius   = ( float(l_cell_size) / 2.0 )
        l_min_gap_area = ( ( l_gap_radius )  ** 2.0 ) * math.pi
        return l_min_gap_area
    except Exception, err:
        logger.critical("Calculate minimum gap area failed: ERROR: %s\n" % str(err))
        raise

def get_min_gap_area ( logger, epsg_desc_cmdop, link_distance, y ) :
    """Function to calculate minimum area of gaps in hull"""
    try :
        logger.info ( "Calculate minimum gap area" )
        # First two charaters of epsg_code cmdop determine whether it is geographic or not
        # FG = Geographic => Convert meters to decimal degrees TO DO: Add cos latitude!
        # FP = Projected
        if epsg_desc_cmdop[:2] == 'FG' :
            earth_perimeter = EARTH_PERIMETER * math.cos(math.radians(y))
            if earth_perimeter == 0 :
                earth_perimeter = MIN_EARTH_PERIMETER
            min_gap_size = ( ( ( ( float(link_distance)/float(earth_perimeter) ) * 360.0 ) / 2.0 ) ** 2.0 ) * math.pi
        if epsg_desc_cmdop[:2] == 'FP' :
            min_gap_size = ( ( float(link_distance) / 2.0 )  ** 2.0 ) * math.pi
        logger.info ( "Minimum gap area is " + str(min_gap_size) )

        return min_gap_size

    except Exception, err:
        logger.critical("Calculate minimum gap area failed: ERROR: %s\n" % str(err))
        raise

def convert_meters_to_decimal_degrees ( logger, distance_m, y) :
    """Function to convert meters to decimal degrees based on position on earth"""
    try :
        logger.info ( "Convert meters to decimal degrees" )
        earth_perimeter = EARTH_PERIMETER * math.cos(math.radians(y))
        distance_dd = ( float(distance_m) / float(earth_perimeter) ) * 360
        return distance_dd
    except Exception, err:
        logger.critical("Convert meters to decimal degrees failed: ERROR: %s\n" % str(err))
        raise

def get_gap_area ( DbConnection, logger,  coord_sys_class_id, link_distance, y ) :
    """Function to calculate minimum area of gaps in hull"""
    try :
        logger.info ( "Calculate minimum gap area using link distance " + str(link_distance) )
        logger.info ( "y = " + str(y) )

        # Now calculate gap area
        if int(coord_sys_class_id) == int( BathyDbLib.GEOGRAPHIC ) :
            earth_perimeter = EARTH_PERIMETER * math.cos(math.radians(y))
            if earth_perimeter == 0 :
                earth_perimeter = MIN_EARTH_PERIMETER
            min_gap_size = ( ( ( ( float(link_distance)/float(earth_perimeter) ) * 360.0 ) / 2.0 ) ** 2.0 ) * math.pi
        if int(coord_sys_class_id) == int( BathyDbLib.PROJECTED ) :
            min_gap_size = ( ( float(link_distance) / 2.0 )  ** 2.0 ) * math.pi
        logger.info ( "Minimum gap area is " + str(min_gap_size) )

        return min_gap_size

    except Exception, err:
        logger.critical("Calculate minimum gap area failed: ERROR: %s\n" % str(err))
        raise

def get_donar_mapper_id ( DbConnection, logger, mapper_id, mapper_column ) :
    """Function to get mapper for donar"""
    try :
        logger.info ( "Get mapper for Donar" )
        attributes = [ mapper_column ]
        values = DbConnection.get_obj_attributes ( BathyDbLib.DONAR_IMPORTER_CLASS_ID, mapper_id, attributes )
        mapper_id  = values[0]
        if not mapper_id :
            mapper_id = 0
        return mapper_id
    except Exception, err:
        logger.critical("Get mapper for Donar failed: ERROR: %s\n" % str(err))
        raise

def gen_xyz_tmp_file ( logger, bathyspace_file, tmp_file, bounds_file, x_vector ) :
    "Function to generate xyz temp file for hull generation"
    try :
        logger.info("Create xyz tmp file " + tmp_file)
        logger.info("Write boundaries to " + bounds_file)
        fAsciiIn = open(bathyspace_file, 'r')
        fAsciiTmp = open(tmp_file,'w')
        fAsciiBounds = open(bounds_file,'w')
        line = fAsciiIn.readline()
        l = line.rstrip().split(BATHYSPACE_SEP)
        x = float(l[0])
        if x < float(0) :
            xmin = x + float(x_vector)
            xmax = x + float(x_vector)
        else :
            xmin = float(l[0])
            xmax = float(l[0])
        ymin = float(l[1])
        ymax = float(l[1])
        zmin = float(str(l[2]))
        zmax = float(str(l[2]))
        fAsciiIn.close()
        fAsciiIn = open(bathyspace_file, 'r')
        i = 0
        for line in fAsciiIn :
            i = i + 1
            l = line.rstrip().split(BATHYSPACE_SEP)
            x = float(l[0])
            if x < float(0) :
                x = x + float(x_vector)
            y = float(l[1])
            z = float(l[2])
            if x < xmin :
                xmin = x
            if x > xmax :
                xmax = x
            if y < ymin :
                ymin = y
            if y > ymax :
                ymax = y
            if z < zmin :
                zmin = z
            if z > zmax :
                zmax = z
            fAsciiTmp.write ( str(x) + " "  + str(y) + " " + str(z) + "\n" )
            if i % BathyDbLib.NR_OF_ROWS_PER_INSERT == 0 :
                logger.info( str(i) + " points processed" )
        # Write boundaries to file
        fAsciiBounds.write( "xmin=" + str(xmin) + "\n")
        fAsciiBounds.write( "xmax=" + str(xmax) + "\n")
        fAsciiBounds.write( "ymin=" + str(ymin) + "\n")
        fAsciiBounds.write( "ymax=" + str(ymax) + "\n")
        fAsciiBounds.write( "zmin=" + str(zmin) + "\n")
        fAsciiBounds.write( "zmax=" + str(zmax) + "\n")
        fAsciiBounds.write( "nrps=" + str(i)    + "\n")
        fAsciiBounds.close()
        fAsciiIn.close()
        logger.info("Total number of points processed: " + str(i))
        return xmin, xmax, ymin, ymax, zmin, zmax
    except Exception, err:
        logger.critical("Create xyz tmp file failed: ERROR: %s\n" % str(err))
        raise

def gen_xyz_tmp_file_geographic( logger, bathyspace_file, tmp_file, bounds_file ) :
    """Function to extract boundary from bathyspace file"""
    try :
        logger.info ( "Generate xyz file from bathyspace file " + str(bathyspace_file) )

        # Scan file for boundaries if boundary file does not exist
        if not os.path.isfile(tmp_file) or not os.path.isfile(bounds_file) or int(os.path.getsize(tmp_file)) == int(0) or int(os.path.getsize(bounds_file)) == int(0) :
            # Create file for hull generation
            xmin, xmax, ymin, ymax, zmin, zmax = gen_xyz_tmp_file ( logger, bathyspace_file, tmp_file, bounds_file, 0 )
            # If for dateline problem
        else :
            # extract boudaries from existing boundary file
            logger.info("Extract boudaries from " + bounds_file)
            fAsciiBounds = open(bounds_file,'r')
            for line in fAsciiBounds:
                l = line.rstrip().split("=")
                if l[0] == "xmin" :
                    xmin = float(l[1])
                if l[0] == "xmax" :
                    xmax = float(l[1])
                if l[0] == "ymin" :
                    ymin = float(l[1])
                if l[0] == "ymax" :
                    ymax = float(l[1])
                if l[0] == "zmin" :
                    zmin = float(l[1])
                if l[0] == "zmax" :
                    zmax = float(l[1])
            fAsciiBounds.close()

        if ( xmax - xmin ) > float(180.0) :
            logger.info("Survey crosses dataline; Recreate xyz tmp file")
            os.remove (tmp_file)
            os.remove (bounds_file)
            xmin, xmax, ymin, ymax, zmin, zmax = gen_xyz_tmp_file ( logger, bathyspace_file, tmp_file, bounds_file, 360 )

        logger.info("Dimensions ASCII file " + str(xmin) + " " + str(xmax) + " , " + str(ymin) + " " + str(ymax) + " , " + str(zmin) + "  " + str(zmax) )

        # Return dimensions
        return xmin, xmax, ymin, ymax, zmin, zmax

    except Exception, err:
        logger.critical("Generate xyz file from bathyspace file failed: ERROR: %s\n" % str(err))
        raise

def get_bathyspace_dimensions ( logger, bathyspace_dir, im_id ) :
    try :
        ascii_file_bounds = get_bounds_file_name ( logger, bathyspace_dir, im_id )
        logger.info("Extract boudaries from " + ascii_file_bounds)
        if os.path.exists ( ascii_file_bounds ) :
            fAsciiBounds = open(ascii_file_bounds,'r')
            for line in fAsciiBounds:
                l = line.rstrip().split("=")
                if l[0] == "xmin" :
                    xmin = l[1]
                if l[0] == "xmax" :
                    xmax = l[1]
                if l[0] == "ymin" :
                    ymin = l[1]
                if l[0] == "ymax" :
                    ymax = l[1]
                if l[0] == "zmin" :
                    zmin = l[1]
                if l[0] == "zmax" :
                    zmax = l[1]
            fAsciiBounds.close()

            # Return dimensions
            return xmin, xmax, ymin, ymax, zmin, zmax

        else :
            logger.critical("No dimensions file found" )
            os.sys.exit(1)

    except Exception, err:
        logger.critical("Get dimensions from bathyspace file failed: ERROR: %s\n" % str(err))
        raise

def get_nr_points_source ( logger, bathyspace_dir, im_id ) :
    try :
        ascii_file_bounds = get_bounds_file_name ( logger, bathyspace_dir, im_id )
        logger.info("Get number of points from " + ascii_file_bounds)
        if os.path.exists ( ascii_file_bounds ) :
            fAsciiBounds = open(ascii_file_bounds,'r')
            for line in fAsciiBounds:
                l = line.rstrip().split("=")
                if l[0] == "nrps" :
                    nrps = l[1]
            fAsciiBounds.close()

            # Return number of points
            return nrps

        else :
            logger.critical("No dimensions file found" )
            os.sys.exit(1)

    except Exception, err:
        logger.critical("Get number of points from bathyspace file failed: ERROR: %s\n" % str(err))
        raise

def get_avg_y_source ( logger, bathyspace_dir, im_id ) :
    try :
        ascii_file_bounds = get_bounds_file_name ( logger, bathyspace_dir, im_id )
        logger.info("Get avg y of points from " + ascii_file_bounds)
        if os.path.exists ( ascii_file_bounds ) :
            fAsciiBounds = open(ascii_file_bounds,'r')
            for line in fAsciiBounds:
                l = line.rstrip().split("=")
                if l[0] == "ymin" :
                    y_min = float(l[1])
                if l[0] == "ymax" :
                    y_max = float(l[1])
            fAsciiBounds.close()
            y_avg = ( y_max + y_min ) / 2.0
            logger.info ( "Average y = " + str(y_avg) )
            return y_avg
        else :
            logger.critical("No dimensions file found" )
            os.sys.exit(1)

    except Exception, err:
        logger.critical("Get avg y from bathyspace file failed: ERROR: %s\n" % str(err))
        raise

def store_bathyspace_dimensions ( logger, DbConnection, object_class_id, bathyspace_dir, im_id, coord_sys_class_id ) :
    try :

        logger.info("Store bathyspace dimensions")
        xmin, xmax, ymin, ymax, zmin, zmax = get_bathyspace_dimensions ( logger, bathyspace_dir, im_id )
        nr = get_nr_points_source ( logger, bathyspace_dir, im_id )

        logger.info("Xmax = " + str(xmax) )
        # Correct x for data line
        if int(coord_sys_class_id) == int(BathyDbLib.GEOGRAPHIC) and float(xmax) > float(180.0) :
            xmax = float(xmax) - float(360.0)
        logger.info("Xmax corrected = " + str(xmax) )

        # Switch xmin and xmax
        if float(xmax) < float (xmin) :
            xtmp = xmax
            xmax = xmin
            xmin = xtmp

        # Now update TL
        if int(object_class_id) == int(BathyDbLib.TL_CLASS_ID) :
            attribute_list = {}
            attribute_list [ BathyDbLib.TL_XMIN_COL ]     = xmin
            attribute_list [ BathyDbLib.TL_XMAX_COL ]     = xmax
            attribute_list [ BathyDbLib.TL_YMIN_COL ]     = ymin
            attribute_list [ BathyDbLib.TL_YMAX_COL ]     = ymax
            attribute_list [ BathyDbLib.TL_ZMIN_COL ]     = zmin
            attribute_list [ BathyDbLib.TL_ZMAX_COL ]     = zmax
            attribute_list [ BathyDbLib.TL_NR_PS_SOURCE ] = nr
            DbConnection.set_obj_attributes ( BathyDbLib.TL_CLASS_ID, im_id, attribute_list )

        # Now update IM
        if int(object_class_id) == int(BathyDbLib.IM_CLASS_ID) :
            attribute_list = {}
            attribute_list [ BathyDbLib.IM_XMIN_COL ]     = xmin
            attribute_list [ BathyDbLib.IM_XMAX_COL ]     = xmax
            attribute_list [ BathyDbLib.IM_YMIN_COL ]     = ymin
            attribute_list [ BathyDbLib.IM_YMAX_COL ]     = ymax
            attribute_list [ BathyDbLib.IM_ZMIN_COL ]     = zmin
            attribute_list [ BathyDbLib.IM_ZMAX_COL ]     = zmax
            attribute_list [ BathyDbLib.IM_NR_PS_SOURCE ] = nr
            DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, im_id, attribute_list )

    except Exception, err:
        logger.critical("Store bathyspace dimensions failed: ERROR: %s\n" % str(err))
        raise


def coordinate_system_correct ( logger, file_in, epsg_code, coord_sys_class_id  ) :
    """Check coordinate system of file"""
    try :

        logger.info ( "Check coordinate system of file " + str(file_in) )
        x, y = get_x_y ( logger, file_in )
        logger.info("Coordinates: x = " + str(x) + ", y = " + str(y))
        logger.info("Coordinate system IM = " + epsg_code )
        # Correct for translated coordinate system when survey crosses dateline
        if ( x > 180 and x < 360 ) :
            x = x - 180
        if ( x >= -180 and x <= 180 ) and ( y >= -90 and y <= 90 ) and ( int(coord_sys_class_id) == int( BathyDbLib.GEOGRAPHIC ) ) :
            coordinate_correct = True
        elif not ( x >= -180 and x <= 180 ) and not ( y >= -90 and y <= 90 ) and ( int(coord_sys_class_id) == int( BathyDbLib.PROJECTED )  ) :
            coordinate_correct = True
        else :
            coordinate_correct = False

        # Return result
        return coordinate_correct

    except Exception, err:
        logger.critical("Check coordinate system of file failed: ERROR: %s\n" % str(err))
        raise

def generate_sdfile_from_db ( DbConnection, logger, im_id, tmp_file, sd_file, cellsize ) :
    """Generate SD file from DB"""
    try :
        logger.info("Generate SD file from DB")

        # Set default values
        factor     = float( DEPTH_MULTIPLICATION_FACTOR )
        epsg_code  = BathyDbLib.EPSG_CODE_DB

        # Remove temporary file
        if os.path.isfile ( tmp_file ) :
            os.remove( tmp_file )

        # Lock IM
        DbConnection.lock_survey( BathyDbLib.IM_CLASS_ID, im_id)

        # Get depths from database and write to file
        # write_xyz_depths_to_file ( self, fOut, survey_id, product_area, cookie_id, im_segment_id ) :
        fOut = open(tmp_file, 'w')
        nr = DbConnection.write_xyz_depths_to_file ( fOut, im_id, None, None, None, SPACE_SEP, False )
        fOut.close()

        # Get IM dimensions from database
        x_min, x_max, y_min, y_max, z_min, z_max = DbConnection.get_im_dimensions ( im_id, epsg_code, factor )

        # Convert cellsize from metres to decimal degrees
        y_avg = ( y_min + y_max ) / 2
        cellsize_new = convert_cell_size ( logger, BathyDbLib.EPSG_DESC_DB, cellsize, y_avg )

        # Generate sd file using cmdop gridder
        BathyExecutablesLib.cmdop_gridder ( DbConnection, logger, tmp_file, sd_file, epsg_code, x_min, x_max, y_min, y_max, z_min, z_max, cellsize_new)

        # Remove temporary file
        if os.path.isfile ( tmp_file ) :
            os.remove( tmp_file )

    except Exception, err:
        logger.critical( "Generate SD file from DB failed:ERROR: %s\n" % str(err))
        raise

def get_nr_of_points_model ( logger, input_file ) :
    """Function to get nr of points of model"""
    try :
        logger.info( "Get nr of points of model")
        fIn = open(input_file,'r')
        for line in fIn:
            if "=" in line:
                l = line.rstrip().split('=')
                if l[0] == "nrps" :
                    l_nr_points = l[1]
        fIn.close()
        return l_nr_points
    except Exception, err:
        logger.critical( "Get nr of points of model failed:ERROR: %s\n" % str(err))
        raise

def get_pp_bounds_file_names ( logger, bathyspace_dir, im_id ) :
    """Function to get file names for post processing boundary files"""
    try :
        ascii_file_tmp    = bathyspace_dir + "\\" + "tmp_pp_" + str(im_id) + BathyExecutablesLib.FILE_EXT_ASCII
        ascii_file_bounds = bathyspace_dir + "\\" + "bounds_pp_" + str(im_id) + BathyExecutablesLib.FILE_EXT_ASCII
        return ascii_file_tmp, ascii_file_bounds
    except Exception, err:
        logger.critical( "Get file names for post processing boundary files failed:ERROR: %s\n" % str(err))
        raise

def get_temp_file_name ( logger, bathyspace_dir, im_id ) :
    """Function to get file names for post processing boundary files"""
    try :
        ascii_file_tmp    = bathyspace_dir + "\\" + "tmp_" + str(im_id) + BathyExecutablesLib.FILE_EXT_ASCII
        return ascii_file_tmp
    except Exception, err:
        logger.critical( "Get file name failed:ERROR: %s\n" % str(err))
        raise

def get_bounds_file_name ( logger, bathyspace_dir, im_id ) :
    """Function to get file names for post processing boundary files"""
    try :
        ascii_file_bounds = bathyspace_dir + "\\" + "bounds_" + str(im_id) + BathyExecutablesLib.FILE_EXT_ASCII
        return  ascii_file_bounds
    except Exception, err:
        logger.critical( "Get file name failed:ERROR: %s\n" % str(err))
        raise

def write_bounds_file ( logger, bathyspace_file, im_id, coord_sys_class_id ) :

    try :
        logger.info ("Write boundaries to file")
        bathyspace_dir  = os.path.dirname(bathyspace_file)
        bounds_file_tmp = get_bounds_file_name ( logger, bathyspace_dir, im_id )
        ascii_file_tmp  = get_temp_file_name ( logger, bathyspace_dir, im_id )
        nr              = 0

        # Get first rows
        fIn  = open(ascii_file_tmp, 'r')
        check_line = fIn.readline()
        l = check_line.rstrip().split()
        xmin = float(l[0])
        xmax = float(l[0])
        ymin = float(l[1])
        ymax = float(l[1])
        zmin = float(str(l[2]))
        zmax = float(str(l[2]))
        fIn.close()

        # Get boundaries and count rows
        fIn       = open(ascii_file_tmp, 'r')
        for line in fIn :
            columns = line.rstrip().split()
            x = float(columns[0])
            if x < xmin :
                xmin = x
            if x > xmax :
                xmax = x
            y = float(columns[1])
            if y < ymin :
                ymin = y
            if y > ymax :
                ymax = y
            z = float(columns[2])
            if z < zmin :
                zmin = z
            if z > zmax :
                zmax = z
            nr = nr + 1
            if nr % BathyDbLib.NR_OF_ROWS_PER_INSERT == 0 :
                logger.info( str(nr) + " points counted" )
        fIn.close()
        logger.info ( str(nr) + " points in bathyspace" )

        # Write to bounds file
        fAsciiBounds = open(bounds_file_tmp,'w')
        fAsciiBounds.write( "xmin=" + str(xmin) + "\n")
        fAsciiBounds.write( "xmax=" + str(xmax) + "\n")
        fAsciiBounds.write( "ymin=" + str(ymin) + "\n")
        fAsciiBounds.write( "ymax=" + str(ymax) + "\n")
        fAsciiBounds.write( "zmin=" + str(zmin) + "\n")
        fAsciiBounds.write( "zmax=" + str(zmax) + "\n")
        fAsciiBounds.write( "nrps=" + str(nr)   + "\n")
        fAsciiBounds.close()

        # If survey crosses dataline, regenerate bathyspace file
        if int(coord_sys_class_id) == int(BathyDbLib.GEOGRAPHIC) and ( xmax - xmin ) > float(180.0) :
            logger.info("Survey crosses dataline; Recreate xyz tmp file")
            os.remove (ascii_file_tmp)
            os.remove (bounds_file_tmp)
            xmin, xmax, ymin, ymax, zmin, zmax = gen_xyz_tmp_file ( logger, bathyspace_file, ascii_file_tmp, bounds_file_tmp, 360 )

    except Exception, err:
        logger.critical( "Write boundaries to file failed:ERROR: %s\n" % str(err))
        raise


def generate_postprocess_sdfile ( DbConnection, logger, im_id, processed_datafile, gridsize, regenerate_hull ):
    """Function to generate hull on postprocessed file"""
    try :
        logger.info("Generate sdfile on postprocessed file " + str(processed_datafile) )

        # Get bathysspace directory
        l_bathyspace_dir = os.path.dirname(processed_datafile)

        # cmdop gridder runs only on xyz file, so extract xyz file from bathyspace ascii
        l_ascii_file_tmp, l_ascii_file_bounds = get_pp_bounds_file_names ( logger, l_bathyspace_dir, im_id )

        #l_ascii_file_tmp    = l_bathyspace_dir + "\\" + "tmp_pp_" + str(im_id) + BathyExecutablesLib.FILE_EXT_ASCII
        #l_ascii_file_bounds = l_bathyspace_dir + "\\" + "bounds_pp_" + str(im_id) + BathyExecutablesLib.FILE_EXT_ASCII

        # Drop tmp file when existing
        if os.path.isfile ( l_ascii_file_tmp ) :
            os.remove( l_ascii_file_tmp )
        if os.path.isfile ( l_ascii_file_bounds ) :
            os.remove( l_ascii_file_bounds )

        # Get boundaries and extract xyz file
        l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax = gen_xyz_tmp_file_geographic( logger, processed_datafile, l_ascii_file_tmp, l_ascii_file_bounds )

        # Get epsg code of database
        l_epsg_code = DbConnection.get_epsg_code_db()

        # First get generate ap area and cell size used for hull generation from database
        l_y             = float(l_ymin) +  ( ( float(l_ymax) - float(l_ymin) ) / float(2.0) )
        l_attributes    = [ BathyDbLib.IM_LINK_DISTANCE_COL, BathyDbLib.IM_COORD_SYS_SRC_COL ]
        l_values        = DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, im_id, l_attributes )
        l_link_distance = l_values[0]
        l_coord_sys_id  = l_values[1]
        if not gridsize :
            logger.info ("Use link distance as gridsize " + str(l_link_distance) )
            gridsize     = convert_cell_size ( logger, BathyDbLib.GEOGRAPHIC, l_link_distance, l_y )
        else:
            logger.info ("Use gridsize " + str(gridsize) )
            l_coord_sys_class_id = get_coord_sys_class ( DbConnection, logger, l_coord_sys_id )
            if int(l_coord_sys_class_id) <> int( BathyDbLib.GEOGRAPHIC ) :
                gridsize        = convert_cell_size ( logger, BathyDbLib.GEOGRAPHIC, gridsize, l_y )
        
        logger.info ("Use gridsize in decimal degrees = " + str(gridsize) )
        #l_min_gap_area  = get_minimum_gap_area ( logger, l_cell_size )
        #logger.info ("Use gap area " + str(l_min_gap_area) )

        # Check for empty gridsize, if no resampling, use gridsize used for hull generation
        #gridsize = l_cell_size
#        else :
#            if float(gridsize) > float(DEGREE_TO_METER_SWITCH) :
#                # Assume gridsize is in meters so convert to decimal degrees
#                gridsize = convert_cell_size ( logger, BathyDbLib.GEOGRAPHIC, gridsize, l_y )

        # Generate new SD file
        l_sd_file   = l_bathyspace_dir + "\\" + "tmp_pp_" + str(im_id) + BathyExecutablesLib.FILE_EXT_SD
        gridsize    =  float(gridsize) * float(1.1)
        logger.info ("Generate SD file " + str(l_sd_file) + " with gridsize " + str(gridsize) )
        BathyExecutablesLib.cmdop_gridder ( DbConnection, logger, l_ascii_file_tmp, l_sd_file, l_epsg_code, l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax, gridsize )

        # Store location of temporary SD file and BLOB in database (IM_SDFILE_NAME_COL)
        logger.info ("Storing SD file in database")
        l_blob_file_name = "BLOB" + str(im_id) + BathyExecutablesLib.FILE_EXT_SD
        l_attribute_list = {}
        l_attribute_list [  BathyDbLib.IM_SDFILE_NAME_COL ]    = l_sd_file
        DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, im_id, l_attribute_list )
        DbConnection.set_blob ( BathyDbLib.IM_CLASS_ID, im_id, BathyDbLib.IM_SDBLOB_COL, l_sd_file, l_blob_file_name )

        # Now start hull generation based on SD file
        if regenerate_hull == "T" :
            logger.info ("Generate hull")
            l_hull_file_tmp = l_bathyspace_dir + "\\" + "hull_pp_" + str(im_id) + BathyExecutablesLib.FILE_EXT_TMP
            l_option = '-dtm'
            BathyExecutablesLib.cmdop_createcoveragevectors ( DbConnection, logger, l_option, l_sd_file, l_hull_file_tmp )
            # Check if fgenerated file contains coordinates
            if os.path.getsize( l_hull_file_tmp ) :
                # Finally store hull in database
                logger.info ("Store hull in database")
                l_hull = BathyExecutablesLib.ogr_convert_hull_to_wkt ( DbConnection, logger, l_hull_file_tmp )
                DbConnection.insert_im_hull ( BathyDbLib.IM_CLASS_ID, im_id, l_hull, l_epsg_code, l_link_distance )
            else :
                logger.critical ("Hull could not be generated")
                raise

    except Exception, err:
        logger.critical( "Generate hull on postprocessed file failed: ERROR: %s\n" % str(err))
        raise


def gen_bathyspace_for_tl_im ( DbConnection, logger, im_id, file_name) :
    """Function to generate bathyspace for trackline IM"""
    try :
        logger.info("Generate bathyspace for trackline IM " + str(id) )

        # Write trackline to bathyspace
        write_tracklines_to_file ( DbConnection, logger, im_id, file_name, BATHYSPACE_SEP )

    except Exception, err:
        logger.critical( "Generate bathyspace for trackline IM: ERROR: %s\n" % str(err))
        raise

def import_tl ( DbConnection, logger, ParameterList, tl_id, full_file_name, im_format_id ) :
    """Function to import individual trackline"""
    try :
        logger.info("Import trackline " + str(id) )
        
        # Get parameters from list
        task_id               = ParameterList[ TASKID ]
        coord_sys_id          = ParameterList[ PARAMETER_COORD_SYS ]
        etrsyear              = ParameterList[ PARAMETER_ETRSYEAR ]
        vert_ref_id           = ParameterList[ PARAMETER_VERT_REF ] 

        # Update TL attributes
        logger.info ( 'Write trackline attributes to database')
        attribute_list = {}
        attribute_list [ BathyDbLib.TL_EPSG_ID_IN ]       = coord_sys_id
        attribute_list [ BathyDbLib.TL_DATA_FILE_COL ]    = ParameterList[ PARAMETER_INPUT_FILE ]
        attribute_list [ BathyDbLib.TL_IM_FORMAT ]        = im_format_id
        attribute_list [ BathyDbLib.TL_SEP_MODEL_COL ]    = vert_ref_id
        attribute_list [ BathyDbLib.TL_ETRSYEAR_COL ]     = etrsyear
        attribute_list [ BathyDbLib.TL_INPUT_FORMAT_COL ] = BathyDbLib.TLFORMAT_ASCII
        DbConnection.set_obj_attributes ( BathyDbLib.TL_CLASS_ID, tl_id, attribute_list )

        # Update workflowstep to archived
        DbConnection.update_workflow_step ( BathyDbLib.PROCESS_IMP_TL, BathyDbLib.TL_CLASS_ID, tl_id )

        # Get parameters for Makegrid
        logger.info ( 'Get geodetic parameters for conversion' )
        epsg_code_in   = get_epsg_code ( DbConnection, logger, coord_sys_id )
        wkt_in         = DbConnection.get_wkt_coord_sys_id ( l_coord_sys_id )
        epsg_code_out  = DbConnection.get_epsg_code_db ()
        wkt_out        = DbConnection.get_wkt_epsg_code ( epsg_code_out )
        ver_dat_in, ver_dat_out, offset, m_factor = get_separation_model ( DbConnection, logger, vert_ref_id )

        # First check file to see if it already has correct separator, if not separator is added
        gen_bathyspace_files ( logger, full_file_name )

        # Run Makegrid for geodetic transformations
        logger.info ( 'Apply coordinate transformation and apply separation model' )
        working_dir = ParameterList [ TEMPDIR ]
        l_sep_model_name, l_direction, l_gridsize, l_algorithm_id = BathyExecutablesLib.makegrid_separation_model_file ( DbConnection, logger, working_dir, vert_ref_id,None, None )
        output_file = BathyExecutablesLib.makegrid_geo_conv (logger, full_file_name, working_dir, epsg_code_in, epsg_code_out, ver_dat_in, ver_dat_out, offset, m_factor, etrsyear, ";", ";", wkt_in, wkt_out, l_sep_model_name, l_direction, l_gridsize, l_algorithm_id )
        logger.info ('File to import into database: ' + str(output_file) )

        # Import trackline into database
        logger.info ( 'Write trackline into database' )
        #im_format_id = BathyDbLib.IM_FRMT_DONAR
        #im_format_id = BathyDbLib.IM_FRMT_XYZ
        write_depths_to_database ( DbConnection, logger, output_file, im_format_id )

        # Import trackline into database
        logger.info ( 'Create spatial index on database' )
        create_spatial_index_on_database ( DbConnection, logger, BathyDbLib.TL_CLASS_ID, tl_id, task_id  )

    except Exception, err:
        logger.critical( "Write tracklines from DB to file failed: ERROR: %s\n" % str(err) )
        raise

def import_im ( DbConnection, logger, ParameterList, im_id, full_file_name ) :
    """Function to import individual trackline"""
    try :
        logger.info("Import IM " + str(id) )

        # Set bathyspace type and IM format
        bathyspace_type = BathyDbLib.BATHYSPACE_ASCII
        im_format_id    = BathyDbLib.IM_FRMT_DONAR

        # Get parameters from list
        coord_sys_id    = ParameterList[ PARAMETER_COORD_SYS ]
        etrsyear        = ParameterList[ PARAMETER_ETRSYEAR ]
        vert_ref_id     = ParameterList[ PARAMETER_VERT_REF ]

        # Create bathyspace directory
        bathyspace_dir  = create_bathyspace_dir ( logger, im_id )
        bathyspace_file = bathyspace_dir + "\\" + "survey_" + str(im_id) + BathyExecutablesLib.FILE_EXT_ASCII

        # Add separator and extract dimensions
        logger.info ("Add separator to file and extract dimensions")
        coord_sys_class_id = get_coord_sys_class ( DbConnection, logger, coord_sys_id )
        logger.info ("Coordinate system class is " + str(coord_sys_class_id) )
        gen_bathyspace_files ( logger, full_file_name, im_id, coord_sys_class_id )

        # Extract and store boundaries
        logger.info ("Store bathyspace dimensions")
        BathyToolsLib.store_bathyspace_dimensions ( logger, DbConnection, BathyDbLib.IM_CLASS_ID, full_file_name, im_id, coord_sys_class_id )

        # Copy file to bathyspace directory
        logger.info("Copy " + str(full_file_name) + " to " + str(bathyspace_file) )
        shutil.copyfile(full_file_name, bathyspace_file)

        # Store IM Bathyspace attributes
        logger.info("Store IM bathyspace parameters")
        attribute_list = {}
        attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = bathyspace_file
        attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = bathyspace_type
        attribute_list [ BathyDbLib.IM_IM_FORMAT_COL ]      = im_format_id
        attribute_list [ BathyDbLib.IM_SOURCE_FILES_COL ]   = ParameterList[ PARAMETER_INPUT_FILE ]
        attribute_list [ BathyDbLib.IM_INPUT_FORMAT_COL ]   = ParameterList[ PARAMETER_FILE_FORMAT ]
        attribute_list [ BathyDbLib.IM_COORD_SYS_SRC_COL ]  = coord_sys_id
        attribute_list [ BathyDbLib.IM_SEP_MODEL_COL ]      = vert_ref_id
        attribute_list [ BathyDbLib.IM_ETRSYEAR_COL ]       = etrsyear
        DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, im_id, attribute_list )

        # Update workflowstep
        DbConnection.update_workflow_step ( ParameterList[ PARAMETER_PROCESS_ID ], BathyDbLib.IM_CLASS_ID,im_id )

    except Exception, err:
        logger.critical( "Write tracklines from DB to file failed: ERROR: %s\n" % str(err) )
        raise

def group_tracklines_in_im ( ParameterList, DbConnection, logger, im_id, trackline_list) :
    """Function to group tracklines in IM"""
    try :
        logger.info( "Group tracklines in IM")

        # Call database procedure
        DbConnection.add_trackline_to_im ( im_id, trackline_list )

        # Set bathyspace type
        bathyspace_type = BathyDbLib.BATHYSPACE_ASCII

        # Create bathyspace directory
        bathyspace_dir  = create_bathyspace_dir (logger, im_id )
        bathyspace_file = bathyspace_dir + "\\" + "survey_" + str(im_id) + BathyExecutablesLib.FILE_EXT_ASCII

        # Generate Bathyspace for IM
        gen_bathyspace_for_tl_im (DbConnection, logger, im_id, bathyspace_file )

        # Store IM Bathyspace attributes
        logger.info("Store IM bathyspace parameters")
        # EPSG is always wgs84 (epsp_code database)
        coord_sys_id = DbConnection.get_coord_sys_id_db()
        # IM format is always XYZ
        im_format = BathyDbLib.IM_FRMT_XYZ
        # Separation model unknown
        sep_model_id = BathyDbLib.SEP_MODEL_UNKONWN
        # Surveytype = trackline
        survey_type = BathyDbLib.TRACKLINE_SURVEYTYPE_ID
        attribute_list = {}
        attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = bathyspace_file
        attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = bathyspace_type
        attribute_list [ BathyDbLib.IM_IM_FORMAT_COL ]      = im_format
        attribute_list [ BathyDbLib.IM_INPUT_FORMAT_COL ]   = ParameterList[ PARAMETER_FILE_FORMAT ]
        attribute_list [ BathyDbLib.IM_COORD_SYS_SRC_COL ]  = coord_sys_id
        attribute_list [ BathyDbLib.IM_SEP_MODEL_COL ]      = sep_model_id
        attribute_list [ BathyDbLib.IM_STARTDATE_COL ]      = ParameterList[ PARAMETER_STARTDATE ]
        attribute_list [ BathyDbLib.IM_SOURCE_FILES_COL ]   = trackline_list
        attribute_list [ BathyDbLib.IM_SURVEYTYPE_COL ]     = survey_type
        DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, im_id, attribute_list )

        # Update workflowstep
        DbConnection.update_workflow_step ( ParameterList[ PARAMETER_PROCESS_ID ], BathyDbLib.IM_CLASS_ID, ParameterList[ PARAMETER_IM_ID ] )

    except Exception, err:
        logger.critical( "Group tracklines in IM failed: ERROR: %s\n" % str(err) )
        raise

def write_tracklines_to_file ( DbConnection, logger, im_id, tmp_file, separator ) :
    """Function write tracklines from DB to file"""
    try :
        logger.info("Write tracklines from DB to file")

        # Get trackline ID's from DB
        tr_list            = DbConnection.get_trackline_list ( im_id )
        
        # Delete file when exists
        if os.path.isfile (tmp_file ) :
            logger.info("Delete temporary file " + tmp_file )
            os.remove( tmp_file)

        # Loop through IM's, get points from DB and write to file
        logger.info("Open temporary file " + tmp_file )
        tr_file = open(tmp_file, 'w')
        nr = 0
        for tr_id in tr_list :
            logger.info("Add trackline " + str(tr_id) + " to file")
            nr = nr + DbConnection.write_xyz_depths_to_file ( tr_file, tr_id, None, None, None, separator, False  )
            logger.info( str(nr) + " points written to file" )
        tr_file.close()

    except Exception, err:
        logger.critical( "Write tracklines from DB to file failed: ERROR: %s\n" % str(err))
        raise

def remove_uncertainty_attribute ( logger, input_file ) :
    """Function to add separator to ascii file"""
    try :
        logger.info("Remove uncertainty attribute from file " + str(input_file) )

        separator     = BATHYSPACE_SEP
        tmp_file      = os.path.dirname( input_file ) + "\\tmp.xyz"

        # Remove tmpfile
        if os.path.isfile ( tmp_file ) :
            os.remove( tmp_file )

        # Process file to remove uncertainty
        fIn  = open(input_file, 'r')
        fOut = open(tmp_file, 'w')
        for line in fIn :
            columns     = line.rstrip().split()
            output_line =  str(columns[0]) + separator + str(columns[1]) + separator + str(columns[2]) 
            fOut.write ( output_line + "\n" )
        fIn.close()
        fOut.close()

        # Copy tmpfile to unload file
        if os.path.isfile ( input_file ) :
            os.remove( input_file )
            shutil.copyfile ( tmp_file, input_file )
            os.remove( tmp_file )

    except Exception, err:
        logger.critical( "Remove uncertainty attribute from file failed: ERROR: %s\n" % str(err))
        raise

def gen_bathyspace_files ( logger, input_file, im_id, coord_sys_class_id ) :
    """Function to add separator to ascii file"""
    # Two files are written:
    # Bathyspace file : <x>;<y>;<z>; + attributes (3 or more columns separared by ;)
    # tmp file for hull generation : <x> <y> <z>  (3 columns separated by <space>)
    try :
        logger.info("Generate bathyspace file " + str(input_file) )
        
        bathyspace_dir  = os.path.dirname( input_file )
        bounds_file_tmp = get_bounds_file_name ( logger, bathyspace_dir, im_id )
        ascii_file_tmp  = get_temp_file_name ( logger, bathyspace_dir, im_id )
        output_line     = ""
        tmp_output_line = ""
        nr              = 0
        tmp_file        = bathyspace_dir + "\\tmp.xyz"

        # First check file to see if it already has correct separator
        # And extract initial xyz
        fIn  = open(input_file, 'r')
        check_line = fIn.readline()
        if len(check_line.rstrip().split(BATHYSPACE_SEP)) > 2 :
            l = check_line.rstrip().split(BATHYSPACE_SEP)
            xmin = float(l[0])
            xmax = float(l[0])
            ymin = float(l[1])
            ymax = float(l[1])
            zmin = float(str(l[2]))
            zmax = float(str(l[2]))
            file_separator  = BATHYSPACE_SEP
        else :
            l = check_line.rstrip().split()
            xmin = float(l[0])
            xmax = float(l[0])
            ymin = float(l[1])
            ymax = float(l[1])
            zmin = float(str(l[2]))
            zmax = float(str(l[2]))
            file_separator  = ''
        fIn.close()

        # Add separator to file
        logger.debug("Process file to add separator")
        
        if file_separator <> BATHYSPACE_SEP :
            fIn       = open(input_file, 'r')
            if os.path.isfile ( tmp_file ) :
                os.remove( tmp_file )
            fOut      = open(tmp_file, 'w')
            for line in fIn :
                columns = line.rstrip().split()
                for i in range(len(columns)) :
                    output_line = output_line + columns[i] + BATHYSPACE_SEP
                fOut.write ( output_line + "\n" )
                output_line = ""
                nr = nr + 1
                if nr % BathyDbLib.NR_OF_ROWS_PER_INSERT == 0 :
                    logger.info( str(nr) + " points processed" )
            fOut.close()
            fIn.close()
            logger.info( "Bathyspace has " + str(nr) + " points" )

            # Copy tmpfile to unload file
            if os.path.isfile ( input_file ) :
                os.remove( input_file )
            shutil.copyfile ( tmp_file, input_file )
            os.remove( tmp_file )
        
        # Set bathyspace separator ;        
        file_separator = BATHYSPACE_SEP
        nr             = 0

        # Write tmp_file for files that have already bathyspace separator
        logger.info("Extract bathyspace dimensions")

        if file_separator == BATHYSPACE_SEP :
            fIn       = open(input_file, 'r')
            if os.path.isfile ( ascii_file_tmp ) :
                os.remove( ascii_file_tmp )
            fAsciiTmp = open(ascii_file_tmp, 'w')
            for line in fIn :
                columns = line.rstrip().split( BATHYSPACE_SEP )
                x = float(columns[0])
                if x < xmin :
                    xmin = x
                if x > xmax :
                    xmax = x
                y = float(columns[1])
                if y < ymin :
                    ymin = y
                if y > ymax :
                    ymax = y
                z = float(columns[2])
                if z < zmin :
                    zmin = z
                if z > zmax :
                    zmax = z
                tmp_output_line = tmp_output_line + " " + str(x) + " " + str(y) + " " + str(z)
                fAsciiTmp.write ( tmp_output_line + "\n" )
                tmp_output_line = ""
                nr = nr + 1
                if nr % BathyDbLib.NR_OF_ROWS_PER_INSERT == 0 :
                    logger.info( str(nr) + " points processed" )
            fAsciiTmp.close()
            fIn.close()
            logger.info( str(nr) + " points processed" )

        # Write bounds file
        if os.path.isfile ( bounds_file_tmp ) :
            os.remove( bounds_file_tmp )
        fAsciiBounds = open(bounds_file_tmp,'w')
        fAsciiBounds.write( "xmin=" + str(xmin) + "\n")
        fAsciiBounds.write( "xmax=" + str(xmax) + "\n")
        fAsciiBounds.write( "ymin=" + str(ymin) + "\n")
        fAsciiBounds.write( "ymax=" + str(ymax) + "\n")
        fAsciiBounds.write( "zmin=" + str(zmin) + "\n")
        fAsciiBounds.write( "zmax=" + str(zmax) + "\n")
        fAsciiBounds.write( "nrps=" + str(nr)   + "\n")
        fAsciiBounds.close()

        # If survey crosses dataline, regenerate bathyspace file
        if int(coord_sys_class_id) == int(BathyDbLib.GEOGRAPHIC) and ( xmax - xmin ) > float(180.0) :
            logger.info("Survey crosses dataline; Recreate xyz tmp file")
            os.remove (ascii_file_tmp)
            os.remove (bounds_file_tmp)
            xmin, xmax, ymin, ymax, zmin, zmax = gen_xyz_tmp_file ( logger, input_file, ascii_file_tmp, bounds_file_tmp, 360 )

    except Exception, err:
        logger.critical( "Generate bathyspace files failed: ERROR: %s\n" % str(err))
        raise

def scan_file_for_dimensions ( logger, file_in, separator ) :
    """"Function to scan file for xyz dimensions"""
    try :
        logger.info( "Scan file for xyz dimensions" )

        # Determine start xyz min/max
        fIn       = open(file_in, 'r')
        check_line = fIn.readline()
        l = check_line.rstrip().split( separator )
        xmin = float(l[0])
        xmax = float(l[0])
        ymin = float(l[1])
        ymax = float(l[1])
        zmin = float(str(l[2]))
        zmax = float(str(l[2]))
        fIn.close()

        # Scan file for xyz min/max
        fIn       = open(file_in, 'r')
        for line in fIn :
            columns = line.rstrip().split( separator )
            x = float(columns[0])
            if x < xmin :
                xmin = x
            if x > xmax :
                xmax = x
            y = float(columns[1])
            if y < ymin :
                ymin = y
            if y > ymax :
                ymax = y
            z = float(columns[2])
            if z < zmin :
                zmin = z
            if z > zmax :
                zmax = z
        fIn.close()

        #Return values
        return xmin, xmax, ymin, ymax, zmin, zmax

    except Exception, err:
        logger.critical( "Scan file for xyz dimensions failed: ERROR: %s\n" % str(err))
        raise


def unload_sdfile ( DbConnection, logger, im_id, bathyspace_file, unload_file ) :
    """Function to unload sdfile into xyz file, adding separator for bathyspace """
    try :
        logger.info("Unload SD file")
        BathyExecutablesLib.cmdop_exportsurface ( DbConnection, logger, bathyspace_file, unload_file ) 

        # Now add separator to file
        gen_bathyspace_files ( logger, unload_file )

    except Exception, err:
        logger.critical( "Unload SD file failed: ERROR: %s\n" % str(err))
        raise

def create_bathyspace_dir ( logger, im_id ) :
    # Function to create bathyspace dir
    try :
        logger.info("Create bathyspace directory" )

        # Get path from registry
        bathyspace_path = get_key_value_from_registry( REGISTRY_KEY_BATHYSPACE )
        logger.info("Bathyspace path from registry is " + str(bathyspace_path) )

        # Atlis directory
        working_directory = bathyspace_path + "\\SENSData"
        if not os.path.isdir( working_directory ) :
            os.mkdir( working_directory )

        # Create bathyspace dir; If exists then first remove directory with files
        bathyspace_dir = str( working_directory + "\\Bathyspace" + "_" + str(im_id) )
        logger.info("Bathyspace directory is " + bathyspace_dir )
        if os.path.isdir( bathyspace_dir ) :
            shutil.rmtree( bathyspace_dir )
        
        # Now make directory
        logger.info("Make directory and set to r/w")
        os.mkdir( bathyspace_dir )
        # Set directory to r/w
        os.chmod( bathyspace_dir, stat.S_IWUSR)

        # Return directory name
        return str( bathyspace_dir )

    except Exception, err:
        logger.critical("Creating bathyspace directory failed: ERROR: %s\n" % str(err))
        raise

def drop_bathyspace_dir ( logger, bathyspace_dir ) :
    # Drop bathyspace directory
    try :
        logger.info("Drop bathyspace directory " + str(bathyspace_dir))
        if os.path.isdir( bathyspace_dir ) :
            shutil.rmtree( bathyspace_dir )
    except Exception, err:
        logger.warning("Drop bathyspace directory failed: ERROR: %s\n" % str(err))

def check_bathyspace_dir ( logger, im_id, bathyspace_file ) :
    # Create bathyspace directory if it does not exist
    try :
        logger.info("Check existence of bathyspace directory")

        # Get bathyspace directory
        if bathyspace_file :
            bathyspace_dir = os.path.dirname(l_bathyspace_file)
        else :
            bathyspace_dir = create_bathyspace_dir( logger, im_id )
        logger.info("Bathyspace directory is " + str(bathyspace_dir) )

        # Return directory
        return bathyspace_dir

    except Exception, err:
        logger.critical("Check existence of bathyspace directory failed: ERROR: %s\n" % str(err))
        raise

def convert_to_decimal_degs ( logger, i1, i2, separator ) :
    # Convert lat, long to decimal degrees
    try :
        # 62;00;16.79034 N,  5;28;00.00711 E,0.000
        # 40 + (20 * 1/60) + (50 * 1/60 * 1/60)
        # First remove N/E based on <whitespace>
        a    = i1.rstrip().split()[0]
        b    = i2.rstrip().split()[0]
        # Now split into degrees, minutes, seconds
        c    = a.rstrip().split( separator )
        d    = b.rstrip().split( separator )
        # First coordinate
        ordinate_1 = float(c[0]) + ( float(c[1]) * float(1.0/60.0) ) + ( float(c[2]) * float(1.0/60.0) * float(1.0/60.0) )
        ordinate_2 = float(d[0]) + ( float(d[1]) * float(1.0/60.0) ) + ( float(d[2]) * float(1.0/60.0) * float(1.0/60.0) )

        # return ordinates
        return ordinate_1, ordinate_2

    except Exception, err:
        logger.error("Conversion to decimal degrees failed: ERROR: %s\n" % str(err))
        raise

def get_coordinate_desc ( DbConnection, logger, epsg_id_db ) :
    # Get coordinate system description from DB
    try :
        logger.info("Get coordinate system description from DB")
        attributes = [ BathyDbLib.EPSG_CMDOP_COL, BathyDbLib.EPSG_CODE_COL ]
        values     = DbConnection.get_obj_attributes ( BathyDbLib.EPSG_CLASS_ID, epsg_id_db, attributes )
        icoordsys  = values[0]
        epsg_code  = values[1]

        # Return cmdop description and epsg_code
        return icoordsys, epsg_code

    except Exception, err:
        logger.critical("Get coordinate system description from DB failed: ERROR: %s\n" % str(err))
        raise

def write_metadata_from_esri_ascii_grid ( logger, grid_file_in, bathyspace_dir, im_id  ) :
    # Function to extract boundaries from esri ascii grid and store in file
    try:
        logger.info("Write metadata from Esri ascii grid")
        esri_asc_grid_file = open (grid_file_in, 'r')
        line_nr = 0
        grid_paramter_list = {}
        cellsize      = None
        no_data_value = None
        nocols        = None
        norows        = None
        xllcenter     = None
        xllcorner     = None
        yllcenter     = None
        yllcorner     = None
        xdim          = None
        ydim          = None
        while line_nr < 7 :
            line = esri_asc_grid_file.readline()
            key_value = line.rstrip().split()
            if str.upper(key_value[0]) == str.upper('cellsize') :
                cellsize = float(key_value[1])
                grid_paramter_list [ BathyDbLib.IM_GRID_CELL_SIZE_COL ] = cellsize
                logger.info("CELLSIZE = " + str(cellsize) )
            if str.upper(key_value[0]) == str.upper("NODATA_value") :
                no_data_value = key_value[1]
                grid_paramter_list [ BathyDbLib.IM_GRID_NODATA_VALUE ] = no_data_value
                logger.info("NODATA_VALUE = " + str(no_data_value) )
            if str.upper(key_value[0]) == str.upper("NCOLS") :
                nocols = float(key_value[1])
                logger.info("NCOLS = " + str(nocols) )
                grid_paramter_list [ BathyDbLib.IM_GRID_NCOLS ] = nocols
            if str.upper(key_value[0]) == str.upper("NROWS") :
                norows = float(key_value[1])
                logger.info("NROWS = " + str(norows) )
                grid_paramter_list [ BathyDbLib.IM_GRID_NROWS ] = norows
            if str.upper(key_value[0]) == str.upper("XLLCENTER") :
                xllcenter = float(key_value[1])
                logger.info("XLLCENTER = " + str(xllcenter) )
                grid_paramter_list [ BathyDbLib.IM_GRID_XLLCENTER ] = xllcenter
            if str.upper(key_value[0]) == str.upper("XLLCORNER") :
                xllcorner = float(key_value[1])
                logger.info("XLLCORNER = " + str(xllcorner) )
                grid_paramter_list [ BathyDbLib.IM_GRID_XLLCORNER ] = xllcorner
            if str.upper(key_value[0]) == str.upper("YLLCENTER") :
                yllcenter = float(key_value[1])
                logger.info("YLLCENTER = " + str(yllcenter) )
                grid_paramter_list [ BathyDbLib.IM_GRID_YLLCENTER ] = yllcenter
            if str.upper(key_value[0]) == str.upper("YLLCORNER") :
                yllcorner = float(key_value[1])
                logger.info("YLLCORNER = " + str(yllcorner) )
                grid_paramter_list [ BathyDbLib.IM_GRID_YLLCORNER ] = yllcorner
            if str.upper(key_value[0]) == str.upper("XDIM") :
                xdim = float(key_value[1])
                logger.info("XDIM = " + str(xdim) )
                grid_paramter_list [ BathyDbLib.IM_GRID_XDIM ] = xdim
            if str.upper(key_value[0]) == str.upper("YDIM") :
                ydim = float(key_value[1])
                logger.info("YDIM = " + str(ydim) )
                grid_paramter_list [ BathyDbLib.IM_GRID_YDIM ] = ydim
            line_nr = line_nr + 1
        esri_asc_grid_file.close()

        # Check if all parameters have a value, if not raise error and exit
        if cellsize == None and xdim == None and ydim == None :
            logger.critical("Cell dimension missing")
            raise
        if no_data_value == None :
            logger.critical("Nodata_value missing")
            raise
        if nocols == None :
            logger.critical("Ncolls missing")
            raise
        if norows == None  :
            logger.critical("Nrows missing")
            raise
        if xllcenter == None and xllcorner == None  :
            logger.critical("Xll missing")
            raise
        if yllcenter == None and yllcorner == None  :
            logger.critical("Yll missing")
            raise

        # Write boundaries to file
#        ascii_file_bounds = bathyspace_dir + "\\" + "bounds_" + str(im_id) + BathyExecutablesLib.FILE_EXT_ASCII
#        fAsciiBounds = open(ascii_file_bounds,'w')
#        if xllcenter :
#            fAsciiBounds.write( "xmin=" + str(  xllcenter - ( cellsize/2 ) ) + "\n")
#            fAsciiBounds.write( "xmax=" + str(  xllcenter - ( cellsize/2 ) + ( nocols* cellsize ) ) + "\n")
#        if yllcenter :
#            fAsciiBounds.write( "ymin=" + str(  yllcenter - ( cellsize/2 ) ) + "\n")
#            fAsciiBounds.write( "ymax=" + str(  yllcenter - ( cellsize/2 ) + ( norows* cellsize ) ) + "\n")
#        if xllcorner :
#            fAsciiBounds.write( "xmin=" + str(  xllcorner ) + "\n")
#            fAsciiBounds.write( "xmax=" + str(  xllcorner + ( nocols* cellsize ) ) + "\n")
#        if yllcorner :
#            fAsciiBounds.write( "ymin=" + str(  yllcorner  ) + "\n")
#            fAsciiBounds.write( "ymax=" + str(  yllcorner + ( norows* cellsize ) ) + "\n")
#        fAsciiBounds.write( "zmin=" + "\n")
#        fAsciiBounds.write( "zmax=" + "\n")
#        fAsciiBounds.close()

        # Return the cellsize
        return grid_paramter_list

    except Exception, err:
        logger.critical("Write metadata from Esri ascii grid failed: ERROR: %s\n" % str(err))
        raise

def process_imp_ascii_no_attr_line ( logger, line, attribute_order_id, separator, separator_id, multiplication_factor) :
    # Function to process import ascii line without additional attributes
    try :
        # First split line
        l = line.rstrip().split( separator )
        # Only write lines with a depth (3 columns)
        if int(attribute_order_id) == int(BathyDbLib.ATTR_ORDER_XYZ_ID) :
            l_z = str( multiplication_factor * float(l[2]) )
            output_line = l[0] + " " + l[1] + " " + l_z + "\n"
        if int(attribute_order_id) == int(BathyDbLib.ATTR_ORDER_YXZ_ID) :
            l_z = str( multiplication_factor * float(l[2]) )
            output_line = l[1] + " " + l[0] + " " + l_z + "\n"
        if int(attribute_order_id) == int(BathyDbLib.ATTR_ORDER_DMSNE_ID) :
            if int(separator_id) == int(BathyDbLib.SEP_WHITESPACE_ID) :
                n, e = convert_to_decimal_degs ( l[0], l[2], ";" )
                l_z = str( multiplication_factor * float(l[4]) )
                output_line =  str(e) + " " + str(n) + " " + l_z + "\n"
            elif int(separator_id) == int(BathyDbLib.SEP_SEMICOLON_ID) :
                n_in = str(l[0]) + ";" + str(l[1]) + ";" + str(l[2])
                e_in = str(l[3]) + ";" + str(l[4]) + ";" + str(l[5])
                n, e = convert_to_decimal_degs ( n_in, e_in, ";" )
                l_z = str( multiplication_factor * float(l[6]) )
                output_line = str(e) + " " + str(n) + " " + l_z + "\n"
            else :
                n, e = convert_to_decimal_degs ( l[0], l[1], ";" )
                l_z = str( multiplication_factor * float(l[2]) )
                output_line =  str(e) + " " + str(n) + " " + l_z + "\n"
        if int(attribute_order_id) == int(BathyDbLib.ATTR_ORDER_DMSEN_ID) :
            if int(separator_id) == int(BathyDbLib.SEP_WHITESPACE_ID) :
                e, n = convert_to_decimal_degs ( l[0], l[2], ";" )
                l_z = str( multiplication_factor * float(l[4]) )
                output_line = str(e) + " " + str(n) + " " + l_z + "\n"
            elif int(separator_id) == int(BathyDbLib.SEP_SEMICOLON_ID) :
                e_in = str(l[0]) + ";" + str(l[1]) + ";" + str(l[2])
                n_in = str(l[3]) + ";" + str(l[4]) + ";" + str(l[5])
                e, n = convert_to_decimal_degs ( n_in, e_in, ";" )
                l_z = str( multiplication_factor * float(l[6]) )
                output_line = str(e) + " " + str(n) + " " + l_z + "\n"
            else :
                e, n = convert_to_decimal_degs ( l[0], l[1], ";" )
                l_z = str( multiplication_factor * float(l[2]) )
                output_line =  str(e) + " " + str(n) + " " + l_z + "\n"
        
        # Return formatted output line
        return output_line

    except Exception, err:
        logger.error("Processing line " + str(line) + " failed: ERROR: %s\n" % str(err))
        return None

def process_imp_ascii_unc_attr_line ( logger, line, attribute_order_id, separator, separator_id, multiplication_factor) :
    # Function to process import ascii line with additional uncertainty attribute
    try :
        # First split line
        l = line.rstrip().split( separator )
        # Only write lines with a depth and uncertainty (4 columns)
        if int(attribute_order_id) == int(BathyDbLib.ATTR_ORDER_XYZ_ID) :
            l_z = str( multiplication_factor * float(l[2]) )
            output_line = l[0] + " " + l[1] + " " + l_z + " " + l[3] + "\n"
        if int(attribute_order_id) == int(BathyDbLib.ATTR_ORDER_YXZ_ID) :
            l_z = str( multiplication_factor * float(l[2]) )
            output_line = l[1] + " " + l[0] + " " + l_z + " " + l[3] + "\n"
        if int(attribute_order_id) == int(BathyDbLib.ATTR_ORDER_DMSNE_ID) :
            if int(separator_id) == int(BathyDbLib.SEP_WHITESPACE_ID) :
                n, e = convert_to_decimal_degs (logger, l[0], l[2], ";" )
                l_z = str( multiplication_factor * float(l[4]) )
                output_line =  str(e) + " " + str(n) + " " + l_z + " " + l[5] + "\n"
            elif int(separator_id) == int(BathyDbLib.SEP_SEMICOLON_ID) :
                n_in = str(l[0]) + ";" + str(l[1]) + ";" + str(l[2])
                e_in = str(l[3]) + ";" + str(l[4]) + ";" + str(l[5])
                n, e = convert_to_decimal_degs (logger, n_in, e_in, ";" )
                l_z = str( multiplication_factor * float(l[6]) )
                output_line = str(e) + " " + str(n) + " " + l_z + " " + l[7] + "\n"
            else :
                n, e = convert_to_decimal_degs (logger, l[0], l[1], ";" )
                l_z = str( multiplication_factor * float(l[2]) )
                output_line =  str(e) + " " + str(n) + " " + l_z + " " + l[3] + "\n"
        if int(attribute_order_id) == int(BathyDbLib.ATTR_ORDER_DMSEN_ID) :
            if int(separator_id) == int(BathyDbLib.SEP_WHITESPACE_ID) :
                e, n = convert_to_decimal_degs (logger, l[0], l[2], ";" )
                l_z = str( multiplication_factor * float(l[4]) )
                output_line = str(e) + " " + str(n) + " " + l_z + " " + l[5] + "\n"
            elif int(separator_id) == int(BathyDbLib.SEP_SEMICOLON_ID) :
                e_in = str(l[0]) + ";" + str(l[1]) + ";" + str(l[2])
                n_in = str(l[3]) + ";" + str(l[4]) + ";" + str(l[5])
                e, n = convert_to_decimal_degs (logger, n_in, e_in, ";" )
                l_z = str( multiplication_factor * float(l[6]) )
                output_line = str(e) + " " + str(n) + " " + l_z + " " + l[7] + "\n"
            else :
                e, n = convert_to_decimal_degs (logger, l[0], l[1], ";" )
                l_z = str( multiplication_factor * float(l[2]) )
                output_line =  str(e) + " " + str(n) + " " + l_z + " " + l[3] + "\n"

        # Return formatted output line
        return output_line

    except Exception, err:
        logger.error("Processing line " + str(line) + " failed: ERROR: %s\n" % str(err))
        return None

def process_imp_gml_line ( logger, line, depth_attribute_name ) :
    # Function to process import gml line without additional attributes
    try :
        # Only process line when it is a point
        if 'gml:Point' in line :
            # Remove namespace
            line = line.replace('gml:','')
            # Parse line
            xml_line = xml.dom.minidom.parseString(line)
            # Get depth
            xml_elements = xml_line.getElementsByTagName('Point')
            for xml_element in xml_elements :
                z = xml_element.getAttribute(depth_attribute_name)
            # Get coordinates
            xml_elements = xml_line.getElementsByTagName('coordinates')[0]
            xml_element = xml_elements.childNodes[0].nodeValue
            x = xml_element.rstrip().split()[0]
            y = xml_element.rstrip().split()[1]
            z = float(z)
            # Write output
            output_line = str(x) + str(BATHYSPACE_SEP) + str(y) + str(BATHYSPACE_SEP) + str(z) + "\n"

            # Return formatted output line
            return output_line

    except Exception, err:
        logger.error("Processing line " + str(line) + " failed: ERROR: %s\n" % str(err))
        return None

def process_imp_emodnet_line ( logger, line, multiplication_factor) :
    # Function to process emodnet line
    try :
        # Only process line with a depth (l[4] must not be empty)
        l  = line.rstrip().split(";")
        if l[4] :
            z = str( multiplication_factor * float(l[4]) )
            output_line = check_value(l[0]) + " " + check_value(l[1]) + " " + z + " " + check_value(l[2]) + " " + check_value(l[3]) + " " + check_value(l[5]) + " " + check_value(l[6]) + " " + check_value(l[7]) + " " + check_value(l[8]) + " " + check_value(l[9]) + " " + check_value(l[10]) + " " + check_value(l[11]) + "\n"

            # Return formatted output line
            return output_line

    except Exception, err:
        logger.error("Processing line " + str(line) + " failed: ERROR: %s\n" % str(err))
        return None

def create_spatial_index_on_database ( DbConnection, logger, object_class_id, im_id, task_id  ) :
    # Create spatial index on database
    try :
        logger.info("Create spatial index on database")

        # Set default values
        multiplication_factor = 1
        tiling = 'F'

        # Start processing in database
        DbConnection.import_survey ( object_class_id, im_id, task_id, multiplication_factor, tiling )

    except Exception, err:
        logger.critical("Create spatial index on database failed: ERROR: %s\n" % str(err))
        raise

def write_depths_to_database  ( DbConnection, logger, import_file, im_format_id ) :
    # Write depths to intermediate table on database
    try :
        logger.info("Write depths to intermediate table on database from file " + str(import_file) )

        # Delete rows that may exist in sdb_im_import_temp
        logger.info("Delete from temp table")
        DbConnection.delete_im_temp_table ()

        # First build the insert statement based on im_fomat to import
        insert_stmt, nr_columns = DbConnection.get_insert_statement ( im_format_id )

        # Get number of lines in file
        nr_of_lines = get_nr_of_lines ( logger, import_file )
        
        # Now read points from file and insert into array
        depths = []
        i = 0
        first_row = True
        file = open(import_file,'r')

        # Loop through files
        for line in file :

            # Split line into columns
            c = line.rstrip().split(BathyExecutablesLib.MG_OUTPUTDELIMITER_VAL)

            # Log first line
            if first_row :
                logger.info( "File format: "+ str(line) )
                logger.info( "Number of columns: " + str(nr_columns) )
                first_row = False

            # Write columns to array
            if nr_columns == 3 :
                depths.append( ( float(c[0]), float(c[1]), float(c[2]) ) )
                i = i + 1
            if nr_columns == 4 :
                depths.append( ( float(c[0]), float(c[1]), float(c[2]), str(c[3]) ) )
                i = i + 1
            if nr_columns == 5 :
                depths.append( ( float(c[0]), float(c[1]), float(c[2]), str(c[3]), str(c[4]) ) )
                i = i + 1
            if nr_columns == 6 :
                depths.append( ( float(c[0]), float(c[1]), float(c[2]), str(c[3]), str(c[4]), str(c[5]) ) )
                i = i + 1
            if nr_columns == 7 :
                depths.append( ( float(c[0]), float(c[1]), float(c[2]), str(c[3]), str(c[4]), str(c[5]), str(c[6]) ) )
                i = i + 1
            if nr_columns == 8 :
                depths.append( ( float(c[0]), float(c[1]), float(c[2]), str(c[3]), str(c[4]), str(c[5]), str(c[6]), str(c[7]) ) )
                i = i + 1
            if nr_columns == 9 :
                depths.append( ( float(c[0]), float(c[1]), float(c[2]), str(c[3]), str(c[4]), str(c[5]), str(c[6]), str(c[7]), str(c[8]) ) )
                i = i + 1
            if nr_columns == 10 :
                depths.append( ( float(c[0]), float(c[1]), float(c[2]), str(c[3]), str(c[4]), str(c[5]), str(c[6]), str(c[7]), str(c[8]), str(c[9]) ) )
                i = i + 1
            if nr_columns == 11 :
                depths.append( ( float(c[0]), float(c[1]), float(c[2]), str(c[3]), str(c[4]), str(c[5]), str(c[6]), str(c[7]), str(c[8]), str(c[9]), str(c[10]) ) )
                i = i + 1
            if nr_columns == 12 :
                depths.append( ( float(c[0]), float(c[1]), float(c[2]), str(c[3]), str(c[4]), str(c[5]), str(c[6]), str(c[7]), str(c[8]), str(c[9]), str(c[10]), str(c[11]) ) )
                i = i + 1
            if nr_columns == 13 :
                depths.append( ( float(c[0]), float(c[1]), float(c[2]), str(c[3]), str(c[4]), str(c[5]), str(c[6]), str(c[7]), str(c[8]), str(c[9]), str(c[10]), str(c[11]), str(c[12]) ) )
                i = i + 1

            if i % BathyDbLib.NR_OF_ROWS_PER_INSERT == 0 or i == nr_of_lines:
                DbConnection.insert_depth( insert_stmt, depths )
                logger.info(str(i) + " depths written to database")
                depths = []

        # All depths are writeen to database
        logger.info("Write file to database completed: " + str(i) + " depths written to database")
        file.close()

    except Exception, err:
        logger.critical("Write depths to intermediate table on database failed: ERROR: %s\n" % str(err))
        raise

def get_link_distance_estimate ( DbConnection, logger, im_id, coord_sys_id, bathyspace_file ) :

    try:
        logger.info("Estimate link distance")

        # Get additional attributes
        coord_sys_class_id = get_coord_sys_class ( DbConnection, logger, coord_sys_id )
        min_link_distance, max_link_distance = get_link_distance_limits ( DbConnection, logger, im_id, coord_sys_id, coord_sys_class_id, bathyspace_file )

        # Get import file type for IM
        attributes = [BathyDbLib.IM_INPUT_FORMAT_COL, BathyDbLib.IM_SURVEYTYPE_COL ]
        values     = DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, im_id, attributes )
        input_file_type_id = values[0]
        survey_type_id     = values[1]

        # Calculate link distance estimate:
        # - If you have too little points ( less than MIN_NR_GRIDCELLS * MIN_NR_POINTS )
        # - Min link distance is larger than max link distance: estimate = max link distance
        if int(min_link_distance) < int(max_link_distance) :
            link_distance_estimate = int( min_link_distance + 0.1 * ( max_link_distance - min_link_distance ) )
        else :
            link_distance_estimate = int( max_link_distance )

        # Correct for singlebeam or trackline (multiply estimate with 2)
        if int(survey_type_id)  == int(BathyDbLib.SINGLEBEAM_SURVEYTYPE_ID) or int(survey_type_id)  == int(BathyDbLib.TRACKLINE_SURVEYTYPE_ID) :
            link_distance_estimate = link_distance_estimate * 2.0

        logger.info("Link distance estimate is " + str( round( link_distance_estimate ) ) )

        return int(round( link_distance_estimate ))

    except Exception, err:
        logger.critical("Estimate link distance failed: ERROR: %s\n" % str(err))
        raise


def store_im_attributes_from_import ( DbConnection, logger, ParameterList ) : 
    """Function to store IM attributes from import wizard"""
    try :
        logger.info("Store IM attributes from import wizard")

        attributes             = [ BathyDbLib.IM_BATHYSP_FILE_COL ]
        values                 = DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, ParameterList[ PARAMETER_IM_ID ], attributes )
        bathyspace_file        = values[0]
        
        attribute_list = {}
        attribute_list [ BathyDbLib.IM_SOURCE_FILES_COL ]   = ParameterList[ PARAMETER_INPUT_FILE ]
        attribute_list [ BathyDbLib.IM_INPUT_FORMAT_COL ]   = ParameterList[ PARAMETER_FILE_FORMAT ]
        attribute_list [ BathyDbLib.IM_COORD_SYS_SRC_COL ]  = ParameterList[ PARAMETER_COORD_SYS ]
        attribute_list [ BathyDbLib.IM_SEP_MODEL_COL ]      = ParameterList[ PARAMETER_VERT_REF ]
        attribute_list [ BathyDbLib.IM_ETRSYEAR_COL ]       = ParameterList[ PARAMETER_ETRSYEAR ]
        attribute_list [ BathyDbLib.IM_STARTDATE_COL ]      = ParameterList[ PARAMETER_STARTDATE ]
        attribute_list [ BathyDbLib.IM_VERDAT_SOURCE_COL ]  = ParameterList[ PARAMETER_VERDAT_SOURCE ]
        DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, ParameterList[ PARAMETER_IM_ID ], attribute_list )

        # Now estimate link distance and store
        attribute_list [ BathyDbLib.IM_LINK_DIST_EST_COL ]  = get_link_distance_estimate ( DbConnection, logger, ParameterList[ PARAMETER_IM_ID ], ParameterList[ PARAMETER_COORD_SYS ], bathyspace_file )
        DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, ParameterList[ PARAMETER_IM_ID ], attribute_list )

        # Update workflowstep
        DbConnection.update_workflow_step ( ParameterList[ PARAMETER_PROCESS_ID ], BathyDbLib.IM_CLASS_ID, ParameterList[ PARAMETER_IM_ID ] )

    except Exception, err:
        logger.critical("Store IM attributes from import wizard: ERROR: %s\n" % str(err))
        raise

def extract_metadata_from_bag ( DbConnection, logger, bag_xml_file ) :
    # Extract coordinate system and vertical datum info from BAG metadata XML
    try :
        logger.info("Retrieve coordinate system and vertical datum from BAG")
        parameter_list = ( BAG_PROJECTION, BAG_ELLIPSOID, BAG_DATUM , BAG_PROJECTION_PARAMS )
        tag_list       = ( BAG_CODE, BAG_ZONE )
        parameter_values = {}
        bagXml = xml.dom.minidom.parse(bag_xml_file)
        for parameter in parameter_list :
            nodelist = bagXml.getElementsByTagName(parameter)
            for node in nodelist :
                for tag in tag_list :
                    codelist = node.getElementsByTagName(tag)
                    for code in codelist :
                        parameter_values[parameter] = code.childNodes[0].nodeValue

        # Find database ID of coordinate system
        db_attributes = {}
        parameters = parameter_values.keys()
        logger.info("Coordinate system parameters from BAG: " + str(parameter_values))
        for parameter_name in parameters :
            if BAG_EPSG_DB_MAPPING.has_key( parameter_name ) :
                db_attribute = BAG_EPSG_DB_MAPPING [ parameter_name ]
                db_attributes[db_attribute] = parameter_values[parameter_name]
        result_list = DbConnection.query_object ( BathyDbLib.EPSG_CLASS_ID, db_attributes )
        if result_list :
            for row in result_list :
                epsg_id = row
                # Now query name of coordinate system
                attributes = [ "NAME", "SYS002" ]
                values =  DbConnection.get_obj_attributes ( BathyDbLib.EPSG_CLASS_ID, epsg_id, attributes )
                epsg_name = values[0]
                epsg_code = values[1]
                logger.info("Coordinate system BAG file: " + str(epsg_name))
                logger.info( "EPSG code = " + str(epsg_code) )
                # Now get db_id of epsg
                db_attributes = {}
                db_attributes[BathyDbLib.EPSG_CODE_COL] = epsg_code
                result_list =  DbConnection.query_object ( BathyDbLib.GEODETIC_HORIZ_CLASS_ID, db_attributes )
                if result_list :
                    for row in result_list :
                        epsg_id_db = row
                        logger.info( "EPSG ID database = " + str(epsg_id_db) )
                else :
                    epsg_id_db = None
        else :
            logger.warning("Coordinate system BAG file not in database")
            epsg_id_db = None
#            # Now query name of coordinate system
#            attributes = [ "NAME" ]
#            values =  DbConnection.get_obj_attributes ( BathyDbLib.EPSG_CLASS_ID, epsg_id, attributes )
#            epsg_name = values[0]
#            logger.info("Store " + str(epsg_name) + " as coordinate system")

        # Find database ID of vertical datum
#        db_attributes = {}
#        parameters = parameter_values.keys()
#        for parameter_name in parameters :
#            if BAG_VERD_DB_MAPPING.has_key( parameter_name ) :
#                db_attribute = BAG_VERD_DB_MAPPING [ parameter_name ]
#                db_attributes[db_attribute] = parameter_values[parameter_name]
#        result_list =  DbConnection.query_object ( BathyDbLib.VERDATIN_CLASS_ID, db_attributes )
#        if result_list :
#            for row in result_list :
#                verdat_in_id = row
#                # Now query name of vertical datum
#                attributes = [ "NAME" ]
#                values =  DbConnection.get_obj_attributes ( BathyDbLib.VERDATIN_CLASS_ID, verdat_in_id, attributes )
#                verdat_name = values[0]
#                logger.info("Vertical datum BAG file: " + str(verdat_name))
#        else :
#            logger.warning("Vertical datum BAG file not in database")
#            # Now query name of vertical datum
#            attributes = [ "NAME" ]
#            values =  DbConnection.get_obj_attributes ( BathyDbLib.VERDATIN_CLASS_ID, verdat_in_id, attributes )
#            verdat_name = values[0]
#            logger.info("Store " + str(verdat_name) + " as vertical datum")

        # Get database ID of epsg_code

        

        # Return extracted metadata
        return epsg_id_db

    except Exception, err:
        logger.critical("Retrieve coordinate system and vertical datum from BAG file failed: ERROR: %s\n" % str(err))
        raise

def upload_personal_dtm (  logger, user_id, file_ext, file_in ) :
    """Function to upload personal DTM to server"""
    try :
        logger.info('Start upload to server ' + EMODNET_UPLOAD_HOST )
        
        # Switch on Personal layer for production 
        # so make upload dependent of environment setting
        # host = EMODNET_UPLOAD_HOST
        # host = EMODNET_UPLOAD_HOST if not "EMODNET_APP_HOST" in os.environ else os.environ["EMODNET_APP_HOST"]

        host = EMODNET_UPLOAD_HOST        
        
        url = "http://%s:8080/geoserver/rest" % host
        user = "personal"
        password = "layer"
        workspace = "user"
        
        scp_user = "usrprod"
        scp_pass = "emodnet"
        scp_host = host
        scp_data = "/var/www/html/personal.n4m5.eu"
        scp_path = "PSCP.EXE"
        plink_path = "PLINK.EXE"
        
        #user_id = "123467"
        store = str(user_id) + file_ext
        
        cat = Catalog(url, user, password)
        
        #localfile = str(user_id) + file_ext
        localfile = file_in
        tmpfile = '%s/%s.new' % (scp_data, user_id)
        targetfile = '%s/%s.%s' % (scp_data, user_id, file_ext)
        
        scp_command = '%s -pw %s "%s" "%s@%s:%s"' % (scp_path, scp_pass, localfile, scp_user, scp_host, tmpfile)
        logger.info( scp_command ) 
        os.system(scp_command)
        
        ssh_command = '%s -pw %s "%s@%s" "mv %s %s"' % (plink_path, scp_pass, scp_user, scp_host, tmpfile, targetfile)
        logger.info( ssh_command )
        os.system(ssh_command)

    except Exception, err:
        logger.critical("Upload to server failed: ERROR: %s\n" % str(err))
        raise

def upload_to_geoserver (  logger, user_id, file_in ) :
    """Function to upload layer to Geoserver"""
    try :
        logger.info('Start upload to Geoserver '  + EMODNET_UPLOAD_HOST )
        
        ####################################################
        
        host = EMODNET_UPLOAD_HOST
        
        url = "http://%s:8080/geoserver/rest" % host
        user = "personal"
        password = "layer"
        workspace = "user"
        
        scp_user = "usrtif"
        scp_pass = "geotiff"
        scp_host = host
        scp_data = "/opt/geoserver/coverages/user"
        scp_path = "PSCP.EXE"
        plink_path = "PLINK.EXE"
        
        #user_id = "123467"
        store = str(user_id) + ".tif"
        
        cat = Catalog(url, user, password)
        
        #localfile = str(user_id) + ".tif"
        localfile = file_in
        tmpfile = '%s/%s.new' % (scp_data, user_id)
        targetfile = '%s/%s.tif' % (scp_data, user_id)
        
        scp_command = '%s -pw %s "%s" "%s@%s:%s"' % (scp_path, scp_pass, localfile, scp_user, scp_host, tmpfile)
        logger.info( scp_command )
        os.system(scp_command)
        
        ssh_command = '%s -pw %s "%s@%s" "mv %s %s"' % (plink_path, scp_pass, scp_user, scp_host, tmpfile, targetfile)
        logger.info( ssh_command )
        os.system(ssh_command)
        
        try:
            user_store = cat.get_store(store, workspace)
            cat.delete(user_store, recurse=True)
            logger.info( "Deleted current store %s" % store )
        except FailedRequestError:
            logger.warning(  "No store yet" )
        
        #create store in geoserver
        fileUrl = "file:" + targetfile
        headers = {"Content-type": "text/xml"}
        xml = '<coverageStore>'
        xml = xml + '<name>%s</name>'
        xml = xml + '<workspace><name>%s</name></workspace>'
        xml = xml + '<url>%s</url>'
        xml = xml + '<enabled>true</enabled>'
        xml = xml + '<type>GeoTIFF</type>'
        xml = xml + '</coverageStore>'
        xml = xml % (store, workspace, fileUrl) 
        
        request_uri = '%s/workspaces/%s/coveragestores/' % (url, workspace)
        conn = cat.http
        resp = conn.request(request_uri, "POST", xml, headers)
        if resp[0].status != 201:
            logger.info(  "XML: " + xml )
            logger.info(  "URI: " + request_uri )
            logger.info(  "RESP: "+ str(resp) )
            raise FailedRequestError
        else:
            logger.info( "Created store %s" % store )
        
        #publish coverage
        headers = {"Content-type": "text/xml"}
        xml = '<coverage><name>%s</name></coverage>' % (store);
        
        xml = '<coverage>'
        xml = xml + '<name>%s</name>'
        xml = xml + '<title>Geotiff Personal Layer %s</title>'
        xml = xml + '</coverage>'
        
        xml = xml % (user_id, user_id)
        
        request_uri = '%s/workspaces/%s/coveragestores/%s/coverages' % (url, workspace, store)
        conn = cat.http
        resp = conn.request(request_uri, "POST", xml, headers)
        
        if resp[0].status != 201:
            logger.info(  "XML: " + xml )
            logger.info(  "URI: " + request_uri )
            logger.info(  "RESP: "+ str(resp) )
            raise FailedRequestError
        else:
            logger.info(  "Created coverage %s" % user_id )
        
        #change layer settings
        xml = '<layer>'
        xml = xml + '<enabled>true</enabled>'
        xml = xml + '<metadata><entry key="advertised">false</entry></metadata>'
        xml = xml + '</layer>'
        
        request_uri = '%s/layers/%s:%s' % (url, workspace, user_id)
        conn = cat.http
        resp = conn.request(request_uri, "PUT", xml, headers)
        if resp[0].status != 200:
            logger.info(  "XML: " + xml )
            logger.info(  "URI: " + request_uri )
            logger.info(  "RESP: "+ str(resp) )
            raise FailedRequestError
        else:
            logger.info( "Updated layer visibility for layer %s" % user_id )  
        
    except Exception, err:
        logger.critical("Upload to Geoserver failed: ERROR: %s\n" % str(err))
        raise

   
def getenv_system(varname, default=''):
    #Get SYSTEM environment value, as if running under Service or SYSTEM account
    
    #Author: Denis Barmenkov <denis.barmenkov@gmail.com>
    
    #Copyright: this code is free, but if you want to use it, 
               #please keep this multiline comment along with function source. 
               #Thank you.
    
    #2006-01-28 15:30
    #'''    
    v = default
    try:
        rkey = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment')
        try:
            v = str(win32api.RegQueryValueEx(rkey, varname)[0])
            v = win32api.ExpandEnvironmentStrings(v)
        except:
            pass
    finally:
        win32api.RegCloseKey(rkey)
    return v



#def generate_intermediate_file ( logger, input_file, output_file ) :
#
#    # Start execution
#    try:
#        logger.info ('Start generation intermediate file' )
#
#        # Get pre-defined contour set
#        if l_predef_set_id :
#            l_predef_set  = self.DbConnection.get_domain_value ( self.ParameterList [ BathyToolsLib.PARAMETER_PROCESS_ID ], self.ParameterList[ BathyToolsLib.PARAMETER_PREDEFINEDSET ], int( l_predef_set_id ) )
#
#        # Check outputfile for extension, if not add extension
#        l_contour_file    = BathyToolsLib.add_file_ext( l_contour_file, self.ParameterList[ BathyToolsLib.PARAMETER_FILE_MASK ] )
#
#        # Define temporary file name
#        l_temp_dir        = BathyToolsLib.get_working_dir( self.logger, self.ParameterList [ BathyToolsLib.TEMPDIR ] )
#        l_ascii_file      = l_temp_dir + "\\tmp_"         + str(im_id) + BathyExecutablesLib.FILE_EXT_ASCII
#        l_aggr_sds_file   = l_temp_dir + "\\tmp_aggr_"    + str(im_id) + BathyExecutablesLib.FILE_EXT_SDS
#        l_cont_sds_file   = l_temp_dir + "\\tmp_contour_" + str(im_id) + BathyExecutablesLib.FILE_EXT_SDS
#
#        # Get vertical reduction parameters
#        l_value = int( l_verdatout_id )
#        l_ver_dat_in, l_ver_dat_out, l_offset, l_m_factor = BathyToolsLib.get_separation_model ( self.DbConnection, self.logger, l_value )
#
#        # Get bathyspace type and file from database
#        l_attributes   = [ BathyDbLib.IM_IM_FORMAT_COL ]
#        l_values       = self.DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attributes )
#        l_im_format_id = l_values[0]
#
#        # Call database procedure to get depths from database
#        self.logger.info ( 'Get depths from database' )
#        l_ascii_format_id = BathyDbLib.FORMAT_XYZ_SEMICOLON
#        l_point_in_hull   = "F"
#        l_include_attr    = "F"
#        l_depth_positive  = "T"
#        l_nr = self.DbConnection.write_IM_depths_to_file ( l_ascii_file, l_im_id, l_im_format_id, l_ascii_format_id, l_point_in_hull, l_include_attr, l_depth_positive )
#
#        # Run Makegrid for geodetic transformations
#        self.logger.info ( 'Apply separation model' )
#        l_etrsyear  = 2010
#        l_epsg_code = BathyDbLib.get_epsg_code_db()
#        l_geoconv_file = BathyExecutablesLib.makegrid_geo_conv (self.logger, l_ascii_file, l_temp_dir, l_epsg_code, l_epsg_code, l_ver_dat_in, l_ver_dat_out, l_offset, l_m_factor, l_etrsyear, ";", ";" )
#
#        # Remove ascii file
#        if os.path.exists( l_ascii_file ) :
#            os.remove( l_ascii_file )
#
#        # Generate aggregated SDS file
#        self.logger.info ( 'Generate aggregate file' )
#        BathyExecutablesLib.sds_aggregate ( self.logger, l_geoconv_file, l_aggr_sds_file, l_temp_dir, l_im_id )
#
#        # Remove geoconv file
#        if os.path.exists( l_geoconv_file ) :
#            os.remove( l_geoconv_file )
#
#        # Generate contours from SDS aggregate file
#        self.logger.info ( 'Generate contours' )
#        BathyExecutablesLib.sds_generate_contours ( self.logger, l_aggr_sds_file, l_cont_sds_file, l_temp_dir, l_mapscale, l_predef_set, l_begin_contour, l_contour_incr, l_contour_levels )
#
#        # Remove aggregate file
#        if os.path.exists( l_aggr_sds_file ) :
#            os.remove( l_aggr_sds_file )
#
#        # Convert contours to 7cb file
#        self.logger.info ( 'Convert contours to 7cb' )
#        BathyExecutablesLib.sds_convert_contours_to_7cb ( self.logger, l_cont_sds_file, l_contour_file )
#
#        # Remove contour file
#        if os.path.exists( l_cont_sds_file ) :
#            os.remove( l_cont_sds_file )
#
#    except Exception, err:
#        logger.critical( "Start generation intermediate file failed:ERROR: %s\n" % str(err))
#        raise


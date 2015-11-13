#! /usr/bin/python

# standard library imports 
import os
import logging
import string
import shutil
import numpy
#from Numeric import *

# related third party imports
#from CGAL.Alpha_shapes_2 import *
#from CGAL.Kernel import *
from osgeo import ogr
from osgeo import osr
#from Scientific.IO.NetCDF import *

# Shapely imports
# from shapely.wkb import loads, dumps

# local application/library specific imports
import BathyToolsLib
import BathyDbLib

__author__="Terlien"
__date__ ="$28-mei-2010 11:52:24$"

# Module name
BATHYTOOLS  = "BathyTools"
MODULE_NAME = "BathyExecutablesLib"

# Executables CMDOP IVS3D:
PROJECTCREATE         = "cmdop projectcreate"
PROJECTADDSOURCE      = "cmdop projectaddsource"
GENERATESDFILE        = "cmdop gridder"
CREATECOVERAGEVECTORS = "cmdop createcoveragevectors"
ESRIASCIICONVERTER    = "cmdop gasciitoscalar"
ESRIBINCONVERTER      = "cmdop arctoscalar"
RESAMPLER             = "cmdop resampler"
UNLOADSDFILE          = "cmdop exportsurface"
BAGTOASCIICONVERTER   = "cmdop bagtoascii"
BAGTOSDCONVERTER      = "cmdop bagtoscalar"
SCALARINVERT          = "cmdop scalarinvert"
IMAGECONVERT          = "cmdop imageconvert"
IMAGEINGESTER         = "cmdop imageingester"
SHADER                = "cmdop shader"
SURFACEDIFFERENCE     = "cmdop surfacediff"

# Executables Makegrid
MAKEGRID                = "SENSMakegrid.exe"
MAKEGRIDORACLEINTERFACE = "MakeGridOracleInterface"
MAKEGRIDHULL            = "MakeHull.exe"
MAKEGRIDEMODNET         = "MakeEMODNet.exe"
MAKEGRIDESRIGRID        = "MakeEsriGrid.exe"
MAKEGRIDGEOTIF          = "MakeGeoTIFF.exe"

# Executables SENS
ASCIIIMPORTER  = "AsciiImportParser.exe"
DONARIMPORTER  = "DonarImporter.exe"
CSVIMPORTER    = "CsvImporter.exe"
ISOXMLIMPORTER = "IsoXmlImporter.exe"
BAGIMPORTER    = "BagImporter.exe"
SQLIMPORTER    = "SqlImporter.exe"

# Executables SDS (Herman Varma)
ASC2SDS      = "asc2sds"
SDS2ASC      = "sds2asc.exe"
SDS2SDS      = "sds2sds"
SDSSORT      = "sdssort"
HHAGGREGATE  = "hhaggregate"
SDSOVERPLOT  = "sdsoverplot"
SDSCONTOUR   = "sdscontour"
SDSPOINT27CB = "sdspoint27cb"
SDSLINE27CB  = "sdsline27cb"
SDS2CONTASC  = "sds2contAsc.exe"

# SDS config files
SDS_XYZ_CONFIG  = "xyz.ctl"
SDS_CONV_CONFIG = "conv2meter.con"
SDS_TILE_CONFIG = "tile_23_23_STAT_meter.ctl"
SDS_SORT_CONFIG = "sort.con"
SDS_AGGR_CONFIG = "aggregate_22.con"
SDS_CONT_CONFIG = "contour_intervals.con"
SDS_SPOT_CONFIG = "spot_soundings.con"
SDS_LINE_7CB_CONFIG  = "line_27cb.con"
SDS_POINT_7CB_CONFIG = "point_27cb.con"
SD2ASC_OVERPL_CONFIG = "sds2asc_overplot.con"
SD2ASC_OVERPL_CONFIG_SHOALS = "sds2asc_overplot_shoals.con"
SD2ASC_OVERPL_CONFIG_DEEPS  = "sds2asc_overplot_deeps.con"

# Depth field for shape file
CONTOUR_DEPTH_FIELD = "Depth"
OVERPLOT_SEPARATOR  = ","

# SDS constants
SDS_POINTSIZE_CARIS  = 4.336200043362
SDS_POINTSIZE_7CS    = 11
SDS_SPOTS_SHOALS     = "SHOALS"
SDS_SPOTS_SHOALS_COL = "MIN_DEPTH"
SDS_SPOTS_DEEPS      = "DEEPS"
SDS_SPOTS_DEEPS_COL  = "MAX_DEPTH"
SDS_WORKSPACE_SIZE   = "10000000000"
SDS_MEMORY_SIZE      = "50000000"
#SDS_MEMORY_SIZE     = "500000"

# SDS dictionaries
# Spot sounding algorithm assumes depth positive
# For SENS depth is negative
# For shoals extract smallest value from spot sounding file => CONFIG_DEEPS
# For deeps  extract largest value from spot sounding file => CONFIG_SHOALS
SPOT_SOUNDING_TYPE_INV = {}
SPOT_SOUNDING_TYPE_INV [ SDS_SPOTS_SHOALS ] = SDS_SPOTS_DEEPS
SPOT_SOUNDING_TYPE_INV [ SDS_SPOTS_DEEPS  ] = SDS_SPOTS_SHOALS
SPOT_SOUNDING_COL = {}
SPOT_SOUNDING_COL [ SDS_SPOTS_SHOALS ] = SDS_SPOTS_SHOALS_COL
SPOT_SOUNDING_COL [ SDS_SPOTS_DEEPS  ] = SDS_SPOTS_DEEPS_COL
# For conversion to ascii depth is negative
SDS2ASC_CONFIG_FILES = {}
SDS2ASC_CONFIG_FILES [ SDS_SPOTS_SHOALS ] = SD2ASC_OVERPL_CONFIG_SHOALS
SDS2ASC_CONFIG_FILES [ SDS_SPOTS_DEEPS  ] = SD2ASC_OVERPL_CONFIG_DEEPS



# File extensions
FILE_EXT_ASCII = ".xyz"
FILE_EXT_META  = ".dat"
FILE_EXT_SD    = ".sd"
FILE_EXT_TMP   = ".tmp"
FILE_EXT_SHP   = ".shp"
FILE_EXT_LOG   = ".log"
FILE_EXT_ASC   = ".asc"
FILE_EXT_GRD   = ".grd" # Makegrid generated files
FILE_EXT_SDS   = ".sds" # Herman Varma SDS files
FILE_EXT_7CB   = ".7cb"
FILE_EXT_GML   = ".gml"
FILE_EXT_ZIP   = ".zip"
FILE_EXT_TIF   = ".tif"
FILE_EXT_NC    = ".nc"
FILE_EXT_PAR   = ".makegrid_parameter"

# Makegrid parameters for geodetic conversions
MG_DBUSER          = "DbUser"
MG_DBPASS          = "DbPass"
MG_DBCNXT          = "DbCnxt"
MG_OUTPUTFILE      = "OutputFile"
MG_TEMPPATH        = "TempPath"
MG_PRODUCTMODE     = "ProductMode"
MG_FILELIST        = "FileList"
MG_PRODUCTFORMAT   = "ProductFormat"
MG_INPUTDELIMITER  = "InputDelimiter"
MG_OUTPUTDELIMITER = "OutputDelimiter"
MG_DECIMALSEP      = "DecimalSeparator"
MG_FACTOR          = "Factor"
MG_OFFSET          = "Offset"
MG_EPSGCODEOUT     = "EPSGCodeOut"
MG_ETRSYEAR        = "ETRSYear"
MG_VERDATOUT       = "VerDatOut"
MG_XYZFORMAT       = "XyzFormat"
MG_VERBOSE         = "Verbose"
MG_WKT_OUT         = "WktOut"

# Makegrid standard parameter values for geodetic conversions
MG_PRODUCTASCIIGRID_VAL = "ASCII xyz grid"
MG_PRODUCTASCII_VAL     = "ASCII xyz"
MG_PRODUCTESRIAG_VAL    = "ESRI ASCII grid"
MG_PRODUCTSDFILE_VAL    = "SD file"
MG_INPUTDELIMITER_VAL   = ";"
MG_OUTPUTDELIMITER_VAL  = ";"
MG_XYZFORMAT_VAL        = "x;y;z*"
MG_XYZFORMAT_SDS_VAL    = "x y z"
MG_DEFAULT_IM_TYPE_VAL  = "M"
MG_DECIMALSEP_VAL       = "."
MG_FILELIST_FILE_VAL    = "MakegridFileList.dat"
MG_PARAMETER_FILE_VAL   = "MakegridParameters.dat"
MG_OUTPUT_FILE_VAL      = "MakegridOutput.asc"
MG_OUTPUT_FILE_ASC_VAL  = "MakegridOutput.xyz"
MG_OUTPUT_FILE_GRD_VAL  = "MakegridOutput.grd"
MG_ETRSYEAR_VAL         = "2010"
MG_POSTPROCESSING_VAL   = "SENS"
MG_VERBOSE_VAL          = "1"
MG_GEOGRAPHIC_LIMIT     = 0.1
MG_PIPE_SEPARATOR       = "|"
MG_PROD_MODE_IM         = "Single IM"
MG_SHALLOWEST_VAL       = "Shallowest"
MG_DEEPEST_VAL          = "Deepest"

# Polygons that split the world in half for dateline correction
WEST_HEMISPHERE         = 'POLYGON ((180 -90, 360 -90, 360 90, 180 90, 180 -90))'
EAST_HEMISPHERE         = 'POLYGON ((0 -90, 180 -90 , 180 90, 0 90, 0 -90))'

# Separation model options
NO_SEP_MODEL_AVAILABLE = -1
NO_SEP_MODEL_REQUIRED  = 99

# Mapping from survey type id's to Multibeam or Singlebeam for Makegrid
MAKEGRID_DB_IM_TYPE_MAPPING = { 796: 'M'
                              , 797: 'S'
                              , 798: 'M'
                              , 799: 'S'
                              , 800: 'M'
                              , 5135: 'M'
                              }

# Parameter Ascii importer
AI_INPUTFILE            = "InputFile"
AI_GEOGRAPHIC           = "IsGeographic"
AI_REQUIRED_COLS        = "RequiredColumns"
AI_NUMERIC_COLS         = "NumericColumns"

# GDAL globals
GDAL_NODATA_VALUE   = int(-32767)
GDAL_AAIGRID_FORMAT = "AAIGrid"
GDAL_MEM_FORMAT     = "MEM"

# Parameter CSV importer
CSV_INPUTFILE            = "InputFile"

# Defines for Donar
DONAR_TR       = "donar_tr"
DONAR_IM       = "donar_im"
DONAR_TR_GROUP = "donar_tr_group"
DONAR_IM_GROUP = "donar_im_group"

# Limits of TIN hull generation algorithm
MAX_NR_OF_LINES = 250000
MAX_NR_OF_EDGES = 25000

# Defines for EMODNET
EMODNET_SEPARATOR     = ";"
EMODNET_GRIDSIZE      = float(0.00416667)
EMODNET_MISSING_VALUE = 0

# Defines for NetCDF
NETCDF_FLOAT = 'f'
NETCDF_DOUBLE_PRECISION_FLOAT = 'd'
NETCDF_INT = 'i'
NETCDF_LONG = 'l'
NETCDF_CHARACTER = 'c'
NETCDF_BYTE = 'b'

# Defines for NetCDF CF convention
NETCDF_DIMENSION = 'area'

# CF dimensions
NETCDF_LON = 'position_long'
NETCDF_LAT = 'position_lat'

# CF metadata attributes
NETCDF_VARIABLE_ATTRIBUTES = { 'units': 'units'
                               , 'standard_name' : 'standard_name'
                               , 'long_name' : 'long_name'
                               , '_FillValue' : '_FillValue'
                               , 'cell_methods' : 'cell_methods'
                               , 'start' : 'start'
                               , 'increment' : 'increment'
                               }

# CF global attributes
NETCDF_GLOBAL_ATTRIBUTES = { 'title': 'title'
                             , 'institution': 'institution'
                             , 'history': 'history'
                             , 'source': 'source'
                             , 'references': 'references'
                             , 'comment' : 'comment'
                             }

# CF cell methods
NETCDF_CELL_METHODS = { 'minimum': 'minimum'
                        , 'maximum': 'maximum'
                        , 'mean': 'mean'
                        , 'standard_deviation': 'standard_deviation'
                        , 'interpolations': 'interpolations'
                        , 'elementary_surfaces': 'elementary_surfaces'
                        , 'smoothed':  'smoothed'
                        , 'smoothed_offset': 'smoothed_offset'
                        }


####################################
# CMDOP functions                  #
####################################

def cmdop_projectcreate ( DbConnection, logger, project, icoordsys) :
    """Function run run cmdop executable projectcreate"""
    try :
        logger.info("Running cmdop_projectcreate")
        command = PROJECTCREATE + " -project " + "\"" + str(project) + "\"" + " -icoordsys " + str(icoordsys)
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
    except Exception, err:
        logger.critical( "Running cmdop_projectcreate failed:ERROR: %s\n" % str(err))
        raise

def cmdop_projectaddsource ( DbConnection, logger, project, file, icoordsys) :
    """Function run run cmdop executable projectcreate"""
    try :
        logger.info("Running cmdop_projectaddsource")
        command = PROJECTADDSOURCE + " -project " + "\"" + str(project) + "\"" + " -in " + "\"" + str(file) + "\"" + " -icoordsys " + str(icoordsys) + " -type ungridded"
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
    except Exception, err:
        logger.critical( "Running cmdop_projectaddsource failed:ERROR: %s\n" % str(err))
        raise

def cmdop_gridder ( DbConnection, logger, file_in, sd_file, epsg_code, x_min, x_max, y_min, y_max, z_min, z_max, cellsize) :
    """Function run run cmdop executable gridder"""
    try :
        logger.info("Running cmdop_gridder")
        command = GENERATESDFILE + " -in " + "\"" + file_in + "\" -out " + "\"" + sd_file + "\"" + " -icoordsys " + str(epsg_code)  + " -ocoordsys " + str(epsg_code) + " -bounds " + str(x_min) + " " + str(x_max) + " " + str(y_min) + " " + str(y_max) + " " + str(z_min) + " " + str(z_max) + " -cell " + str(cellsize)
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
    except Exception, err:
        logger.critical( "Running cmdop_projectaddsource failed:ERROR: %s\n" % str(err))
        raise

def cmdop_createcoveragevectors ( DbConnection, logger, option, file_in, tmpfile_out ) :
    """Function run run cmdop executable createcoveragevectors"""
    try :
        logger.info("Running cmdop_createcoveragevectors")
        command = CREATECOVERAGEVECTORS + " " + option + " " + "\"" + file_in + "\" -out " + "\"" + tmpfile_out + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
    except Exception, err:
        logger.critical( "Running cmdop_createcoveragevectors failed:ERROR: %s\n" % str(err))
        raise

def cmdop_gasciitoscalar ( DbConnection, logger, file_in, sdfile_out, icoordsys, no_data_value ) :
    """Function run run cmdop executable gasciitoscalar"""
    try :
        logger.info("Running cmdop_gasciitoscalar")
        command = ESRIASCIICONVERTER + " -arcgis -in " + "\"" +  file_in + "\"" + " -out " + "\"" + sdfile_out + "\"" + " -icoordsys " + icoordsys + " -nodata "  + str(no_data_value)
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
    except Exception, err:
        logger.critical( "Running cmdop_gasciitoscalar failed:ERROR: %s\n" % str(err))
        raise

def cmdop_exportsurface ( DbConnection, logger, file_in, file_out ) :
    """Function run run cmdop executable exportsurface"""
    try :
        logger.info("Running cmdop_exportsurface")
        command = UNLOADSDFILE + " -in " + "\"" + file_in + "\"" + " -out " + "\"" + file_out + "\"" + " -format ascxyz"
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
    except Exception, err:
        logger.critical( "Running cmdop_exportsurface failed:ERROR: %s\n" % str(err))
        raise

def cmdop_bagtoascii ( logger, file_in, file_out ) :
    """Function run run cmdop executable bagtoascii"""
    try :
        logger.info("Running cmdop_bagtoascii")
        command = BAGTOASCIICONVERTER + " -in " + "\"" +  file_in + "\"" + " -out " + "\"" + file_out + "\"" + " -xml "
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
    except Exception, err:
        logger.critical( "Running cmdop_bagtoascii failed:ERROR: %s\n" % str(err))
        raise

def cmdop_bagtoscalar ( logger, file_in, sdfile_out ) :
    """Function run run cmdop executable bagtoscalar"""
    try :
        logger.info("Running cmdop_bagtoscalar")
        command = BAGTOSDCONVERTER + " -in " + "\"" +  file_in + "\"" + " -out " + "\"" + sdfile_out + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
    except Exception, err:
        logger.critical( "Running cmdop_bagtoscalar failed:ERROR: %s\n" % str(err))
        raise

def cmdop_scalarinvert ( logger, sd_file_vis, sd_file_vis_inv  ) :
    """Function run run cmdop executable scalarinvert"""
    try :
        logger.info("Running cmdop_scalarinvert")
        command = SCALARINVERT + " -in " + "\"" +  sd_file_vis + "\"" + " -out " + "\"" + sd_file_vis_inv + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
    except Exception, err:
        logger.critical( "Running cmdop_bagtoscalar failed:ERROR: %s\n" % str(err))
        raise

def cmdop_write_edges_from_cmdopfile ( file_in_cmdop, file_out_makegrid ) :
    """"Function conver cmdop edges file to makegrid input file"""
    fIn  = open( file_in_cmdop, 'r' )
    fOut = open( file_out_makegrid, 'w' )
    id_edge = 1
    for line_in in fIn :
        l = line_in.rstrip().split()
        if float(l[0]) <> float(9999) and float(l[1]) <> float(9999) and float(l[2]) <> float(9999) :
            line_out = l[0] + ";" + l[1] + ";" + l[2] + ";" + str(id_edge) + "\n"
            fOut.write( line_out )
        else :
            id_edge = id_edge + 1
    fIn.close()
    fOut.close()

def cmdop_write_edges_to_cmdopfile ( file_in_makegrid, file_out_cmdop  ) :
    """"Function conver makegrid output file to cmdop edges file"""
    fIn  = open( file_in_makegrid, 'r' )
    fOut = open( file_out_cmdop, 'w' )
    id_edge_actual = 1
    for line_in in fIn :
        l = line_in.rstrip().split(";")
        id_edge_new = str(l[3])
        if int(id_edge_new) <> int(id_edge_actual) :
            line_out = "9999 9999 9999" + "\n"
            fOut.write( line_out )
            id_edge_actual = id_edge_new
        line_out = str(l[0]) + " " + str(l[1]) + " " + str(l[2]) + "\n"
        fOut.write( line_out )
    fIn.close()
    fOut.close()

def cmdop_coordinate_conversion_hull ( logger, hull_file_in, edges_file_tmp, epsg_code_in, epsg_code_out, etrsyear, wkt_in, wkt_out, hull_file_tmp_conv ) :
    """"Function to execute coordinate conversion with Makegrid on cmdop edges file"""
    cmdop_write_edges_from_cmdopfile ( hull_file_in, edges_file_tmp )
    tmp_dir  = os.path.dirname(edges_file_tmp)
    tmp_file = os.path.basename(edges_file_tmp)
    output_file_name = makegrid_geo_conv (logger, tmp_file, tmp_dir, epsg_code_in, epsg_code_out, None, None, 0, 1, etrsyear, ";", ";", wkt_in, wkt_out, None, None, None, None )
    cmdop_write_edges_to_cmdopfile ( output_file_name, hull_file_tmp_conv  )

def cmdop_generate_32bit_geotif ( DbConnection, logger, file_in, file_out, no_data_value) :
    try :
        logger.info("Running cmdop_exportsurface")
        command = UNLOADSDFILE + " -in " + "\"" + file_in + "\"" + " -out " + "\"" + file_out + "\"" + " -format geotiff" + " -nodata " + str(no_data_value)
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
    except Exception, err:
        logger.critical( "Generate 32 bit geotif failed:ERROR: %s\n" % str(err))
        raise

def cmdop_generate_rgba_geotif ( DbConnection, logger, tif_file_in, sd_file_in, file_out) :
    try :
        logger.info("Running cmdop_imageconvert")
        file_tmp = file_out + str(".tmp")
        command = IMAGECONVERT + " -in " + "\"" + tif_file_in + "\"" + " -out " + "\"" + file_tmp + "\"" + " -intype tif -outtype tif -cf rgba"
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
        logger.info("Running cmdop_imageingester")
        command = IMAGEINGESTER + " -in " + "\"" + file_tmp + "\"" + " -sd " + "\"" + sd_file_in + "\"" +  " -out " + "\"" + file_out + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
        os.remove( file_tmp )
    except Exception, err:
        logger.critical( "Generate rgba geotif failed:ERROR: %s\n" % str(err))
        raise

def cmdop_shader ( DbConnection, logger, sd_file_in, colormap_in ):
    try :
        logger.info("Running cmdop_shadere")
        command = SHADER + " -in " + "\"" + sd_file_in + "\"" + " -out " + "\"" + sd_file_in + "\"" + " -cmap " + "\"" + colormap_in + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
    except Exception, err:
        logger.critical( "Apply colormap failed:ERROR: %s\n" % str(err))
        raise

def cmdop_surfacedifference ( DbConnection, logger, sd_file_in_1, sd_file_in_2, sd_file_out ):
    try :
        logger.info("Running cmdop_shadere")
        command = SURFACEDIFFERENCE + " -surf1 " + "\"" + sd_file_in_1 + "\"" + " -surf2 " + "\"" + sd_file_in_2 + "\"" + " -out " + "\"" + sd_file_out + "\"" + " -mode difference"
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
    except Exception, err:
        logger.critical( "Apply colormap failed:ERROR: %s\n" % str(err))
        raise

####################################
# CGAL functions                    #
####################################

#def Point_2_str(self):
    #return "Point_2"+str((self.x(), self.y()))
    ## now we turn it into a member function
#Point_2.__str__ = Point_2_str

#def cgal_generate_hull_edges ( DbConnection, logger, file_in, gap_radius ) :
    #"""Function to generate edges of hull using cgal"""
    #try :
        #logger.info("Generate edges of hull")

        ## Count nr of lines in file
        #nr_of_lines = BathyToolsLib.get_nr_of_lines ( logger, file_in )

        ## Skip datapoints when file is too big to handle 
        #if int(nr_of_lines) > int( MAX_NR_OF_LINES ) : 
            #step = round(float(nr_of_lines)/float(MAX_NR_OF_LINES))
        #else :
            #step = 1

        ## Read points from file into array
        #list_of_points = []
        #i = 0
        #file = open(file_in, 'r')
        #for line in file :
            #i = i + 1
            #if i % step == 0 :
                #l = line.rstrip().split()
                #x = float(l[0])
                #y = float(l[1])
                #list_of_points.append(Point_2(x,y))
        #file.close()
        #logger.info( str(i) + " points read from file")

        ## Construct TIN and generate alpha shape; ? is the squared radius of the carving spoon.
        #logger.info("Start hull generation from TIN using gap radius of " + str(gap_radius) )
        #min_gap_area = gap_radius ** 2.0
        #tin = Alpha_shape_2()
        #tin.make_alpha_shape(list_of_points)
        #tin.set_mode(Alpha_shape_2.Mode.REGULARIZED)
        #tin.set_alpha(min_gap_area)
        #alpha_shape_edges = []
        #for it in tin.alpha_shape_edges:
            #alpha_shape_edges.append(tin.segment(it))
        #nr_of_edges = len(alpha_shape_edges)
        #logger.info( str(nr_of_edges) + " edges generated")
        #if int(nr_of_edges) > int(MAX_NR_OF_EDGES) :
            #logger.critical( "Too many gaps; Regenerate hull with larger link distance")
            #raise

        ## Extract edges from TIN
        #logger.info("Extract edges from TIN")
        #edges = []
        #id = 0
        #for it in tin.alpha_shape_edges:
            #id = id + 1
            #x_coor_start = tin.segment(it).vertex(0).x()
            #y_coor_start = tin.segment(it).vertex(0).y()
            #x_coor_end   = tin.segment(it).vertex(1).x()
            #y_coor_end   = tin.segment(it).vertex(1).y()
            #edges.append((id, x_coor_start, y_coor_start, x_coor_end, y_coor_end))

        ## Return array with edges
        #return edges

    #except Exception, err:
        #logger.critical( "Genereate hull edges failed:ERROR: %s\n" % str(err))
        #raise

#def cgal_write_edges_to_file ( edges_list, edges_file ) :
    #""""Function to write edges to file"""
    #fOut = open(edges_file, 'w')
    #for index in range(len(edges_list)):
        #edge_record = edges_list[index]
        #row_start   = str(edge_record[1]) + ";" + str(edge_record[2]) + ";" + str(edge_record[0])
        #row_end     = str(edge_record[3]) + ";" + str(edge_record[4]) + ";" + str(edge_record[0])
        #fOut.write( row_start + "\n" )
        #fOut.write( row_end   + "\n" )
    #fOut.close

#def cgal_write_edges_to_list ( edges_file, edges_list ) :
    #""""Function to write edges from file to list"""
    #i = 0
    #fOut = open(edges_file, 'r')
    #for line in fOut :
        #edge = line.rstrip().split(";")
        #i = i + 1
        #if i % 2 != 0 :
            #x_coor_start = float(edge[0])
            #y_coor_start = float(edge[1])
            #id           = float(edge[2])
        #if i % 2 == 0 :
            #x_coor_end = float(edge[0])
            #y_coor_end = float(edge[1])
            #id         = float(edge[2])
            #edges_list.append((id, x_coor_start, y_coor_start, x_coor_end, y_coor_end))

#def cgal_coordinate_conversion_edges ( logger, edges_list_in, edges_file_tmp, epsg_code_in, epsg_code_out, etrsyear, wkt_in, wkt_out, hull_edges_conv ) :
    #""""Function to execute coordinate conversion with Makegrid on edges list"""
    #cgal_write_edges_to_file ( edges_list_in, edges_file_tmp )
    #tmp_dir  = os.path.dirname(edges_file_tmp)
    #tmp_file = os.path.basename(edges_file_tmp)
    #output_file_name = makegrid_geo_conv (logger, tmp_file, tmp_dir, epsg_code_in, epsg_code_out, None, None, 0, 1, etrsyear, ";", ";", wkt_in, wkt_out, None, None, None, None )
    #cgal_write_edges_to_list ( output_file_name, hull_edges_conv )

####################################
# MAKEGRID functions               #
####################################

def makegrid_separation_model_file ( DbConnection, logger, temp_dir, vert_ref_id, verdat_from, verdat_to ) :
    """Generate separation model esri grid or get name of algorithm to apply"""
    try :
        logger.info( "Check for generation of separation model file" )

        sep_model_name = "mtj"

        # You have either a vert_ref_id or a combination of verdat_from and verdat_to
        if not verdat_from :
            verdat_from = BathyDbLib.VERTICAL_DATUM_UNKNOWN
        if not verdat_to :
            verdat_to = BathyDbLib.VERTICAL_DATUM_UNKNOWN

        # First check if you need to generate a separation model
        generate_sep_model = True
        if not vert_ref_id and ( int(verdat_from) == int(BathyDbLib.VERTICAL_DATUM_UNKNOWN) or int(verdat_to) == int(BathyDbLib.VERTICAL_DATUM_UNKNOWN) ) :
            generate_sep_model = False
            sep_model_id_init  = NO_SEP_MODEL_AVAILABLE
        if not vert_ref_id and ( int(verdat_from) == int(verdat_to) ) :
            generate_sep_model = False
            sep_model_id_init  = NO_SEP_MODEL_REQUIRED
        if vert_ref_id and int(vert_ref_id) == int(BathyDbLib.SEP_MODEL_UNKONWN) :
            generate_sep_model = False
            sep_model_id_init  = NO_SEP_MODEL_REQUIRED

        # Check if separation model exists for verdat_from and verdat_to, if not do not generate separation model
        if generate_sep_model and not vert_ref_id :
            sep_model_id  = None
            verdat_in_id  = verdat_from
            verdat_out_id = verdat_to
            attributes = {}
            attributes[ BathyDbLib.VERDAT_IN_COL ]  = verdat_in_id
            attributes[ BathyDbLib.VERDAT_OUT_COL ] = verdat_out_id
            attributes[ BathyDbLib.DISABLED_COL]    = "F"
            result_list = DbConnection.query_object ( BathyDbLib.SEP_MOD_CLASS_ID, attributes )
            if result_list :
                for row in result_list :
                    sep_model_id = row
            if not sep_model_id :
                generate_sep_model = False
                sep_model_id_init  = NO_SEP_MODEL_AVAILABLE

        # Get separation model and verdat_in and verdat_out IDs, check is vertical reference is not unknown
        if generate_sep_model  :
            logger.info( "Get separation model definition" )
            if vert_ref_id :
                # Get sep model attributes based on vertical reference model
                attributes    = [ BathyDbLib.SEP_MODEL_ID_COL ]
                values        = DbConnection.get_obj_attributes ( BathyDbLib.GEODETIC_VERTI_CLASS_ID, vert_ref_id, attributes )
                sep_model_id  = values[0]
                if sep_model_id :
                    attributes    = [ BathyDbLib.VERDAT_IN_COL, BathyDbLib.VERDAT_OUT_COL, BathyDbLib.HASFILE_COL, BathyDbLib.ISALGORITHM_COL ]
                    values        = DbConnection.get_obj_attributes ( BathyDbLib.SEP_MOD_CLASS_ID, sep_model_id, attributes )
                    verdat_in_id  = values[0]
                    verdat_out_id = values[1]
                    hasfile       = values[2]
                    isalgorithm   = values[3]
                else :
                    # Make verdat_in - verdat_out so that no separation model is generated
                    verdat_in_id  = BathyDbLib.VERDAT_UNKNOWN
                    verdat_out_id = verdat_in_id

            else :
                # Get sep model attributes based on verdat in and out
                attributes    = [ BathyDbLib.VERDAT_IN_COL, BathyDbLib.VERDAT_OUT_COL, BathyDbLib.HASFILE_COL, BathyDbLib.ISALGORITHM_COL ]
                values        = DbConnection.get_obj_attributes ( BathyDbLib.SEP_MOD_CLASS_ID, sep_model_id, attributes )
                verdat_in_id  = values[0]
                verdat_out_id = values[1]
                hasfile       = values[2]
                isalgorithm   = values[3]

            # Get sep model ID with link to data file (requery with verdat_in = out and verdat_in = out when hasFile = F)
            # Check if verdat in and verdat out are different
            if int(verdat_in_id) <> int(verdat_out_id) :
                if str(hasfile) == "F" :
                    attributes = {}
                    attributes[ BathyDbLib.VERDAT_IN_COL ]  = verdat_out_id
                    attributes[ BathyDbLib.VERDAT_OUT_COL ] = verdat_in_id
                    result_list = DbConnection.query_object ( BathyDbLib.SEP_MOD_CLASS_ID, attributes )
                    if result_list :
                        for row in result_list :
                            sepmodel_id_hasfile = row
                    direction = int(-1)
                if str(hasfile) == "T" :
                    direction = int(1)
                    sepmodel_id_hasfile = sep_model_id

                # Get separation model name and gridsize
                attributes = {}
                attributes[ BathyDbLib.SEP_MOD_ID_COL ]  = sepmodel_id_hasfile
                result_list = DbConnection.query_object ( BathyDbLib.SEP_MOD_FILE_CLASS_ID, attributes )
                if result_list :
                    for row in result_list :
                        sepmodel_file_id = row
                attributes     = [ BathyDbLib.SEP_MOD_ALGO_COL, BathyDbLib.SEP_MOD_GRIDSIZE, BathyDbLib.SEP_MOD_ALG_COL ]
                values         = DbConnection.get_obj_attributes ( BathyDbLib.SEP_MOD_FILE_CLASS_ID, sepmodel_file_id, attributes )
                sep_model_name = values[0]
                grid_size      = values[1]
                algorithm_id   = values[2]
                if not algorithm_id :
                    algorithm_id = 0
                if not grid_size :
                    grid_size = 0

                # Extract separation model files (shape and data) from database
                logger.info( "Separation model is algorithm = " + str(isalgorithm) )
                sep_model_name = temp_dir + "\\" + str(verdat_in_id) + "_" + str(verdat_out_id) + FILE_EXT_ASC
                sep_model_shp  = temp_dir + "\\" + str(verdat_in_id) + "_" + str(verdat_out_id) + FILE_EXT_SHP
                if not os.path.exists( sep_model_name ) or int(os.path.getsize( sep_model_name )) == int(0) :
                    fOut = open(sep_model_name, 'w')
                    logger.info("Start writing files for seperation model id = " + str(sepmodel_id_hasfile) )
                    DbConnection.write_separation_model_file ( fOut, sep_model_shp, sepmodel_id_hasfile, isalgorithm )
                    fOut.close()
            
            else :
                sepmodel_id_hasfile = NO_SEP_MODEL_REQUIRED
                sep_model_name      = NO_SEP_MODEL_REQUIRED
                direction           = 0
                grid_size           = 0
                algorithm_id        = 0

        else :
            sepmodel_id_hasfile = sep_model_id_init
            sep_model_name      = sep_model_id_init
            direction           = 0
            grid_size           = 0
            algorithm_id        = 0

        logger.info( "Separation model " + str(sepmodel_id_hasfile) + " file " + str(sep_model_name) + " generated with direction " + str(direction) + " and gridsize " + str(grid_size) )
        logger.info( "Algorithm ID = " + str(algorithm_id) )
        return sep_model_name, direction, grid_size, algorithm_id

    except Exception, err:
        logger.critical( "Genereate separation model file failed:ERROR: %s\n" % str(err))
        if os.path.exists( sep_model_name ) :
            os.remove(sep_model_name)
        raise


def makegrid_write_file_list ( logger, input_file, temp_dir, ver_dat_in, wkt_in, sep_model_file, direction, grid_size, algorithm_id, id, name) :
    """Make fileList file for makegrid with inputfile and geodetic charcteristics of input file"""
    try :
        logger.info ( "Write FileList file for Makegrid" )
        if not sep_model_file :
            sep_model_file = NO_SEP_MODEL_REQUIRED
        if not direction :
            direction = 0
        if not grid_size :
            grid_size = 0
        if not algorithm_id :
            algorithm_id = 0
        if not id :
            id = 0
        if not name :
            name = 0
        file_name  = temp_dir + "\\" + MG_FILELIST_FILE_VAL
        input_file = temp_dir + "\\" + input_file
        if os.path.exists( file_name ) :
            os.remove( file_name )
        fOut = open(file_name, 'w')
        # OLD: line = input_file + MG_PIPE_SEPARATOR + MG_DEFAULT_IM_TYPE_VAL + MG_PIPE_SEPARATOR + str(ver_dat_in) + MG_PIPE_SEPARATOR + str(wkt_in)+ MG_PIPE_SEPARATOR + "0" + "\n"
        line = input_file + MG_PIPE_SEPARATOR + MG_DEFAULT_IM_TYPE_VAL + MG_PIPE_SEPARATOR + str(sep_model_file) + MG_PIPE_SEPARATOR + str(direction) + MG_PIPE_SEPARATOR + str(grid_size) + MG_PIPE_SEPARATOR + str(wkt_in)+ MG_PIPE_SEPARATOR + "0" + MG_PIPE_SEPARATOR + str(id)+ MG_PIPE_SEPARATOR + str(name) + MG_PIPE_SEPARATOR + str(algorithm_id) + "\n"
        logger.info( line )
        fOut.write( line )
        fOut.close()
        logger.info ( "FileList file for Makegrid is " + file_name )
        return file_name
    except Exception, err:
        logger.critical( "Genereate hull edges failed:ERROR: %s\n" % str(err))
        raise

def makegrid_get_parametervalue_from_file ( logger, parameter_file, parameter ) :
    """Function to get parametervalue from file"""
    try :
        fIn = open(parameter_file,'r')
        for line in fIn:
            if "=" in line:
                l = line.rstrip().split('=')
                if str(l[0]) == str(parameter) :
                    value = str(l[1])
        fIn.close()
        return value
    except Exception, err:
        logger.critical( "Get paraemetervalue from file failed:ERROR: %s\n" % str(err))
        raise

def makegrid_geo_conv (logger, input_file, temp_dir, coord_sys_in, coord_sys_out, ver_dat_in, ver_dat_out, offset, m_factor, etrsyear, delimiter_in, delimiter_out, wkt_in, wkt_out, sep_model_file, direction, grid_size, algorithm_id) :
    # Use makegrid for geodetic conversions
    try :
        logger.info ( "Run Makegrid for geodetic conversions" )

        if not ver_dat_in :
            ver_dat_in = BathyDbLib.VERDAT_UNKNOWN
        if not ver_dat_out :
            ver_dat_out = BathyDbLib.VERDAT_UNKNOWN
        if not sep_model_file :
            sep_model_file = 0
        if not direction :
            direction = 0
        if not grid_size :
            grid_size = 0

        # First make filelist file with file and parameters of input IM
## TO DO: sep_model_file, direction in function makegrid_write_file_list
        #filelist_file_name = makegrid_write_file_list ( logger, input_file, temp_dir, ver_dat_in, coord_sys_in)
        filelist_file_name = makegrid_write_file_list ( logger, input_file, temp_dir, ver_dat_in, wkt_in, sep_model_file, direction, grid_size, algorithm_id, "", "")

        # Now construct Makegrid parameter file
        parameter_file_name = temp_dir + "\\" + MG_PARAMETER_FILE_VAL
        output_file_name    = temp_dir + "\\" + MG_OUTPUT_FILE_ASC_VAL
        if os.path.exists( parameter_file_name ) :
            os.remove( parameter_file_name )        
        if os.path.exists( output_file_name ) :
            os.remove( output_file_name ) 
        fOut = open(parameter_file_name, 'w')
        fOut.write ("# Automatically created configuration file for Makegrid" + "\n" )
        fOut.write ("\n" )
        fOut.write ("# System parameters" + "\n" )
        fOut.write ( MG_VERBOSE + "=" + MG_VERBOSE_VAL + "\n" )
        fOut.write ( MG_OUTPUTFILE + "=" + output_file_name + "\n" )
        fOut.write ( MG_TEMPPATH + "=" + temp_dir + "\n" )
        fOut.write ( MG_FILELIST + "=" + filelist_file_name + "\n" )
        fOut.write ("\n" )
        fOut.write ("# Product defintion parameters" + "\n" )
        fOut.write ( MG_PRODUCTFORMAT + "=" + MG_PRODUCTASCII_VAL + "\n" )
        fOut.write ( MG_INPUTDELIMITER + "=" + str(delimiter_in) + "\n" )
        fOut.write ( MG_OUTPUTDELIMITER + "=" + str(delimiter_out) + "\n" )
        fOut.write ( MG_DECIMALSEP + "=" + MG_DECIMALSEP_VAL + "\n" )
        fOut.write ( MG_FACTOR + "=" + str(m_factor) + "\n" )   
        fOut.write ( MG_OFFSET + "=" + str(offset) + "\n" )   
        fOut.write ( MG_EPSGCODEOUT + "=" + str(coord_sys_out) + "\n" )
        fOut.write ( MG_WKT_OUT + "=" + str(wkt_out) + "\n" )
        fOut.write ( MG_ETRSYEAR + "=" + str(etrsyear) + "\n"  )
        fOut.write ( MG_VERDATOUT + "=" + str(ver_dat_out) + "\n" )          
        fOut.write ( MG_XYZFORMAT + "=" + MG_XYZFORMAT_VAL + "\n" )
        fOut.close()

        # Get the name of the generated file with converted coordinates
        output_file_name = makegrid_get_parametervalue_from_file ( logger, parameter_file_name, MG_OUTPUTFILE )

        # Start running Makegrid
        logger.info("Start " + MAKEGRID + " with parameter file " + parameter_file_name )
        command = MAKEGRID + " " + "\""+ parameter_file_name + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )

        # Return outputfile name
        return output_file_name

    except Exception, err:
        logger.critical( "Run Makegrid for geodetic conversions failed:ERROR: %s\n" % str(err))
        raise

def makegrid_write_param_file ( DbConnection, logger, ParameterList, temp_dir, input_file ) :
    """Function to generate parameter file for Makegrid from parameter list"""
    try :
        logger.info ( "Generate parameter file for Makegrid from parameter list" )

        # If no tempdir is given, use temp dir from parameter file
        if not temp_dir :
            temp_dir_path = ParameterList [ BathyToolsLib.TEMPDIR ]
            # Now add directory to outputfile
            ParameterList [ BathyToolsLib.OUTPUTFILE ] = ParameterList [ BathyToolsLib.OUTPUTDIRECTORY ] + "/" + ParameterList [ BathyToolsLib.OUTPUTFILE ]
            # Remove last \ or / from path
            if str(temp_dir_path[-1]) == "\\" or str(temp_dir_path[-1]) == "/" :
                temp_dir = temp_dir_path[:-1]

        # Set parameterfile name
        parameter_file_name = temp_dir + "\\" + MG_PARAMETER_FILE_VAL

        # For postprocessing, first check if gridsize has a value, if not Productformat is always Ascii XYZ
        if input_file :
            if not ParameterList [ BathyToolsLib.PARAMETER_GRIDSIZE ] :
                ParameterList [ BathyToolsLib.PARAMETER_PROD_FORMAT ] = MG_PRODUCTASCII_VAL
                output_file_name    = temp_dir + "\\" + MG_OUTPUT_FILE_ASC_VAL
            else :
                output_file_name    = temp_dir + "\\" + MG_OUTPUT_FILE_GRD_VAL

        # Parameterfile
        if os.path.exists( parameter_file_name ) :
            os.remove( parameter_file_name )
        logger.info ( "Parameter file is: " + str(parameter_file_name) )

        # First retrieve attributes used for processing parameter list
        object_class_id = int ( ParameterList [ BathyToolsLib.PARAMETER_PROCESS_ID ] )
        method          = str ( ParameterList [ BathyToolsLib.PARAMETER_METHOD ] )

        # Write parameters to parameter file
        fOut = open(parameter_file_name, 'w')
        fOut.write ("# Automatically created configuration file for Makegrid" + "\n" )
        fOut.write ("# -------- Parameters extracted from parameterlist ---------" + "\n" )
        fOut.write ("\n" )
        fOut.write ( MG_VERBOSE + "=" + MG_VERBOSE_VAL + "\n" )
        fOut.write ( MG_TEMPPATH + "=" + temp_dir + "\n" )
        fOut.write ( MG_DBUSER + "=" + str( ParameterList [ BathyToolsLib.DBUSER ] ) + "\n" )
        fOut.write ( MG_DBPASS + "=" + str( ParameterList [ BathyToolsLib.DBPASSWORD ]) + "\n" )
        fOut.write ( MG_DBCNXT + "=" + str( ParameterList [ BathyToolsLib.DBCONNECT ]) + "\n" )

        # Loop through parameter list and write to parameter file
        for parameter in ParameterList :
            logger.debug ( "Parameter " + str(parameter) + " = " + str(ParameterList [ parameter ]) )
            # Check if parameter has a value
            if ParameterList [ parameter ] :
                # First special treatment of geodetic parameters
                if str(parameter) == str(BathyToolsLib.PARAMETER_EPSGCODEOUT) :
                    # Get epsgcode
                    if str( ParameterList[ BathyToolsLib.PARAMETER_GEN_CONTOURS] ) == "T"  or str ( ParameterList[ BathyToolsLib.PARAMETER_GEN_SPOTS ] ) == "T" :
                        # For contour and spot sounding generation output is always epsg_code DB (no coordinate conversion)
                        epsg_code_out = DbConnection.get_epsg_code_db()
                        wkt_out       = str(DbConnection.get_wkt_epsg_code( epsg_code_out ) )
                    else :
                        value         = int( ParameterList [ parameter ] )
                        epsg_code_out = BathyToolsLib.get_epsg_code ( DbConnection, logger, value )
                        wkt_out       = str(DbConnection.get_wkt_coord_sys_id ( value ) )
                    fOut.write( str(parameter) + "=" + str(epsg_code_out) + "\n" )
                    fOut.write( MG_WKT_OUT + "=" + str(wkt_out) + "\n" )
                elif str(parameter) == str(BathyToolsLib.PARAMETER_VERDATOUT) :
                    # Get vertical reduction parameters
                    value = int( ParameterList [ parameter ] )
                    ver_dat_in, ver_dat_out, offset, m_factor = BathyToolsLib.get_separation_model ( DbConnection, logger, value )
                    fOut.write( str(parameter) + "=" + str(ver_dat_out) + "\n" )
                    fOut.write( MG_FACTOR + "=" + str(m_factor) + "\n" )
                    fOut.write( MG_OFFSET + "=" + str(offset) + "\n" )
                else :
                    # Second determine the attribute type:
                    # - Boolean: if T then write parameter in parameter file
                    # - Domain:  Get domain value based on domain ID when parameter is not SurveyId or not CM ID
                    # - Domain:  If domain is PRODUCTMODE and value = contours => product mode wordt CM
                    # When parameter is no database parameter function gives an exception, set attribute type to no database attribute
                    no_database_parameter_list = [ BathyToolsLib.OUTPUTFILE, BathyToolsLib.DBUSER, BathyToolsLib.DBPASSWORD, BathyToolsLib.DBCONNECT, BathyToolsLib.OUTPUTDIRECTORY, BathyToolsLib.TEMPDIR, BathyToolsLib.LOGLEVEL, BathyToolsLib.TASKID ]
                    if parameter not in no_database_parameter_list :
                        attribute_type = DbConnection.get_attribute_type ( object_class_id, parameter )
                    else :
                        attribute_type = BathyDbLib.ATYPE_NO_DB
                    #try :
                    #    attribute_type = DbConnection.get_attribute_type ( object_class_id, parameter )
                    #except:
                    #    attribute_type = BathyDbLib.ATYPE_NO_DB
                    logger.debug ( "Attribute type = " + str(attribute_type) )
                    if int(attribute_type) == int(BathyDbLib.ATYPE_BOOLEAN) :
                        if str( ParameterList [ parameter ] ) == "T" :
                            fOut.write( str(parameter) + "\n" )
                    elif int(attribute_type) == int(BathyDbLib.ATYPE_DOMAIN) and str(parameter) <> str(BathyToolsLib.PARAMETER_SURVEY_ID) and str(parameter) <> str(BathyToolsLib.PARAMETER_CM_ID) and str(parameter) <> str(BathyToolsLib.PARAMETER_VERDAT_PROD)  :
                        if str(parameter) == str(MG_PRODUCTMODE) and int(ParameterList [ parameter ]) == int( BathyDbLib.CONTOUR_MODE )  :
                            value = int( BathyDbLib.CM_MODE )
                        elif str(parameter) == str(MG_PRODUCTFORMAT) and  ( int(ParameterList [ parameter ]) == int( BathyDbLib.PRODUCT_SDFILE ) or int( ParameterList[ BathyToolsLib.PARAMETER_PRODUCTFORMAT] )== int(BathyDbLib.PRODUCT_32BIT_GEOTIFF) or int( ParameterList[ BathyToolsLib.PARAMETER_PRODUCTFORMAT] )== int(BathyDbLib.PRODUCT_RGBA_GEOTIFF) ) :
                            value = int( BathyDbLib.PRODUCT_ESRI_ASCII_GRID )
                        elif str(parameter) == str(MG_PRODUCTFORMAT) and ( int(ParameterList [ parameter ]) == int( BathyDbLib.PRODUCT_EMODNET_NETCDF ) ) :
                            value = int( BathyDbLib.PRODUCT_EMODNET_ASCII )
                        else :
                            value = int ( ParameterList [ parameter ] )
#                        value = int ( ParameterList [ parameter ] )
                        domain_value = DbConnection.get_domain_value ( object_class_id, parameter, value )
                        fOut.write( str(parameter) + "=" + str(domain_value) + "\n" )
                    else :
                        fOut.write( str(parameter) + "=" + str( ParameterList [ parameter ] ) + "\n" )

        # If not postprocessing, 
        if not input_file :
            # for contour and spot sounding generation add product format and product type
            if str( ParameterList[ BathyToolsLib.PARAMETER_GEN_CONTOURS] ) == "T"  or str ( ParameterList[ BathyToolsLib.PARAMETER_GEN_SPOTS ] ) == "T" :
                # For contours and spot sounings product format is always Ascii xyz Grid
                ParameterList[ BathyToolsLib.PARAMETER_PRODUCTFORMAT] = int( BathyDbLib.PRODUCT_ASCII )
                fOut.write( str(BathyToolsLib.PARAMETER_PROD_FORMAT) + "=" + str( MG_PRODUCTASCIIGRID_VAL ) + "\n" )
                # For contours and spot sounings product xyz is always x y z
                fOut.write( str(BathyToolsLib.PARAMETER_XYZ_FORMAT) + "=" + str( MG_XYZFORMAT_SDS_VAL ) + "\n" )
            # For backwards compatibility add verdatout parameter
            #fOut.write( MG_VERDATOUT + "=" + str(BathyDbLib.VERDAT_UNKNOWN) + "\n" )

        # For postprocessing parameter file add additional attributes (input file is present)
        if input_file :

            logger.info ( "Add postprocessing parameters" )

            fOut.write ("# -------- Parameters added for postprocessing ---------" + "\n" )

            # Get geodetic parameters from IM
            im_id = ParameterList [ BathyToolsLib.PARAMETER_IM_ID ]
            attributes = [ BathyDbLib.IM_COORD_SYS_SRC_COL, BathyDbLib.IM_SEP_MODEL_COL, BathyDbLib.IM_ETRSYEAR_COL, BathyDbLib.IM_ID, BathyDbLib.IM_NAME ]
            values     = DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, im_id, attributes )
            coord_sys_id   = int(values[0])
            vert_ref_id    = int(values[1])
            etrs_year      = values[2]
            im_id          = int(values[3])
            im_name        = values[4]
            epsg_code_in   = int(BathyToolsLib.get_epsg_code ( DbConnection, logger, coord_sys_id ))
            wkt_in         = str(DbConnection.get_wkt_coord_sys_id ( coord_sys_id ) )
            epsg_code_out  = int(DbConnection.get_epsg_code_db ())
            wkt_out        = str(DbConnection.get_wkt_epsg_code( epsg_code_out ) )
            ver_dat_in, ver_dat_out, offset, m_factor = BathyToolsLib.get_separation_model ( DbConnection, logger, vert_ref_id )
            # Check for non-existing verdat, use default
            if not ver_dat_in :
                ver_dat_in = BathyDbLib.VERDAT_UNKNOWN
            if not ver_dat_out :
                ver_dat_out = BathyDbLib.VERDAT_UNKNOWN

            # Write filelist file with input geodetic settings


##          ## TO DO:
##          ## sep_model_file, direction, grid_size = makegrid_separation_model_file ( DbConnection, logger, temp_dir, vert_ref_id )
##          ## sep_model_file, direction in function makegrid_write_file_list
            # filelist_file_name = makegrid_write_file_list ( logger, input_file, temp_dir, ver_dat_in, epsg_code_in )
            
            sep_model_file, direction, grid_size, algorithm_id = makegrid_separation_model_file ( DbConnection, logger, temp_dir, vert_ref_id, None, None )
            filelist_file_name                                 = makegrid_write_file_list ( logger, input_file, temp_dir, ver_dat_in, wkt_in, sep_model_file, direction, grid_size, algorithm_id, im_id, im_name)
            fOut.write ( MG_FILELIST + "=" + filelist_file_name + "\n" )

            # Write geodetic output parametetrs
            fOut.write ( MG_FACTOR + "=" + str(m_factor) + "\n" )
            fOut.write ( MG_OFFSET + "=" + str(offset) + "\n" )
            fOut.write ( MG_VERDATOUT + "=" + str(ver_dat_out) + "\n" )
            fOut.write ( MG_EPSGCODEOUT + "=" + str(epsg_code_out) + "\n" )
            fOut.write ( MG_WKT_OUT + "=" + str(wkt_out) + "\n" )
            
            # Get ertsyear for etrs89
            if int(epsg_code_out) == int(BathyToolsLib.EPSGCODE_ETRS89) :
                fOut.write ( MG_ETRSYEAR + "=" + str(etrs_year) + "\n"  )
            else : 
                fOut.write ( MG_ETRSYEAR + "=" + "\n"  )

            # Write xyz format
            fOut.write ( "--------Outputfile generated in code ---------\n" )

            # Write outputfile parameter
            fOut.write ( MG_OUTPUTFILE + "=" + output_file_name + "\n" )

            # Check if XyzFormat must be set
            if str(ParameterList [ BathyToolsLib.PARAMETER_PROD_FORMAT ]) == str(MG_PRODUCTASCII_VAL) :
                fOut.write ( BathyToolsLib.PARAMETER_XYZ_FORMAT + "=" + MG_XYZFORMAT_VAL + "\n"  )

        # Finally close file
        fOut.close()

        # Return filename
        return parameter_file_name

    except Exception, err:
        logger.critical( "Generate parameter file for Makegrid from parameter list failed:ERROR: %s\n" % str(err))
        raise

def makegrid_postprocessing ( DbConnection, logger, ParameterList, temp_dir, input_file ) :
    """Run Makegrid for postprocessing"""
    try :
        logger.info ( "Run Makegrid for postprocessing" )

        # Construct parameter file for Makegrid
        parameter_file_name = makegrid_write_param_file ( DbConnection, logger, ParameterList, temp_dir, input_file )

        # Get the name of the generated file with converted coordinates
        output_file_name = makegrid_get_parametervalue_from_file ( logger, parameter_file_name, MG_OUTPUTFILE )

        # Start running Makegrid
        logger.info("Start " + MAKEGRID + " with parameter file " + parameter_file_name )
        command   = MAKEGRID + " " + "\""+ parameter_file_name + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )

        # Return name of outputfile
        logger.info("Outputfile " + str(output_file_name) )
        return output_file_name

    except Exception, err:
        logger.critical( "Run Makegrid for postprocessing failed:ERROR: %s\n" % str(err))
        raise

#########################################################
# Nieuwe makegrid executables for EMODNET
#########################################################

def makegrid_generate_hull ( DbConnection, logger, input_file, output_file ) :
    """Run Makegrid to generate hul"""
    try :
        logger.info ( "Run Makegrid to generate hull" )  
        # usage: MakeHull.exe <inputfile> <outputfile>
        command = MAKEGRIDHULL + " " + "\"" + input_file + "\"" + " " + "\"" + output_file + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )        
    except Exception, err:
        logger.critical( "Run Makegrid to generate hull failed:ERROR: %s\n" % str(err))
        raise

def makegrid_generate_emodnet_grid ( DbConnection, logger, input_file, output_file, cdi_record ) :
    """Run Makegrid to generate hul"""
    try :
        logger.info ( "Run Makegrid to generate EMODNET grid" )  
        # usage: MakeHull.exe <inputfile> <outputfile> <cdi_record>
        command = MAKEGRIDEMODNET + " " + "\"" + input_file + "\"" + " " + "\"" + output_file + "\"" + " " + "\"" + str(cdi_record) + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )        
    except Exception, err:
        logger.critical( "Run Makegrid to EMODNET grid failed:ERROR: %s\n" % str(err))
        raise
    
def makegrid_generate_esri_ascii_grid ( DbConnection, logger, input_file, output_file ) :
    """Run Makegrid to generate Esri Ascii grid"""
    try :
        logger.info ( "Run Makegrid to generate Esri Ascii grid" )  
        # usage: MakeEsriAsciiGrid.exe <inputfile> <outputfile>
        command = MAKEGRIDESRIGRID + " " + "\"" + input_file + "\"" + " " + "\"" + output_file + "\"" 
        exit_code = BathyToolsLib.run_oscommand ( logger, command )        
    except Exception, err:
        logger.critical( "Run Makegrid to generate Esri Ascii grid failed:ERROR: %s\n" % str(err))
        raise    

def makegrid_generate_geotif ( DbConnection, logger, input_file, output_file, colour_file ) :
    """Run Makegrid to generate Esri Ascii grid"""
    try :
        logger.info ( "Run Makegrid to generate Esri Ascii grid" )  
        # usage: MakeGeoTIFF.exe <inputfile> <outputfile> <colourfile>
        command = MAKEGRIDGEOTIF + " " + "\"" + input_file + "\"" + " " + "\"" + output_file + "\"" + " " + "\"" + colour_file + "\"" 
        exit_code = BathyToolsLib.run_oscommand ( logger, command )        
    except Exception, err:
        logger.critical( "Run Makegrid to generate Esri Ascii grid failed:ERROR: %s\n" % str(err))
        raise 

def makegrid_export ( DbConnection, logger, ParameterList, temp_dir ) :
    """Run Makegrid for product generation"""
    try :
        logger.info ( "Run Makegrid for product generation" )

        # Construct parameter file for Makegrid (input file = None)
        parameter_file_name = makegrid_write_param_file ( DbConnection, logger, ParameterList, None, None )

        # Copy parameterfile to
        copy_file_name  = ParameterList [ BathyToolsLib.OUTPUTFILE ] + ".makegrid_parameter"
        shutil.copyfile(parameter_file_name, copy_file_name)

        # Start running Makegrid
        logger.info("Start " + MAKEGRID + " with parameter file " + parameter_file_name )
        command = MAKEGRID + " " + "\""+ parameter_file_name + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )

        # Continue when exit_code is zero
        if int(exit_code) == 0 :
            # Convert ESRI ASCII Grid to SD file or Geotiff
            if int( ParameterList[ BathyToolsLib.PARAMETER_PRODUCTFORMAT] )== int(BathyDbLib.PRODUCT_SDFILE) or int( ParameterList[ BathyToolsLib.PARAMETER_PRODUCTFORMAT] )== int(BathyDbLib.PRODUCT_32BIT_GEOTIFF) or int( ParameterList[ BathyToolsLib.PARAMETER_PRODUCTFORMAT] )== int(BathyDbLib.PRODUCT_RGBA_GEOTIFF) :
                logger.info("Generate SD file")
                l_input_file      = ParameterList [ BathyToolsLib.OUTPUTFILE ] + FILE_EXT_ASC
                l_sd_file         = ParameterList [ BathyToolsLib.OUTPUTFILE ] + FILE_EXT_SD
                l_epsg_code       = BathyToolsLib.get_epsg_code ( DbConnection, logger, ParameterList[ BathyToolsLib.PARAMETER_EPSGCODEOUT ] )
                l_no_data_value   = int( ParameterList[ BathyToolsLib.PARAMETER_NULLVALUE ] )
                cmdop_gasciitoscalar ( DbConnection, logger, l_input_file, l_sd_file, l_epsg_code, l_no_data_value )
                os.remove( l_input_file )
                # Apply colormap if you generate SD file or RGBA Geotiff
                if int( ParameterList[ BathyToolsLib.PARAMETER_PRODUCTFORMAT] )== int(BathyDbLib.PRODUCT_SDFILE) or int( ParameterList[ BathyToolsLib.PARAMETER_PRODUCTFORMAT] )== int(BathyDbLib.PRODUCT_RGBA_GEOTIFF) :
                    logger.info("Apply color map")
                    l_colormap = ParameterList[ BathyToolsLib.PARAMETER_COLOR_MAP ]
                    if l_colormap :
                        cmdop_shader ( DbConnection, logger, l_sd_file, l_colormap )
                # Convert SD file to Geotiff
                if int( ParameterList[ BathyToolsLib.PARAMETER_PRODUCTFORMAT] )== int(BathyDbLib.PRODUCT_32BIT_GEOTIFF) or int( ParameterList[ BathyToolsLib.PARAMETER_PRODUCTFORMAT] )== int(BathyDbLib.PRODUCT_RGBA_GEOTIFF) :
                    logger.info("Generate 32 bit GeoTIFF file")
                    l_geotif_file_out = ParameterList [ BathyToolsLib.OUTPUTFILE ] + FILE_EXT_TIF
                    l_geotif32_file   = ParameterList [ BathyToolsLib.OUTPUTFILE ] + "_32" + FILE_EXT_TIF
                    cmdop_generate_32bit_geotif ( DbConnection, logger, l_sd_file, l_geotif32_file, l_no_data_value)
                    if int( ParameterList[ BathyToolsLib.PARAMETER_PRODUCTFORMAT] )== int(BathyDbLib.PRODUCT_RGBA_GEOTIFF) :
                        logger.info("Generate rgba GeoTIFF file")
                        l_geotifrgba_file = ParameterList [ BathyToolsLib.OUTPUTFILE ] + "_rgba" + FILE_EXT_TIF
                        cmdop_generate_rgba_geotif ( DbConnection, logger, l_geotif32_file, l_sd_file, l_geotifrgba_file )
                        os.rename ( l_geotifrgba_file, l_geotif_file_out)
                        os.remove( l_geotif32_file )
                    else :
                        os.rename ( l_geotif32_file, l_geotif_file_out)
                    os.remove( l_sd_file )

            # Make NetCDF EMODNET file
            if int( ParameterList[ BathyToolsLib.PARAMETER_PRODUCTFORMAT] )== int(BathyDbLib.PRODUCT_EMODNET_NETCDF) :
                logger.info("Generate NetCDF EMODNET file")
                l_input_file      = ParameterList [ BathyToolsLib.OUTPUTFILE ] + FILE_EXT_ASCII
                l_netcdf_file_out = ParameterList [ BathyToolsLib.OUTPUTFILE ] + FILE_EXT_NC
                l_gridsize        = ParameterList [ BathyToolsLib.PARAMETER_GRIDSIZE ]
                netcdf_generate_emodnet_grid ( logger, l_input_file, l_netcdf_file_out, l_gridsize, ParameterList )

            # Generate file for contour and spot sounding generation
            if str( ParameterList[ BathyToolsLib.PARAMETER_GEN_CONTOURS] ) == "T"  or str ( ParameterList[ BathyToolsLib.PARAMETER_GEN_SPOTS ] ) == "T" :
                logger.info("Generate file for contour and spot sounding generation")
                # Get the working directory and copy config files to working directory
                l_temp_dir      = BathyToolsLib.get_working_dir( logger, ParameterList [ BathyToolsLib.TEMPDIR ] )
                shutil.copyfile ( SDS_XYZ_CONFIG             , l_temp_dir + "/" + SDS_XYZ_CONFIG       )
                shutil.copyfile ( SDS_AGGR_CONFIG            , l_temp_dir + "/" + SDS_AGGR_CONFIG      )
                shutil.copyfile ( SDS_CONV_CONFIG            , l_temp_dir + "/" + SDS_CONV_CONFIG      )
                shutil.copyfile ( SDS_LINE_7CB_CONFIG        , l_temp_dir + "/" + SDS_LINE_7CB_CONFIG  )
                shutil.copyfile ( SDS_POINT_7CB_CONFIG       , l_temp_dir + "/" + SDS_POINT_7CB_CONFIG )
                shutil.copyfile ( SDS_TILE_CONFIG            , l_temp_dir + "/" + SDS_TILE_CONFIG      )
                shutil.copyfile ( SD2ASC_OVERPL_CONFIG       , l_temp_dir + "/" + SD2ASC_OVERPL_CONFIG )
                shutil.copyfile ( SD2ASC_OVERPL_CONFIG_SHOALS, l_temp_dir + "/" + SD2ASC_OVERPL_CONFIG_SHOALS )
                shutil.copyfile ( SD2ASC_OVERPL_CONFIG_DEEPS , l_temp_dir + "/" + SD2ASC_OVERPL_CONFIG_DEEPS )
                os.chdir( l_temp_dir )
                l_input_file      = ParameterList [ BathyToolsLib.OUTPUTFILE ] + FILE_EXT_GRD
                l_sds_file        = l_temp_dir + "\\tmp_aggr_makegrid" + FILE_EXT_SDS
                sds_aggregate (logger, l_input_file, l_sds_file, l_temp_dir )

            if str( ParameterList[ BathyToolsLib.PARAMETER_GEN_CONTOURS] ) == "T" :
                logger.info("Start contour generation")
                l_contour_file_sds     = l_temp_dir + "\\tmp_contour_makegrid" + FILE_EXT_SDS
                sds_generate_contours ( logger, DbConnection, l_temp_dir, l_sds_file, l_contour_file_sds, ParameterList )
                # Conver to required output format
                if int( ParameterList [ BathyToolsLib.PARAMETER_CONT_OUTPUTFT ] ) ==  int(BathyDbLib.CON_FORMAT_7CB) :
                    l_contour_file_7cb = ParameterList [ BathyToolsLib.OUTPUTFILE ] + "_contours" + FILE_EXT_7CB
                    sds_convert_contours_to_7cb ( logger, l_contour_file_sds, l_contour_file_7cb )
                elif int( ParameterList [ BathyToolsLib.PARAMETER_CONT_OUTPUTFT ] ) ==  int(BathyDbLib.CON_FORMAT_SHP) :
                    epsg_code_out = BathyToolsLib.get_epsg_code ( DbConnection, logger, ParameterList [ BathyToolsLib.PARAMETER_EPSGCODEOUT ] )
                    l_contour_file_shp = ParameterList [ BathyToolsLib.OUTPUTFILE ] + "_contours" + FILE_EXT_SHP
                    sds_convert_contours_to_shp ( logger, temp_dir, l_contour_file_sds, l_contour_file_shp, epsg_code_out)

            if str ( ParameterList[ BathyToolsLib.PARAMETER_GEN_SPOTS ] ) == "T" :
                logger.info("Start spot sounding generation generation")
                # Get spot sounding type (shoals or deeps)
                spotsounding_type_db_id = ParameterList [ BathyToolsLib.PARAMETER_SPOTSOUND_TYPE ]
                attributes              = [ BathyDbLib.SPOTSOUND_TYPE_COL ]
                values                  = DbConnection.get_obj_attributes ( BathyDbLib.SPOTSOUND_TYPE_CLASS_ID, spotsounding_type_db_id, attributes )
                l_spotsounding_type     = str(values[0])
                # Invert spot sounding type when multiplication factor is positive
                if int(ParameterList [ BathyToolsLib.PARAMETER_MULTI_FACTOR ]) == int(1) :
                    l_spotsounding_type = SPOT_SOUNDING_TYPE_INV [ l_spotsounding_type ]
                l_spotsounding_file_sds     = l_temp_dir + "\\tmp_spot_sounding_makegrid" + FILE_EXT_SDS
                sds_generate_spotsoundings ( logger, l_temp_dir, l_sds_file, l_spotsounding_file_sds, ParameterList, l_spotsounding_type )
                # ConverT to required output format
                if int( ParameterList [ BathyToolsLib.PARAMETER_CONT_OUTPUTFT ] ) ==  int(BathyDbLib.CON_FORMAT_SHP) :
                    epsg_code_out = BathyToolsLib.get_epsg_code ( DbConnection, logger, ParameterList [ BathyToolsLib.PARAMETER_EPSGCODEOUT ] )
                    l_spotsounding_file_shp = ParameterList [ BathyToolsLib.OUTPUTFILE ] + "_spotsoundings" + FILE_EXT_SHP
                    sds_convert_spotsoundings_to_shp ( logger, temp_dir, l_spotsounding_file_sds, l_spotsounding_file_shp, epsg_code_out, l_spotsounding_type)

    except Exception, err:
        logger.critical( "Run Makegrid for product generation failed:ERROR: %s\n" % str(err))
        raise

####################################
# SENS functions                   #
####################################

def sens_csv_importer ( logger, ParameterList ) :
    """Run csv importer"""
    try :
        logger.info ( "Run csv importer" )
        parameter_file_name = string.replace( ParameterList [ BathyToolsLib.TEMPDIR ], "\\" ,"/" ) + "CsvImporter" + str(ParameterList[ BathyToolsLib.TASKID ]) + ".par"

        logger.info ( "Parameterfile CSV importer is " + str(parameter_file_name) )

        # Write parameters to parameter file
        if os.path.exists( parameter_file_name ) :
            os.remove( parameter_file_name )
        fOut = open(parameter_file_name, 'w')

        # Loop through parameter list and write to parameter file
        logger.info ( "Write parameterfile " + str(parameter_file_name) )
        fOut.write("Generated parameterfile"  + "\n" )
        fOut.write("-------------------------------" + "\n" )
        fOut.write("Parameters from task"  + "\n" )
        fOut.write("-------------------------------" + "\n" )
        for parameter in ParameterList :
            if parameter == BathyToolsLib.PARAMETER_INPUT_FILE :
                fOut.write( str(CSV_INPUTFILE) + "=" + str( ParameterList [ parameter ] ) + "\n" )
            else :
                fOut.write( str(parameter) + "=" + str( ParameterList [ parameter ] ) + "\n" )

        # Close file
        fOut.close()

        # Run executable
        command = CSVIMPORTER + " " + "\""+ parameter_file_name + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )

        # Check exit code
        if exit_code :
            if str(exit_code) == str(1) :
                logger.critical( "Run csv importer failed:ERROR: %s\n" % str(err))
                raise

    except Exception, err:
        logger.critical( "Run csv importer failed:ERROR: %s\n" % str(err))
        raise

def sens_isoxml_importer ( logger, ParameterList ) :
    """Run IsoXml importer"""
    try :
        logger.info ( "Run IsoXml importer" )

        # Parsing parameters
        username         = ParameterList [ BathyToolsLib.DBUSER ]
        password         = ParameterList [ BathyToolsLib.DBPASSWORD ]
        connectString    = ParameterList [ BathyToolsLib.DBCONNECT ]
        filename         = ParameterList [ BathyToolsLib.PARAMETER_INPUT_FILE ]
        mapper_id        = ParameterList [ BathyToolsLib.PARAMETER_METADATAMAPPER ]
        root_class_id    = ParameterList [ BathyToolsLib.PARAMETER_OBJ_CLASS_ID ]
        root_instance_id = ParameterList [ BathyToolsLib.PARAMETER_IM_ID ]

        # Run executable
        command   = ISOXMLIMPORTER + " " + str(username) + " " + str(password) + " " + str(connectString) + " \"" + str(filename) + "\" " + str(mapper_id) + " " + str(root_class_id) + " " + str(root_instance_id)
        exit_code = BathyToolsLib.run_oscommand ( logger, command )

        # Check exit code
        if exit_code :
            if str(exit_code) == str(1) :
                logger.critical( "Run IsoXml importer failed:ERROR: %s\n" % str(err))
                raise

    except Exception, err:
        logger.critical( "Run IsoXml importer failed:ERROR: %s\n" % str(err))
        raise


def sens_bag_importer ( logger, ParameterList ) :
    """Run BAG importer"""
    try :
        logger.info ( "Run BAG importer" )

        # Parsing parameters
        username         = ParameterList [ BathyToolsLib.DBUSER ]
        password         = ParameterList [ BathyToolsLib.DBPASSWORD ]
        connectString    = ParameterList [ BathyToolsLib.DBCONNECT ]
        filename         = ParameterList [ BathyToolsLib.PARAMETER_INPUT_FILE ]
        mapper_id        = ParameterList [ BathyToolsLib.PARAMETER_METADATAMAPPER ]
        root_class_id    = ParameterList [ BathyToolsLib.PARAMETER_OBJ_CLASS_ID ]
        root_instance_id = ParameterList [ BathyToolsLib.PARAMETER_IM_ID ]

        # Run executable
        command   = BAGIMPORTER + " " + str(username) + " " + str(password) + " " + str(connectString) + " \"" + str(filename) + "\" " + str(mapper_id) + " " + str(root_class_id) + " " + str(root_instance_id)
        exit_code = BathyToolsLib.run_oscommand ( logger, command )

        # Check exit code
        if exit_code :
            if str(exit_code) == str(1) :
                logger.critical( "Run BAG importer failed:ERROR: %s\n" % str(err))
                raise

    except Exception, err:
        logger.critical( "Run BAG importer failed:ERROR: %s\n" % str(err))
        raise

def sens_sql_importer ( logger, ParameterList ) :
    """Run sql importer"""
    try :
        logger.info ( "Run sql importer" )

        parameter_file_name =  BathyToolsLib.get_working_dir( logger, ParameterList [ BathyToolsLib.TEMPDIR ] ) + "\\SqlImporter" + str(ParameterList[ BathyToolsLib.TASKID ]) + ".par"

        # Write parameters to parameter file
        logger.info ( "Generate parameterfile " + str(parameter_file_name) )
        if os.path.exists( parameter_file_name ) :
            os.remove( parameter_file_name )
        fOut = open(parameter_file_name, 'w')

        # Loop through parameter list and write to parameter file
        fOut.write("Generated parameterfile"  + "\n" )
        fOut.write("-------------------------------" + "\n" )
        fOut.write("Parameters from task"  + "\n" )
        fOut.write("-------------------------------" + "\n" )
        for parameter in ParameterList :
            fOut.write( str(parameter) + "=" + str( ParameterList [ parameter ] ) + "\n" )

        # Close file
        fOut.close()

        # Run executable
        command = SQLIMPORTER + " " + "\""+ parameter_file_name + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )

        # Check exit code
        if exit_code :
            if str(exit_code) == str(1) :
                logger.critical( "Run ascii importer failed:ERROR: %s\n" % str(err))
                raise

    except Exception, err:
        logger.critical( "Run sql importer failed: ERROR: %s\n" % str(err))
        raise

def sens_ascii_importer ( DbConnection, logger, ParameterList, bathyspace_file ) :
    """Run ascii importer"""
    try :
        logger.info ( "Run ascii importer" )
        parameter_file_name =  os.path.dirname( bathyspace_file ) + "\\AsciiImporter" + str(ParameterList[ BathyToolsLib.TASKID ]) + ".par"

        # Update outputfile with bathyspace file in parameterlist
        ParameterList [ BathyToolsLib.PARAMETER_FILE_OUT ] = bathyspace_file

        # Get ID of ascci mapper
        ascii_mapper_id = ParameterList [ BathyToolsLib.PARAMETER_ASCII_IMP ]
        ParameterListAsciiImp = BathyToolsLib.generate_parameter_value_list_from_object ( DbConnection, BathyDbLib.ASCII_IMPORTER_CLASS_ID, ascii_mapper_id )

        # Determine if coordinates are geographic
        logger.info ( "Get coordinate system for Ascii importer" )
        coord_sys_id       = ParameterList[ BathyToolsLib.PARAMETER_COORD_SYS ]
        coord_sys_class_id = BathyToolsLib.get_coord_sys_class ( DbConnection, logger, coord_sys_id )
        if int(coord_sys_class_id) == int( BathyDbLib.GEOGRAPHIC ) :
            ParameterListAsciiImp [ AI_GEOGRAPHIC ] = "T"
        else :
            ParameterListAsciiImp [ AI_GEOGRAPHIC ] = "F"

        # Determine whether columns are required
        # Parse column defintion string: 1, 70531 ; 2, 70532 ; 3, 70533 ; 4, 70534
        # Get required field from database for column definition
        logger.info ( "Determine which columns are required" )
        column_req_string = " "
        column_num_string = " "
        column_defintions = ParameterListAsciiImp[ BathyToolsLib.PARAMETER_COL_DEFS ]
        column_def_list   = column_defintions.rstrip().split(";")
        for column_def in column_def_list :
            col_index         = int( column_def.rstrip().split(",")[0] )
            col_id            = int( column_def.rstrip().split(",")[1] )
            attributes        = [ BathyDbLib.NOD_STR_REQUIRED_COL, BathyDbLib.NOD_STR_NUMERIC_COL ]
            values            = DbConnection.get_obj_attributes ( BathyDbLib.NODAL_STRUCTURE_CLASS_ID, col_id, attributes )
            required          = values[0]
            numeric           = values[1]
            column_req_string = column_req_string + str(col_index) + ", " + str(required) + "; "
            column_num_string = column_num_string + str(col_index) + ", " + str(numeric) + "; "
        ParameterListAsciiImp [ AI_REQUIRED_COLS ] = column_req_string
        ParameterListAsciiImp [ AI_NUMERIC_COLS  ] = column_num_string

        # Write parameters to parameter file
        if os.path.exists( parameter_file_name ) :
            os.remove( parameter_file_name )
        fOut = open(parameter_file_name, 'w')

        # Loop through parameter list and write to parameter file
        logger.info ( "Write parameterfile " +str(parameter_file_name) )
        fOut.write("Generated parameterfile"  + "\n" )
        fOut.write("-------------------------------" + "\n" )
        fOut.write("Parameters from task"  + "\n" )
        fOut.write("-------------------------------" + "\n" )
        for parameter in ParameterList :
            if parameter == BathyToolsLib.PARAMETER_INPUT_FILE :
                fOut.write( str(AI_INPUTFILE) + "=" + str( ParameterList [ parameter ] ) + "\n" )
            else :
                fOut.write( str(parameter) + "=" + str( ParameterList [ parameter ] ) + "\n" )

        # Sort dictionary keys
        parameters = ParameterListAsciiImp.keys()
        parameters.sort()

        # Loop through parameter ascci importer list and write to parameter file
        fOut.write("-------------------------------" + "\n" )
        fOut.write("Parameters from Ascii importer"  + "\n" )
        fOut.write("-------------------------------" + "\n" )
        for parameter in parameters :
            fOut.write( str(parameter) + "=" + str( ParameterListAsciiImp [ parameter ] ) + "\n" )

        # Close file
        fOut.close()

        # Run executable
        command = ASCIIIMPORTER + " " + "\""+ parameter_file_name + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )

        # Check exit code
        if exit_code :
            if str(exit_code) == str(1) :
                logger.critical( "Run ascii importer failed:ERROR: %s\n" % str(err))
                raise

    except Exception, err:
        logger.critical( "Run ascii importer failed:ERROR: %s\n" % str(err))
        raise

def sens_donar_importer ( DbConnection, logger, ParameterList ):
    """Run Donar importer"""
    try :
        logger.info ( "Run Donar importer" )

        # Running executable with parameters:
        # [username]                   Wordt via product controller aangeleverd
        # [password]                   Wordt via product controller aangeleverd
        # [connectString]             Wordt via product controller aangeleverd
        # [filename]                     FILEIN (in tabel 608)
        # [working dir]                 Wordt via product controller aangeleverd, je moet misschien zelf even een subdir aanmaken.
        # [IM mapper ID]             SYS002 (in tabel 602, krijg je via SYS001 van 608)
        # [TR mapper ID]             SYS001 (in tabel 602, krijg je via SYS001 van 608)
        # [root class id]               OBJECTCLASSID (in tabel 608)
        # [root instance id]          INSTANCEID (in table 608)

        # Initialize
        first_item = True

        # Parsing parameters
        username         = ParameterList [ BathyToolsLib.DBUSER ]
        password         = ParameterList [ BathyToolsLib.DBPASSWORD ]
        connectString    = ParameterList [ BathyToolsLib.DBCONNECT ]
        filename         = ParameterList [ BathyToolsLib.PARAMETER_INPUT_FILE ]
        working_dir      = string.replace( ParameterList [ BathyToolsLib.TEMPDIR ], "\\" ,"/" )
        im_mapper_id     = BathyToolsLib.get_donar_mapper_id ( DbConnection, logger, ParameterList [ BathyToolsLib.PARAMETER_DONARIMPORTER ], BathyDbLib.DONAR_IM_MAPPER_COL )
        tl_mapper_id     = BathyToolsLib.get_donar_mapper_id ( DbConnection, logger, ParameterList [ BathyToolsLib.PARAMETER_DONARIMPORTER ], BathyDbLib.DONAR_TL_MAPPER_COL )
        root_class_id    = ParameterList [ BathyToolsLib.PARAMETER_OBJ_CLASS_ID ]
        root_instance_id = ParameterList [ BathyToolsLib.PARAMETER_IM_ID ]

        logger.info("Run Donar import with TL mapper " + str(tl_mapper_id) + " and IM mapper " + str(im_mapper_id) )
        command   = DONARIMPORTER + " " + str(username) + " " + str(password) + " " + str(connectString) + " \"" + str(filename) + "\" \"" + str(working_dir) + "\" " + str(im_mapper_id) + " " + str(tl_mapper_id) + " " + str(root_class_id) + " " + str(root_instance_id)
        exit_code = BathyToolsLib.run_oscommand ( logger, command )

        # Check exit code
        if exit_code :
            if str(exit_code) == str(1) :
                logger.critical( "Run ascii importer failed:ERROR: %s\n" % str(err))
                os.sys.exit()

        # Loop through file list and import TLs or IM
        for file_name in os.listdir(working_dir) :
            if os.path.isfile(os.path.join(working_dir, file_name)) :
                if file_name[:8] == DONAR_TR and file_name[:14] <> DONAR_TR_GROUP :
                    file_name_without_ext = file_name.rstrip().split(".")
                    file_name_parts = file_name_without_ext[0].rstrip().split("_")
                    id = file_name_parts[2]
                    logger.info("Run import TL " + str(id) )
                    if first_item :
                        trackline_list = str(id)
                        first_item = False
                    else :
                        trackline_list = trackline_list + "," + str(id)
                    full_file_name = os.path.join(working_dir, file_name)
                    BathyToolsLib.import_tl ( DbConnection, logger, ParameterList, id, full_file_name, BathyDbLib.IM_FRMT_DONAR )
                if file_name[:8] == DONAR_IM and file_name[:14] <> DONAR_IM_GROUP :
                    file_name_without_ext = file_name.rstrip().split(".")
                    file_name_parts = file_name_without_ext[0].rstrip().split("_")
                    id = file_name_parts[2]
                    logger.info("Run import IM "  + str(id) )
                    if first_item :
                        im_list = str(id)
                        first_item = False
                    else :
                        im_list = im_list + "," + str(id)
                    full_file_name = os.path.join(working_dir, file_name)
                    BathyToolsLib.import_im ( DbConnection, logger, ParameterList, id, full_file_name )

        logger.info( "Start grouping tracklines or IMs" )

        # Loop through file list and group T's or IMs
        for file_name in os.listdir(working_dir) :
            if os.path.isfile(os.path.join(working_dir, file_name)) :
                if file_name[:14] == DONAR_TR_GROUP :
                    file_name_without_ext = file_name.rstrip().split(".")
                    file_name_parts = file_name_without_ext[0].rstrip().split("_")
                    im_id = file_name_parts[3]
                    logger.info("Group tracklines " + str(trackline_list) + " in IM "  + str(im_id) )
                    BathyToolsLib.group_tracklines_in_im ( ParameterList, DbConnection, logger, im_id, trackline_list  )
                if file_name[:14] == DONAR_IM_GROUP :
                    file_name_without_ext = file_name.rstrip().split(".")
                    file_name_parts = file_name_without_ext[0].rstrip().split("_")
                    im_group_id = file_name_parts[3]
                    logger.info("Group IMs in IM group "  + str(im_group_id) )
                    for im_id in im_list.rstrip().split(",") :
                        attribute_list = {}
                        attribute_list [ BathyDbLib.IM_SURVEY_GROUP ]   = im_group_id
                        DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, im_id, attribute_list )

    except Exception, err:
        logger.critical( "Run Donar importer failed:ERROR: %s\n" % str(err))
        raise

####################################
# SDS functions                    #
####################################

def sds_write_sort_config_file ( logger, temp_dir ) :
    """Write sort config file"""
    try :
        logger.info ( "Write sort config file" )
        sort_file_name = temp_dir + "\\" + SDS_SORT_CONFIG

        # Write parameters to parameter file
        if os.path.exists( sort_file_name ) :
            os.remove( sort_file_name )
        fOut = open(sort_file_name, 'w')
        fOut.write("WORKSPACE {" + "\n" )
        fOut.write("SIZE " + str(SDS_WORKSPACE_SIZE) + "\n")
        fOut.write("PATH \"" + temp_dir + "\"" + "\n" )
        fOut.write("}" + "\n" )
        fOut.write("MEMORY " + str(SDS_MEMORY_SIZE) + "\n" )
        fOut.write("COMPOSE(lon,lat)" + "\n" )
        fOut.close()

        # Return name
        return sort_file_name

    except Exception, err:
        logger.critical( "Write sort config file failed:ERROR: %s\n" % str(err))
        raise

def sds_write_contour_config_file ( logger, temp_dir, map_scale, begin_contour, contour_incr, contour_levels ) :
    """Write contour config file"""
    try :
        logger.info ( "Write contour config file" )
        contour_file_name = temp_dir + "\\" + SDS_CONT_CONFIG

        # Write parameters to parameter file
        if os.path.exists( contour_file_name ) :
            os.remove( contour_file_name )
        fOut = open(contour_file_name, 'w')
        fOut.write("VALUE \"SEL_DEPTH\"" + "\n")
        fOut.write("LINES { " + "\n" )
        fOut.write("START 21 "  + "\n")
        fOut.write("END 21" + "\n" )
        fOut.write("}" + "\n" )
        fOut.write("GRANULARITY 6 " + "\n" )
        fOut.write("SCALE \"1:" + str(map_scale) + "\"" + "\n" )
        fOut.write("COORD_SYSTEM_UNITS DEGREES_DECIMAL" + "\n" )
        fOut.write("CONTOUR {" + "\n" )
        if contour_levels :
            fOut.write("LEVELS  " + str(contour_levels) + "\n" )
        else :
            fOut.write("BEGIN  " + str(begin_contour) + "\n" )
            fOut.write("INCREMENT  " + str(contour_incr) + "\n" )
        fOut.write("}" + "\n" )
        fOut.close()

        # Return name
        return contour_file_name

    except Exception, err:
        logger.critical( "Write sort config file failed:ERROR: %s\n" % str(err))
        raise

def sds_write_spotsounding_config_file ( logger, temp_dir, map_scale, percentage_spacing, spotsounding_type ) :
    """Write contour config file"""
    try :
        logger.info ( "Write spotsounding config file" )
        spotsounding_file_name = temp_dir + "\\" + SDS_SPOT_CONFIG

        # Write parameters to parameter file
        if os.path.exists( spotsounding_file_name ) :
            os.remove( spotsounding_file_name )
        fOut = open(spotsounding_file_name, 'w')
        fOut.write("MAP SCALE " + str(map_scale)  + "\n")
        fOut.write("\n")
        fOut.write("PERCENT SPACING " + str(percentage_spacing)  + "\n")
        fOut.write("\n")
        fOut.write("UNITS METER " + "\n")
        fOut.write("\n")
        fOut.write("POINT SIZE " + str(SDS_POINTSIZE_CARIS) + "\n")
        fOut.write("\n")
        fOut.write("COORDINATE SYSTEM LL " + "\n")
        fOut.write("\n")
        fOut.write("DEPTH { " + "\n" )
        #fOut.write("COLUMN SEL_DEPTH "  + "\n")
        fOut.write("COLUMN " + str( SPOT_SOUNDING_COL [ str(spotsounding_type) ] )  + "\n")
        fOut.write("TYPE " + str(spotsounding_type)  + "\n")
        fOut.write("}" + "\n" )
        fOut.write("\n")
        fOut.write("WORKSPACE {" + "\n" )
        fOut.write("SIZE " + str(SDS_WORKSPACE_SIZE) + "\n")
        fOut.write("PATH \"" + temp_dir + "\"" + "\n" )
        fOut.write("}" + "\n" )
        fOut.write("MEMORY " + str(SDS_MEMORY_SIZE) + "\n" )
        fOut.write("\n")
        fOut.close()

        # Return name
        return spotsounding_file_name

    except Exception, err:
        logger.critical( "Write sort config file failed:ERROR: %s\n" % str(err))
        raise


def sds_aggregate ( logger, input_file, output_file, temp_dir ) :
    """Generate aggregated SDS file"""
    try :
        logger.info ( "Generate aggregated file " + str(output_file) )

        # Temporary files
        sds_file        = temp_dir + "\\tmp_ascii"  + FILE_EXT_SDS
        mapped_sds_file = temp_dir + "\\tmp_mapped" + FILE_EXT_SDS
        sorted_sds_file = temp_dir + "\\tmp_sorted" + FILE_EXT_SDS

        # Run executable
        logger.info ( "Convert ASCII" )
        command   = ASC2SDS + " " + "\"" + input_file + "\"" + " " + "\"" + sds_file + "\"" + " " + SDS_XYZ_CONFIG
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
        logger.info ( "Exit code " + str(exit_code) )
        if not os.path.exists( sds_file ) :
            logger.critical( "Convert ASCII to SDS file failed:ERROR: %s\n" )
            raise

        # Run executable
        logger.info ( "Map file" )
        command   = SDS2SDS + " " + "\"" + sds_file + "\"" + " " + "\"" + mapped_sds_file + "\"" + " " + SDS_CONV_CONFIG + " " + SDS_TILE_CONFIG
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
        logger.info ( "Exit code " + str(exit_code) )
        if not os.path.exists( mapped_sds_file ) :
            logger.critical( "Map file failed:ERROR: %s\n" )
            raise

        # Remove temporary files
        if os.path.exists( sds_file ) :
            os.remove( sds_file )

        # Run executable
        logger.info ( "Sort file" )
        sort_config_file = sds_write_sort_config_file ( logger, temp_dir )
        command   = SDSSORT + " " + "\"" + sort_config_file  + "\"" + " " + "\"" + sorted_sds_file + "\"" + " " + "\"" + mapped_sds_file + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
        logger.info ( "Exit code " + str(exit_code) )
        if not os.path.exists( sorted_sds_file ) :
            logger.critical( "Sort file failed:ERROR: %s\n" )
            raise

        # Remove temporary file
        if os.path.exists( mapped_sds_file ) :
            os.remove( mapped_sds_file )

        # Run executable
        logger.info ( "Aggregate file" )
        command   = HHAGGREGATE + " " + "\"" + sorted_sds_file  + "\"" + " " + "\"" + output_file + "\"" + " " + SDS_AGGR_CONFIG + " " + SDS_TILE_CONFIG
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
        logger.info ( "Exit code " + str(exit_code) )
        if not os.path.exists( output_file ) :
            logger.critical( "Aggregate file failed:ERROR: %s\n" )
            raise

        # Remove temporary file
        if os.path.exists( sorted_sds_file ) :
            os.remove( sorted_sds_file )

    except Exception, err:
        logger.critical( "Generate aggregated file failed:ERROR: %s\n" % str(err))
        raise

def sds_generate_contours ( logger, DbConnection, temp_dir, input_file, output_file, ParameterList ) :
    try :
        logger.info ( "Generate contour file " + str(output_file) )

        # Get contour intervals
        contour_interval_db_id = ParameterList [ BathyToolsLib.PARAMETER_CONT_INTERVAL ]
        attributes             = [ BathyDbLib.CONTOUR_INTERVAL_COL ]
        values                 = DbConnection.get_obj_attributes ( BathyDbLib.CONTOUR_INTERV_CLASS_ID, contour_interval_db_id, attributes )
        contour_definition     = str(values[0])

        # Get Multiplication factor
        m_factor = int( ParameterList [ BathyToolsLib.PARAMETER_MULTI_FACTOR ] )

        # Check if you deal with contour list of start and increment
        start             = None
        increment         = None
        contour_intervals = None
        contour_interval = contour_definition.rstrip().split(";")
        if len ( contour_interval ) == 2 :
            # start and increment
            start      = contour_interval[0]
            increment  = contour_interval[1]
            logger.info("Contour generation with begin contour " + str(start) + " and increment " + str (increment) )
        else :
            # Contour intervals, invert when multiplication factor is negative
            if int(m_factor) < 0 :
                contour_list     = contour_definition.rstrip().split()
                new_contour_list = []
                for i in reversed ( contour_list ) :
                    inversed_contour = int(i) * int(-1)
                    new_contour_list.append(inversed_contour)
                contour_list = new_contour_list
                # Convert list to space separated list
                contour_intervals = ""
                for contour in contour_list :
                    contour_intervals = contour_intervals + str(" ") + str(contour)
            else :
                contour_intervals = contour_definition
            logger.info("Contour generation with contour intervals " + str(contour_intervals) )

        # Generate configuration file
        contour_config_file = sds_write_contour_config_file ( logger, temp_dir, ParameterList [ BathyToolsLib.PARAMETER_MAPSCALE ], start, increment, contour_intervals )

        command   = SDSCONTOUR + " " + "\"" + input_file  + "\"" + " " + "\"" + output_file + "\"" + " " + "\"" + contour_config_file  + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
        logger.info ( "Exit code " + str(exit_code) )
        if not os.path.exists( output_file ) :
            logger.critical( "Generate contour file failed:ERROR: %s\n")
            raise
    except Exception, err:
        logger.critical( "Generate contour file failed:ERROR: %s\n" % str(err))
        raise

def sds_generate_spotsoundings ( logger, temp_dir, input_file, output_file, ParameterList, spotsounding_type ) :
    try :
        logger.info ( "Generate spotsoundings file " + str(output_file) )

        # Generate configuration file
        spotsounding_config_file = sds_write_spotsounding_config_file ( logger, temp_dir, ParameterList [ BathyToolsLib.PARAMETER_MAPSCALE ], ParameterList [ BathyToolsLib.PARAMETER_PERC_SPACING ], spotsounding_type )

        # Run command
        command   = SDSOVERPLOT + " " + "\"" + input_file  + "\"" + " " + "\"" + output_file + "\"" + " " + "\"" + spotsounding_config_file  + "\"" + " " + SDS_TILE_CONFIG
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
        logger.info ( "Exit code " + str(exit_code) )
        if not os.path.exists( output_file ) :
            logger.critical( "Generate spotsoundings failed:ERROR: %s\n" )
            raise
    except Exception, err:
        logger.critical( "Generate spotsoundings failed:ERROR: %s\n" % str(err))
        raise


def sds_convert_contours_to_7cb ( logger, input_file, output_file ) :
    try :
        logger.info ( "Convert contour file to 7cb file " + str(output_file) )
        command   = SDSLINE27CB + " " + "\"" + input_file  + "\"" + " " + "\"" + output_file + "\"" + " " + "\"" + SDS_LINE_7CB_CONFIG + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
        logger.info ( "Exit code " + str(exit_code) )
        if not os.path.exists( output_file ) :
            logger.critical( "Convert contour file to 7cb failed:ERROR: %s\n")
            raise
    except Exception, err:
        logger.critical( "Convert contour file to 7cb failed:ERROR: %s\n" % str(err))
        raise

def sds_convert_contours_to_shp ( logger, temp_dir, input_file, shape_file, epsg_code_out) :
    try :
        logger.info ( "Convert contour file to shape file " + str(shape_file) )
        logger.info ( "Convert contour file to ascii contour file" )
        contour_ascii_file = temp_dir + "\\tmp_contour_ascii" + FILE_EXT_ASCII
        command   = SDS2CONTASC + " " + "\"" + input_file  + "\"" + " " + "\"" + contour_ascii_file + "\""
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
        logger.info ( "Exit code " + str(exit_code) )
        # To be implemented
        # contour_ascii_file = makegrid_geo_conv (logger, contour_ascii_file, temp_dir, coord_sys_in, coord_sys_out, ver_dat_in, ver_dat_out, offset, m_factor, etrsyear, " ", " " )
        # Now convert to shape file
        ogr_convert_contour_to_shp ( logger, contour_ascii_file, shape_file, epsg_code_out )
    except Exception, err:
        logger.critical( "Convert contour file to shape failed:ERROR: %s\n" % str(err))
        raise

def sds_convert_spotsoundings_to_shp ( logger, temp_dir, input_file, shape_file, epsg_code_out, spot_sounding_type) :
    try :
        logger.info ( "Convert spotsoundings to shape file " + str(shape_file) )
        logger.info ( "Convert spotsoundings to ascii contour file" )
        spotsounding_ascii_file = temp_dir + "\\tmp_spotsounding_ascii" + FILE_EXT_ASCII
        command   = SDS2ASC + " " + "\"" + input_file  + "\"" + " " + "\"" + spotsounding_ascii_file + "\"" + " " + SDS2ASC_CONFIG_FILES [ spot_sounding_type ]
        exit_code = BathyToolsLib.run_oscommand ( logger, command )
        logger.info ( "Exit code " + str(exit_code) )
        # To be implemented
        # spotsounding_ascii_file = makegrid_geo_conv (logger, spotsounding_ascii_file, temp_dir, coord_sys_in, coord_sys_out, ver_dat_in, ver_dat_out, offset, m_factor, etrsyear, ",", "," )
        # Now convert to shape file
        ogr_convert_spotsounding_to_shp ( logger, spotsounding_ascii_file, shape_file, epsg_code_out )
    except Exception, err:
        logger.critical( "Convert spotsoundings to shape failed:ERROR: %s\n" % str(err))
        raise


####################################
# NetCDF functions                 #
####################################

def netcdf_generate_emodnet_grid ( logger, input_file, output_file, gridsize, ParameterList ) :
    """Function to generate EMODNET NetCDF file"""
    try :
        logger.info ( "Convert EMODNET Ascii file to EMODNET NetCDF file " )

        i = 0
        fIn = open( input_file, "r")

        # Read file to find dimensions of generated EODNET grid
        for line in fIn :
            a = line.rstrip().split(EMODNET_SEPARATOR)
            position_long         = float(a[0])
            position_lat          = float(a[1])

            # Get dimensions in long and lat
            if i == 0 :
                long_min = position_long
                long_max = position_long
                lat_min  = position_lat
                lat_max  = position_lat
                i = i + 1
            else :
                if position_long < long_min :
                    long_min = position_long
                if position_long > long_max :
                    long_max = position_long
                if position_lat < lat_min :
                    lat_min = position_lat
                if position_lat > lat_max :
                    lat_max = position_lat
                i = i + 1

        # Close file
        fIn.close()

        logger.info (  "Nr of lines = " + str(i)     )
        logger.info (  "Long_min = " + str(long_min) )
        logger.info (  "Long_max = " + str(long_max) )
        logger.info (  "Lat_min  = " + str(lat_min)  )
        logger.info (  "Lat_max  = " + str(lat_max)  )

        # Calculate dimensions (number of rows and columns)
        nr_lons = int ( round ( ( long_max - long_min ) / float(gridsize) , 0 ) ) + 1
        nr_lats = int ( round ( ( lat_max  - lat_min  ) / float(gridsize) , 0 ) ) + 1

        logger.info( "Long dimension calculated (columns) = " + str(nr_lons) )
        logger.info("Lat dimension calculated  (rows) = "     + str(nr_lats) )

        # Open the NetCDF file for first time
        if os.path.exists ( output_file ) :
            os.remove( output_file )
        fOut = NetCDFFile( output_file , 'w')

        # Create some global attribute using a constant
        setattr(fOut, NETCDF_GLOBAL_ATTRIBUTES[ 'title' ]      , ParameterList[ NETCDF_GLOBAL_ATTRIBUTES[ 'title' ] ]       )
        setattr(fOut, NETCDF_GLOBAL_ATTRIBUTES[ 'institution' ], ParameterList[ NETCDF_GLOBAL_ATTRIBUTES[ 'institution' ] ] )
        setattr(fOut, NETCDF_GLOBAL_ATTRIBUTES[ 'source' ]     , ParameterList[ NETCDF_GLOBAL_ATTRIBUTES[ 'source' ] ]      )
        setattr(fOut, NETCDF_GLOBAL_ATTRIBUTES[ 'history' ]    , ParameterList[ NETCDF_GLOBAL_ATTRIBUTES[ 'history' ] ]     )
        setattr(fOut, NETCDF_GLOBAL_ATTRIBUTES[ 'references' ] , ParameterList[ NETCDF_GLOBAL_ATTRIBUTES[ 'references' ] ]  )
        setattr(fOut, NETCDF_GLOBAL_ATTRIBUTES[ 'comment' ]    , ParameterList[ NETCDF_GLOBAL_ATTRIBUTES[ 'comment' ] ]     )

        # Create the lat and lon dimensions.
        fOut.createDimension(NETCDF_LON,nr_lons)
        fOut.createDimension(NETCDF_LAT,nr_lats)
        long_dimension     = ( NETCDF_LON, )
        lat_dimension      = ( NETCDF_LAT, )
        variable_dimension = ( NETCDF_LAT, NETCDF_LON )

        # Add dimensions as variables
        longitude_var = fOut.createVariable( 'lon', NETCDF_FLOAT, long_dimension )
        setattr(longitude_var, NETCDF_VARIABLE_ATTRIBUTES['standard_name'], 'longitude'   )
        setattr(longitude_var, NETCDF_VARIABLE_ATTRIBUTES['long_name']    , 'longitude'   )
        setattr(longitude_var, NETCDF_VARIABLE_ATTRIBUTES['units']        , 'degrees_east')
        setattr(longitude_var, NETCDF_VARIABLE_ATTRIBUTES['start']        , str( long_min - 0.5 * EMODNET_GRIDSIZE) )
        setattr(longitude_var, NETCDF_VARIABLE_ATTRIBUTES['increment']    , str(EMODNET_GRIDSIZE) )
        latitude_var = fOut.createVariable( 'lat', NETCDF_FLOAT, lat_dimension  )
        setattr(latitude_var, NETCDF_VARIABLE_ATTRIBUTES['standard_name'] , 'latitude'     )
        setattr(latitude_var, NETCDF_VARIABLE_ATTRIBUTES['long_name']     , 'latitude'     )
        setattr(latitude_var, NETCDF_VARIABLE_ATTRIBUTES['units']         , 'degrees_north')
        setattr(latitude_var, NETCDF_VARIABLE_ATTRIBUTES['start']        , str( lat_min - 0.5 * EMODNET_GRIDSIZE) )
        setattr(latitude_var, NETCDF_VARIABLE_ATTRIBUTES['increment']    , str(EMODNET_GRIDSIZE) )

        # Close the netCDF file
        fOut.close()

        # Reopen the NetCDF file to append scalars
        fOut = NetCDFFile( output_file , 'a')

        # Init scalar arrays (arrays ara initialized on disk in NetcCDF file)
        depth_min_array             = netcdf_create_variable_array ( logger, fOut, 'depth_min'            , variable_dimension, NETCDF_FLOAT     , 'm', NETCDF_CELL_METHODS['minimum'] )
        depth_max_array             = netcdf_create_variable_array ( logger, fOut, 'depth_max'            , variable_dimension, NETCDF_FLOAT     , 'm', NETCDF_CELL_METHODS['maximum'] )
        depth_average_array         = netcdf_create_variable_array ( logger, fOut, 'depth_average'        , variable_dimension, NETCDF_FLOAT     , 'm', NETCDF_CELL_METHODS['mean'] )
        depth_stDev_array           = netcdf_create_variable_array ( logger, fOut, 'depth_stDev'          , variable_dimension, NETCDF_FLOAT     , 'm', NETCDF_CELL_METHODS['standard_deviation'] )
        interpolations_array        = netcdf_create_variable_array ( logger, fOut, 'interpolations'       , variable_dimension, NETCDF_INT       , '' , NETCDF_CELL_METHODS['interpolations'] )
        elementary_surfaces_array   = netcdf_create_variable_array ( logger, fOut, 'elementary_surfaces'  , variable_dimension, NETCDF_INT       , '' , NETCDF_CELL_METHODS['elementary_surfaces'] )
        depth_smoothed_array        = netcdf_create_variable_array ( logger, fOut, 'depth_smoothed'       , variable_dimension, NETCDF_FLOAT     , 'm', NETCDF_CELL_METHODS['smoothed'] )
        depth_smoothed_offset_array = netcdf_create_variable_array ( logger, fOut, 'depth_smoothed_offset', variable_dimension, NETCDF_FLOAT     , 'm', NETCDF_CELL_METHODS['smoothed_offset'] )
        CDI_ID_array                = netcdf_create_variable_array ( logger, fOut, 'CDI_ID'               , variable_dimension, NETCDF_CHARACTER , '' , '')
        DTM_source_array            = netcdf_create_variable_array ( logger, fOut, 'DTM_source'           , variable_dimension, NETCDF_CHARACTER , '' , '')

        # Read files and write values to array
        i = 0
        long_max = 0
        lat_max  = 0
        fIn = open( input_file, "r")
        for line in fIn :

            try :

                # Process line
                i = i + 1

                # Get attributes from line
                a = line.rstrip().split(EMODNET_SEPARATOR)

                # Get row and column in array
                latitude_row  = int ( round ( ( float(a[1]) - lat_min  ) / float(gridsize) , 0 ) )
                longitude_col = int ( round ( ( float(a[0]) - long_min ) / float(gridsize) , 0 ) )

                # Write values to array
                if a[2] :
                    depth_min_array[latitude_row, longitude_col] = float( a[2] )
                if a[3] :
                    depth_max_array[latitude_row, longitude_col] = float( a[3] )
                if a[4] :
                    depth_average_array[latitude_row, longitude_col] = float( a[4] )
                if a[5] :
                    depth_stDev_array[latitude_row, longitude_col] = float( a[5] )
                if a[6] :
                    interpolations_array[latitude_row, longitude_col] = int( a[6] )
                if a[7] :
                    elementary_surfaces_array[latitude_row, longitude_col] = int( a[7] )
                if a[8] :
                    depth_smoothed_array[latitude_row, longitude_col] = float( a[8] )
                if a[9] :
                    depth_smoothed_offset_array[latitude_row, longitude_col] = float( a[9] )
                if a[10] :
                    CDI_ID_array[latitude_row, longitude_col] = str( a[10] )[:1]
                if a[11] :
                    DTM_source_array[latitude_row, longitude_col] = str( a[11] )[:1]

                if i % BathyDbLib.NR_OF_ROWS_PER_INSERT == 0 :
                    logger.info( str(i) + " rows processed" )

            except Exception, err:
                logger.critical( "Writing value to NetCDF array failed failed:ERROR: %s\n" % str(err))
                logger.critical( "Row:    " + str(latitude_row)  )
                logger.critical( "Column: " + str(longitude_col) )
                raise

        # Close inputfile
        fIn.close()

        # Close the netCDF file
        fOut.close()

    except Exception, err:
        logger.critical( "Convert EMODNET Ascii file to EMODNET NetCDF file failed:ERROR: %s\n" % str(err))
        raise

def netcdf_create_variable_array ( logger, netcdf_file, CF_standard_name, dimension, data_type, canonical_unit, cell_method ) :
    """Function to create array for layer in NetCDF file"""
    try :
        logger.info ("Create NetCDF layer " + str(CF_standard_name))

        # Create variables for scalars
        variable  = netcdf_file.createVariable( CF_standard_name, data_type, dimension )

        # Add attributes to variable
        setattr(variable, NETCDF_VARIABLE_ATTRIBUTES['standard_name'] , CF_standard_name            )
        setattr(variable, NETCDF_VARIABLE_ATTRIBUTES['long_name']     , CF_standard_name            )
        setattr(variable, NETCDF_VARIABLE_ATTRIBUTES['units']         , canonical_unit              )
        setattr(variable, NETCDF_VARIABLE_ATTRIBUTES['cell_methods']  , 'area: ' + str(cell_method) )

        ## Initialize the new variable to missing value
        variable_array = netcdf_file.variables[ CF_standard_name ]
        for i in range(variable.shape[0]):
            for j in range(variable.shape[1]):
                variable_array[int(i), int(j)] = EMODNET_MISSING_VALUE
        return variable_array
    except Exception, err:
        logger.critical( "Create NetCDF layer failed:ERROR: %s\n" % str(err))
        raise

####################################
# OGR functions                    #
####################################

def ogr_geom_dateline_translate ( logger, ogr_geom_in ) :
    try :
        logger.debug ( "Translate geometry" )
        logger.debug ( "Geometry type  " + str(ogr_geom_in.GetGeometryName()) )
        logger.debug ( "Geometry count " + str(ogr_geom_in.GetGeometryCount()) )
        is_translated = False
        if ogr_geom_in.GetGeometryName() == 'POLYGON' :
            polygon      = ogr_geom_in
            polygon_out  = ogr.Geometry(ogr.wkbPolygon)
            for nr_ring in range ( polygon.GetGeometryCount() ):
                ring        = polygon.GetGeometryRef( nr_ring )
                ring_out    = ogr.Geometry(ogr.wkbLinearRing)
                for i in range(ring.GetPointCount()) :
                    x = float(ring.GetX(i))
                    y = float(ring.GetY(i))
                    if x < float(0.0) and not is_translated :
                        x = x + float(360.0)
                        is_translated = True
                    if x >= float(180.0) and not is_translated :
                        x = x - float(360.0)
                        is_translated = True
                    ring_out.AddPoint(x,y)
                    is_translated = False
                ring_out.CloseRings()
                polygon_out.AddGeometry(ring_out)
            ogr_geom_out = polygon_out
        if ogr_geom_in.GetGeometryName() == 'MULTIPOLYGON' :
            multipolygon_out = ogr.Geometry(ogr.wkbMultiPolygon)
            for nr_polygon in range ( ogr_geom_in.GetGeometryCount() ) :
                polygon      = ogr_geom_in.GetGeometryRef( nr_polygon )
                polygon_out  = ogr.Geometry(ogr.wkbPolygon)
                for nr_ring in range ( polygon.GetGeometryCount() ):
                    ring        = polygon.GetGeometryRef( nr_ring )
                    ring_out    = ogr.Geometry(ogr.wkbLinearRing)
                    for i in range(ring.GetPointCount()) :
                        x = float(ring.GetX(i))
                        y = float(ring.GetY(i))
                        if x < float(0.0) and not is_translated :
                            x = x + float(360.0)
                            is_translated = True
                        if x > float(180.0) and not is_translated :
                            x = x - float(360.0)
                            is_translated = True
                        ring_out.AddPoint(x,y)
                        is_translated = False
                    ring_out.CloseRings()
                    polygon_out.AddGeometry(ring_out)
                multipolygon_out.AddGeometry(polygon_out)
            ogr_geom_out = multipolygon_out
        logger.debug ( "Geometry type OUT " + str(ogr_geom_out.GetGeometryName()) )
        return ogr_geom_out
    except Exception, err:
        logger.critical( "Translate geometry failed:ERROR: %s\n" % str(err))
        raise

def ogr_extract_hull_from_shape ( logger, shape_file ) :
    """Function to extract hull from shapefile"""
    try :
        logger.info ( "Extract hull from shapefile " + str(shape_file) ) 
        fIn        = ogr.Open ( str(shape_file) )
        layer      = fIn.GetLayer(0)
        feature    = layer.GetNextFeature()   
        geom       = feature.GetGeometryRef()
        hull_wkt   = str(geom.ExportToWkt())
        return hull_wkt
    except Exception, err:
        logger.critical("Extract hull from shapefile failed: ERROR: %s\n" % str(err))
        raise

def ogr_convert_contour_to_shp ( logger, input_file, shape_file, epsg_code_out ) :
    try :
        logger.info ( "Convert ascii contour file to shape file " + str(shape_file) )
        
        # Initialize shape file
        logger.info("Initialize shape file " + shape_file )
        driver     = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(shape_file) :
            driver.DeleteDataSource(str(shape_file))
        shapeData           = driver.CreateDataSource(str(shape_file))
        target_srs          = osr.SpatialReference()
        target_srs.ImportFromEPSG(int(epsg_code_out))
        contour_layer       = shapeData.CreateLayer("Contours", target_srs, ogr.wkbLineString)
        fieldDefn           = ogr.FieldDefn(CONTOUR_DEPTH_FIELD, ogr.OFTReal)
        contour_layer.CreateField(fieldDefn)
        featureDefn_contour = contour_layer.GetLayerDefn()

        # Open file
        file = open(input_file,'r')
        n = 0
        z = 0
        contour_index = int(-1)

        # Read lines and generate contours
        logger.info("Read lines and generate contours ")
        for line in file :
            # Keep old z value 
            z_old = z
            line_split = line.rstrip().split()
            x = float(line_split[0])
            y = float(line_split[1])
            z = float(line_split[4])
            i = int(line_split[5])
            if i <> contour_index :
                if contour_index == -1 :
                    # New contour
                    contour_ogr = ogr.Geometry(ogr.wkbLineString)
                    contour_ogr.AddPoint_2D(x,y)
                    contour_index = i
                else :
                    # Write contour to file
                    n = n + 1
                    shape_feature_contour = ogr.Feature(featureDefn_contour)
                    shape_feature_contour.SetGeometry(contour_ogr)
                    shape_feature_contour.SetFID(contour_index)
                    shape_feature_contour.SetField(CONTOUR_DEPTH_FIELD, z_old)
                    contour_layer.CreateFeature(shape_feature_contour)
                    shape_feature_contour.Destroy()
                    contour_ogr.Destroy()
                    # New contour
                    contour_ogr = ogr.Geometry(ogr.wkbLineString)
                    contour_ogr.AddPoint_2D(x,y)
                    contour_index = i
            else :
                contour_ogr.AddPoint_2D(x,y)

        # Write last contour to file
        if contour_index <> int(-1) :
            n = n + 1
            shape_feature_contour = ogr.Feature(featureDefn_contour)
            shape_feature_contour.SetGeometry(contour_ogr)
            shape_feature_contour.SetFID(contour_index)
            shape_feature_contour.SetField(CONTOUR_DEPTH_FIELD, z)
            contour_layer.CreateFeature(shape_feature_contour)
            shape_feature_contour.Destroy()
            contour_ogr.Destroy()

        logger.info ( str(n) + " contours written to shape file")

        # Close shape file
        shapeData.Destroy()

    except Exception, err:
        logger.critical( "Convert ascii contour file to shape failed:ERROR: %s\n" % str(err))
        raise

def ogr_convert_spotsounding_to_shp ( logger, input_file, shape_file, epsg_code_out ) :
    try :
        logger.info ( "Convert ascii spotsounding file to shape file " + str(shape_file) )

        # Initialize shape file
        logger.info("Initialize shape file " + shape_file )
        driver     = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(shape_file) :
            driver.DeleteDataSource(str(shape_file))
        shapeData           = driver.CreateDataSource(str(shape_file))
        target_srs          = osr.SpatialReference()
        target_srs.ImportFromEPSG(int(epsg_code_out))
        spotsounding_layer  = shapeData.CreateLayer("Spotsoundings", target_srs, ogr.wkbPoint)
        fieldDefn           = ogr.FieldDefn(CONTOUR_DEPTH_FIELD, ogr.OFTReal)
        spotsounding_layer.CreateField(fieldDefn)
        featureDefn_spotsounding = spotsounding_layer.GetLayerDefn()

        # Open file
        file = open(input_file,'r')
        n = 0

        # Read lines and generate contours
        logger.info("Read lines and write spotsoundings")
        for line in file :
            line_split = line.rstrip().split(OVERPLOT_SEPARATOR)
            x = float(line_split[0])
            y = float(line_split[1])
            z = float(line_split[2])
            spotsounding_ogr = ogr.Geometry(ogr.wkbPoint)
            spotsounding_ogr.AddPoint_2D(x,y)
            shape_feature_spotsounding = ogr.Feature(featureDefn_spotsounding)
            shape_feature_spotsounding.SetGeometry(spotsounding_ogr)
            shape_feature_spotsounding.SetFID(int(n))
            shape_feature_spotsounding.SetField(CONTOUR_DEPTH_FIELD, z)
            spotsounding_layer.CreateFeature(shape_feature_spotsounding)
            shape_feature_spotsounding.Destroy()
            spotsounding_ogr.Destroy()
            n = n + 1

        logger.info ( str(n) + " spotsoundings written to shape file")

        # Close shape file
        shapeData.Destroy()

    except Exception, err:
        logger.critical( "Convert ascii spotsounding file to shape failed:ERROR: %s\n" % str(err))
        raise

def ogr_dump_hull_to_shape ( logger, hull_id, epsg_code_out, shape_file, hull_wkt ) :
    """Write hull as shape file"""
    try :
        logger.info ( "write hull to " + str(shape_file) )

        # Get hull as wkt
        hull_ogr = ogr.CreateGeometryFromWkt ( hull_wkt )

        # Init shapefile
        driver     = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(shape_file) :
            driver.DeleteDataSource(str(shape_file))
        shapeData           = driver.CreateDataSource(str(shape_file))
        target_srs          = osr.SpatialReference()
        target_srs.ImportFromEPSG(int(epsg_code_out))
        hull_layer          = shapeData.CreateLayer("Hull", target_srs, ogr.wkbPolygon)
        fieldDefn           = ogr.FieldDefn('id', ogr.OFTInteger)
        hull_layer.CreateField(fieldDefn)
        featureDefn_hull    = hull_layer.GetLayerDefn()

        # Create feature
        shape_feature_im_hull = ogr.Feature(featureDefn_hull)
        shape_feature_im_hull.SetGeometry(hull_ogr)
        shape_feature_im_hull.SetField('id', hull_id)

        # Write feature to file
        hull_layer.CreateFeature(shape_feature_im_hull)

        # Clean up
        shape_feature_im_hull.Destroy()
        hull_ogr.Destroy()
        shapeData.Destroy()

    except Exception, err:
        logger.warning( "write hull to shape file failed:ERROR: %s\n" % str(err))

def ogr_write_separation_model_to_shape ( OracleConnection, logger, wkt_geometry_list, shape_file_name, epsg_code ) :
    """Correct product area for separation model"""
    try :
        logger.info ( "Write separation model to shape")
        
        # Aggregate wkt geometries to sigle geometry
        logger.info ( "Aggregate separation model segments")
        nr_geometries = 0
        for wkt_geometry_id in wkt_geometry_list.keys() :
            wkt_geometry = str(wkt_geometry_list[ wkt_geometry_id ])
            ogr_geometry = ogr.CreateGeometryFromWkt( wkt_geometry )
            if int(nr_geometries) == int(0) :
                mbr_ogr       = ogr_geometry 
                nr_geometries = nr_geometries + 1
            else:
                #mbr_ogr       = mbr_ogr.Union(ogr_geometry)
                mbr_ogr       = shapely_union( OracleConnection, logger, mbr_ogr, ogr_geometry )
                
        # Convert to wkt
        mbr_ogr.FlattenTo2D()
        mbr_wkt = str(mbr_ogr.ExportToWkt())
 
        # Write shapefile
        ogr_dump_hull_to_shape ( logger, 1, epsg_code, shape_file_name, mbr_wkt )
        
    except Exception, err:
        logger.critical("Write separation model to shape failed: ERROR: %s\n" % str(err))
        raise

def ogr_correct_prod_area_for_sep_model ( OracleConnection, logger, product_area, sep_model_file ) :
    """Correct product area for separation model"""
    try :
        logger.info ( "Correct product area for separation model")

        sep_model_file_shp = sep_model_file.replace ( FILE_EXT_ASC, FILE_EXT_SHP )

        # Continu only when shape file exists
        if os.path.exists( sep_model_file_shp ) :
            sep_model_wkt      = ogr_extract_sep_model_hull_from_shapefile ( logger, sep_model_file_shp )
            ogr_sep_model      = ogr.CreateGeometryFromWkt ( str(sep_model_wkt) )
            if product_area :
                ogr_product_area   = ogr.CreateGeometryFromWkt ( str(product_area) )
                # ogr_product_area   = ogr_product_area.Intersection( ogr_sep_model )
                ogr_product_area   = shapely_intersection ( OracleConnection, logger, ogr_product_area, ogr_sep_model )
            else :
                ogr_product_area   = ogr_sep_model
            product_area_wkt       = str(ogr_product_area.ExportToWkt())
        else :
            product_area_wkt       = None

        return product_area_wkt

    except Exception, err:
        logger.critical("Correct product area for separation model failed: ERROR: %s\n" % str(err))
        raise


def ogr_convert_hull_to_wkt ( DbConnection, logger, hull_file ) :
    """Convert generated hull to WKT"""
    try :
        logger.info ( "Convert generated hull to WKT " + str(hull_file) )

        # Do no longer use min_gap_area
        min_gap_area = 0

        # Open hull file
        file = open(hull_file,'r')

        # Initialize polygon for hull
        polygon = ogr.Geometry(ogr.wkbPolygon)

        # Initialize multi polygon for hull
        MultiPolygon = ogr.Geometry(ogr.wkbMultiPolygon)

        # initialize first ring
        ring = ogr.Geometry(ogr.wkbLinearRing)

        # Add points to ring
        x_old = 0
        y_old = 0
        for line in file:
            line_split = line.rstrip().split()
            x = float(line_split[0])
            y = float(line_split[1])
            z = float(line_split[2])
            if ( x <> 9999 ) :
                if ( x <> x_old ) and ( y <> y_old ) :
                    logger.debug("Correct vertex")
                    ring.AddPoint(x,y)
                    x_old = x
                    y_old = y
                else:
                    logger.debug("Duplicate vertex")
            else :
                # Close ring
                ring.CloseRings()
                if ring.GetArea() > min_gap_area :
                    logger.debug("Add ring to polygon and polygon to multipolygon")
                    polygon.AddGeometry(ring)
                    MultiPolygon.AddGeometry(polygon)
                # Initialize new ring
                ring = ogr.Geometry(ogr.wkbLinearRing)
                polygon = ogr.Geometry(ogr.wkbPolygon)

        # Processing last ring (file is not closed with 9999 9999 9999)
        ring.CloseRings()
        polygon.AddGeometry(ring)
        MultiPolygon.AddGeometry(polygon)

        logger.info("Hull consists of " + str(MultiPolygon.GetGeometryCount()) + " rings")

        # Convert to wkt
        MultiPolygon.FlattenTo2D()
        hull = str(MultiPolygon.ExportToWkt())

        # Close file
        file.close()

        # Return result
        return hull

    except Exception, err:
        logger.critical("Convert generated hull to WKT failed: ERROR: %s\n" % str(err))
        raise

def ogr_extract_sep_model_hull_from_shapefile ( logger, shape_file ) :
    """Function to extract hull of separation model from shapefile"""
    try :
        logger.info ( "Extract hull of separation model from shapefile " + str(shape_file) ) 
        fIn        = ogr.Open ( str(shape_file) )
        layer      = fIn.GetLayer(0)
        feature    = layer.GetNextFeature()   
        geom       = feature.GetGeometryRef()
        hull_wkt   = str(geom.ExportToWkt())
        
        return hull_wkt
        
    except Exception, err:
        logger.critical("Extract hull of separation model from shapefile failed: ERROR: %s\n" % str(err))
        raise

def ogr_extract_hull_from_shapefile ( logger, shape_file, id, temp_dir, wkt_in, wkt_out, etrsyear, epsg_in, epsg_out ) :
    """Extract hull from shapefile"""
    try :
        logger.info ( "Extract hull from shapefile " + str(shape_file) )

        # Init variables
        geo_index         = 0
        geoconv_file_name = "tmp_geoconv_in_" + str(id) + FILE_EXT_ASCII
        geoconv_in_file   = temp_dir + "\\" + geoconv_file_name

        # Write coordinates to tmp file for coordinate transformation with Makegrid geoconv
        logger.info ( "Write intermediate file for coordinate conversion" )
        geo_index  = 0
        fIn        = ogr.Open ( str(shape_file) )
        fGeoconvIn = open( geoconv_in_file, 'w' )
        layer      = fIn.GetLayer(0)
        feature    = layer.GetNextFeature()
        while feature is not None:
            multi_poly = feature.GetGeometryRef()
            if multi_poly :
                logger.info ( "Number of polygons " + str(multi_poly.GetGeometryCount()) )
                for nr_poly in range( multi_poly.GetGeometryCount()):
                    poly = multi_poly.GetGeometryRef ( nr_poly )
                    logger.info ( "Number of rings " + str(poly.GetGeometryCount()) )
                    if int(poly.GetGeometryCount()) > int(0) :
                        for nr_ring in range( poly.GetGeometryCount()):
                            ring = poly.GetGeometryRef( nr_ring )
                            logger.info ( "Number of points " + str(ring.GetPointCount()) + " in ring " )
                            for nr_coord in range(ring.GetPointCount()) :
                                x = ring.GetX(nr_coord)
                                y = ring.GetY(nr_coord)
                                fGeoconvIn.write( str(x) + ";" + str(y) + ";" + str(geo_index) + ";" + "\n" )
                            geo_index = geo_index + 1
                    else :
                        logger.info ( "Number of points " + str(poly.GetPointCount()) + " in polygon" )
                        for nr_coord in range(poly.GetPointCount()) :
                            x = poly.GetX(nr_coord)
                            y = poly.GetY(nr_coord)
                            fGeoconvIn.write( str(x) + ";" + str(y) + ";" + str(geo_index) + ";" + "\n" )
                        geo_index = geo_index + 1
            feature = layer.GetNextFeature()
        fGeoconvIn.close()

        # Run Makegrid Geonconv
        logger.info ( "Run coordinate transformation" )
        geoconv_out_file = makegrid_geo_conv (logger, geoconv_file_name, temp_dir, epsg_in, epsg_out, None, None, 0, 1, etrsyear, ";", ";", wkt_in, wkt_out, None, None, None, None )

        # Now convert coordinates to wkt
        logger.info ( "Convert coordinates to WKT" )
        i_previous   = 0
        ring         = ogr.Geometry(ogr.wkbLinearRing)
        polygon      = ogr.Geometry(ogr.wkbPolygon)
        MultiPolygon = ogr.Geometry(ogr.wkbMultiPolygon)
        fGeoconvOut  = open( geoconv_out_file, 'r' )
        for line in fGeoconvOut :
            a = line.rstrip().split(";")
            x = float(a[0])
            y = float(a[1])
            i = float(a[2])
            if int(i_previous) <> int(i) :
                ring.CloseRings()
                polygon.AddGeometry(ring)
                MultiPolygon.AddGeometry(polygon)
                ring    = ogr.Geometry(ogr.wkbLinearRing)
                polygon = ogr.Geometry(ogr.wkbPolygon)
            ring.AddPoint(x,y)
            i_previous = i
        polygon.AddGeometry(ring)
        MultiPolygon.AddGeometry(polygon)
        fGeoconvOut.close()

        logger.info("Hull consists of " + str(MultiPolygon.GetGeometryCount()) + " rings")

        # Convert to wkt
        MultiPolygon.FlattenTo2D()
        hull = str(MultiPolygon.ExportToWkt())

        # Return result
        return hull

    except Exception, err:
        logger.critical("Extract hull from shapefile failed: ERROR: %s\n" % str(err))
        raise

def gdal_write_esri_ascii_grid ( logger, file_in, file_out, separator, gridsize, epsg_code ) :
    """Function to convert ascii xyz file into esri ascii grid"""
    try :
        logger.info ( "Convert ascii xyz file into esri ascii grid" )

        # Get nr of rows and columns of output raster
        i = 0
        fIn = open( file_in, "r")
        for line in fIn :
            a = line.rstrip().split(separator)
            position_long         = float(a[0])
            position_lat          = float(a[1])

            # Get dimensions in long and lat
            if i == 0 :
                long_min = position_long
                long_max = position_long
                lat_min  = position_lat
                lat_max  = position_lat
                i = i + 1
            else :
                if position_long < long_min :
                    long_min = position_long
                if position_long > long_max :
                    long_max = position_long
                if position_lat < lat_min :
                    lat_min = position_lat
                if position_lat > lat_max :
                    lat_max = position_lat
                i = i + 1

        # Close file
        fIn.close()

        # Calculate dimensions
        nr_lons = int ( round ( ( long_max - long_min ) / gridsize , 0 ) ) + 1
        nr_lats = int ( round ( ( lat_max  - lat_min  ) / gridsize , 0 ) ) + 1

        logger.info ( "Number of rows    = " + str(nr_lats) )
        logger.info ( "Number of columns = " + str(nr_lons) )

        # Build arrays
        NrRows        = nr_lats
        NrCols        = nr_lons
        nodata_value  = GDAL_NODATA_VALUE
        sum_depths    = numpy.zeros((NrRows, NrCols), numpy.float32)
        sum_depths    = sum_depths + nodata_value
        count_depths  = numpy.zeros((NrRows, NrCols), numpy.int8)
        count_depths  = count_depths + 1

        # Loop through file and write to array
        logger.info ( "Write data to grid" )
        i = 0
        fIn = open( file_in, "r")
        for line in fIn :

            # Process line
            i = i + 1

            # Get attributes from line
            a = line.rstrip().split(separator)

            # Get row and column in array
            latitude_row  = int ( round ( ( float(a[1]) - lat_min  ) / gridsize , 0 ) )
            longitude_col = int ( round ( ( float(a[0]) - long_min ) / gridsize , 0 ) )

            # Start counting rows from top
            latitude_row = NrRows - latitude_row - 1

            # Write values to array
            if int ( sum_depths [latitude_row , longitude_col ] ) == int ( nodata_value ) :
                sum_depths [latitude_row , longitude_col ]   = float(a[4])
                count_depths [latitude_row , longitude_col ] = int(1)
            else :
                sum_depths [latitude_row , longitude_col ]   = float( sum_depths [latitude_row , longitude_col ] ) + float(a[4])
                count_depths [latitude_row , longitude_col ] = int ( count_depths [latitude_row , longitude_col ] ) + int(1)

        # Create output raster
        raster =  sum_depths / count_depths

        # Close inputfile
        fIn.close()

        logger.info ( str(i) + " points resampled to grid" )

        # Write grid to Esri ascii grid file
        logger.info ( "Write grid to Esri ascii grid file" )

        # Write data array to memory
        file_format = GDAL_AAIGRID_FORMAT
        mem_format  = GDAL_MEM_FORMAT
        driver      = gdal.GetDriverByName( mem_format )
        dst_ds      = driver.Create( file_out, NrCols, NrRows, 1, gdalconst.GDT_Float32)
        srs         = osr.SpatialReference()
        srs.ImportFromEPSG(epsg_code)
        dst_ds.SetGeoTransform( [ long_min, gridsize, 0.0, lat_max, 0.0, -gridsize ] )
        dst_ds.SetProjection( srs.ExportToWkt() )
        dst_ds.GetRasterBand(1).SetNoDataValue( nodata_value )
        dst_ds.GetRasterBand(1).WriteArray( raster )

        # Write memory array to grid
        driver     = gdal.GetDriverByName(file_format)
        dst_ds_new = driver.CreateCopy(file_out, dst_ds)
        dst_ds     = None
        dst_ds_new = None

    except Exception, err:
        logger.critical("Convert ascii xyz file into esri ascii grid failed: ERROR: %s\n" % str(err))
        raise

#def shapely_envelope ( logger, ogr_geom_in ) :
    #"""Get envelope of geometry"""
    #try :
        #logger.info ( "Get envelope of geometry" )
        #shapely_polygon  = loads(ogr_geom_in.ExportToWkb())
        #shapely_boundary = shapely_polygon.envelope
        #ogr_geom_out     = ogr.CreateGeometryFromWkb(dumps(shapely_boundary))
        #return ogr_geom_out
    #except Exception, err:
        #logger.critical("Get envelope of geometry failed: ERROR: %s\n" % str(err))
        #raise

#def shapely_intersection ( OracleConnection, logger, ogr_geom_in_1, ogr_geom_in_2  ) :
    #"""Get envelope of geometry"""
    #try :
        #logger.debug ( "Get intersection between geometries" )
        ##shapely_polygon_1   = loads(ogr_geom_in_1.ExportToWkb())
        ##shapely_polygon_2   = loads(ogr_geom_in_2.ExportToWkb())
        ##shapely_polygon_out = shapely_polygon_1.intersection(shapely_polygon_2)
        ##ogr_geom_out        = ogr.CreateGeometryFromWkb(dumps(shapely_polygon_out))
        ##return ogr_geom_out
        #return ogr.CreateGeometryFromWkt ( OracleConnection.get_intersection ( ogr_geom_in_1.ExportToWkt(), ogr_geom_in_2.ExportToWkt() )   )
    #except Exception, err:
        #logger.critical("Spatial intersection failed: ERROR: %s\n" % str(err))
        #raise

#def shapely_difference ( OracleConnection, logger, ogr_geom_in_1, ogr_geom_in_2  ) :
    #"""Get envelope of geometry"""
    #try :
        #logger.debug ( "Get difference between geometries" )
        ##shapely_polygon_1   = loads(ogr_geom_in_1.ExportToWkb())
        ##shapely_polygon_2   = loads(ogr_geom_in_2.ExportToWkb())
        ##shapely_polygon_out = shapely_polygon_1.difference(shapely_polygon_2)
        ##ogr_geom_out        = ogr.CreateGeometryFromWkb(dumps(shapely_polygon_out))
        ##return ogr_geom_out
        #return ogr.CreateGeometryFromWkt ( OracleConnection.get_difference ( ogr_geom_in_1.ExportToWkt(), ogr_geom_in_2.ExportToWkt() )   )
    #except Exception, err:
        #logger.critical("Spatial difference failed: ERROR: %s\n" % str(err))
        #raise

#def shapely_union ( OracleConnection, logger, ogr_geom_in_1, ogr_geom_in_2  ) :
    #"""Get envelope of geometry"""
    #try :
        #logger.debug ( "Get union of geometries" )
        ##shapely_polygon_1   = loads(ogr_geom_in_1.ExportToWkb())
        ##shapely_polygon_2   = loads(ogr_geom_in_2.ExportToWkb())
        ##shapely_polygon_out = shapely_polygon_1.union(shapely_polygon_2)
        ##ogr_geom_out        = ogr.CreateGeometryFromWkb(dumps(shapely_polygon_out))
        ##return ogr_geom_out
        #return ogr.CreateGeometryFromWkt ( OracleConnection.get_union ( ogr_geom_in_1.ExportToWkt(), ogr_geom_in_2.ExportToWkt() )   )
    #except Exception, err:
        #logger.critical("Spatial union failed: ERROR: %s\n" % str(err))
        #raise

class SourceDiagramFile :
    """Class to generate a sourcefile diagram of cookies"""
    def __init__  ( self, module_name, temp_path, epsg_code_out, boundary_polygon ) :
        """Initialize logger for class"""
        self.logger = logging.getLogger( module_name + '.' + MODULE_NAME + '.SourceDiagramFile')
        self.logger.debug ('Initializing SourceDiagramFile logger')
        self.logger.debug ('Boundary polygon ' + str(boundary_polygon) )

        # Convert boundary polygon to wkt and get boundaries
        self.boundary_polygon_ogr = ogr.CreateGeometryFromWkt ( boundary_polygon )
        self.logger.debug ('Boundary polygon converted to OGR')
        tmp_boundary_polygon_ogr = shapely_envelope ( self.logger, self.boundary_polygon_ogr )
        self.logger.debug ('Boundary polygon ' + str(tmp_boundary_polygon_ogr.ExportToWkt()))
        for nr_coord in range( tmp_boundary_polygon_ogr.GetGeometryRef(0).GetPointCount() ) :
            x = tmp_boundary_polygon_ogr.GetX(nr_coord)
            self.logger.debug("X = " + str(x) )
            if nr_coord == 0 :
                x_min = x
                x_max = x
            else :
                if float(x) < float(x_min) :
                    x_min = float(x)
                if float(x) > float(x_max) :
                    x_max = float(x)
#        for nr_coord in range( tmp_boundary_polygon_ogr.GetPointCount() ) :
#            x = tmp_boundary_polygon_ogr.GetX(nr_coord)
#            self.logger.debug("X = " + str(x) )
#            if nr_coord == 0 :
#                x_min = x
#                x_max = x
#            else :
#                if float(x) < float(x_min) :
#                    x_min = float(x)
#                if float(x) > float(x_max) :
#                    x_max = float(x)

        self.logger.debug ('Data line check')
        if x_max - x_min > float(180.0) :
            self.logger.info ( "Product crosses dateline")
            self.AcrossDateline = True
        else :
            self.AcrossDateline = False

        # Set source SRS
        # Determine target SRS (TM) based on the boundaries from the MBR
        self.logger.debug ('Set source srs')
        l_source_srs              = osr.SpatialReference()
        self.target_srs           = osr.SpatialReference()
        l_source_srs.ImportFromEPSG(int(epsg_code_out)) # WGS84
        #central_meridian          = x_min + ( ( x_max - x_min )/2 )
        #tm_projection             = "+proj=tmerc +lat_0=0 +lon_0=" + str(central_meridian) + "+k=1 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs"
        #self.target_srs.ImportFromProj4(tm_projection)
        self.target_srs.ImportFromEPSG(int(epsg_code_out)) # WGS84
        #self.logger.info("Central meridian is " + str(central_meridian))
        
        # Init feature nr at 0
        self.feature_nr = 0

        # Coordinate transformation boundary polygon
        self.logger.debug ('Coordinate transformation boundary polygon')
        try :
            self.logger.debug ('Coordinate transformation boundary polygon')
            if self.AcrossDateline :
                self.boundary_polygon_ogr = ogr_geom_dateline_translate ( self.logger, self.boundary_polygon_ogr )
            l_trans           = osr.CoordinateTransformation(l_source_srs    , self.target_srs )
            self.trans_to_wgs = osr.CoordinateTransformation(self.target_srs , l_source_srs    )
            self.boundary_polygon_ogr.Transform(l_trans)
        except Exception, err:
            self.logger.critical("Coordinate transformation boundary polygon failed:ERROR: %s\n" % str(err))
            raise

        # initialize shapefiles
        try :
            self.logger.info ('Initialize shapefiles')

            # Create shapefile driver
            driver = ogr.GetDriverByName('ESRI Shapefile')

            # Create shape file for cookies
            #l_shape_file = temp_path +  "\\source_diagram" + FILE_EXT_SHP
            l_shape_file = temp_path +  "_source_diagram" + FILE_EXT_SHP
            self.logger.debug("Initialize shape file " + l_shape_file )
            if os.path.exists(l_shape_file) :
                driver.DeleteDataSource(l_shape_file)
            self.shapeData = driver.CreateDataSource(l_shape_file)

            # Create layer definition
            l_layer_name = 'ContinuousModel'
            self.logger.debug("Create layer " + l_layer_name )
            self.layer_im_segment = self.shapeData.CreateLayer(l_layer_name, l_source_srs, ogr.wkbPolygon)
            self.featureDefn_im_segment = self.layer_im_segment.GetLayerDefn()
            fieldDefn = ogr.FieldDefn('im_id', ogr.OFTInteger)
            self.layer_im_segment.CreateField(fieldDefn)
            fieldDefn = ogr.FieldDefn('im_type', ogr.OFTString)
            self.layer_im_segment.CreateField(fieldDefn)

            # Create shape file for coverage and gaps
            l_shape_file_cov = temp_path +  "_coverage_diagram" + FILE_EXT_SHP
            self.logger.debug("Initialize shape file " + l_shape_file_cov )
            if os.path.exists(l_shape_file_cov) :
                driver.DeleteDataSource(l_shape_file_cov)
            self.shapeData_cov = driver.CreateDataSource(l_shape_file_cov)

            # Create layer definition
            l_layer_name_cov = 'Coverage'
            self.logger.debug("Create layer " + l_layer_name_cov )
            self.layer_cov = self.shapeData_cov.CreateLayer(l_layer_name_cov, l_source_srs, ogr.wkbPolygon)
            self.featureDefn_cov = self.layer_cov.GetLayerDefn()
            fieldDefn_cov = ogr.FieldDefn('id', ogr.OFTInteger)
            self.layer_cov.CreateField(fieldDefn_cov)
            fieldDefn_cov = ogr.FieldDefn('type', ogr.OFTString)
            self.layer_cov.CreateField(fieldDefn_cov)

        except Exception, err:
            self.logger.critical("Initialize shape file failed:ERROR: %s\n" % str(err))
            raise

    def add_IM_segment ( self, OracleConnection, segment_id, segment_type, epsg_code_in, object_class_id ) :
        """Function to add segment to shapefile"""

        try :
            self.logger.info("Write IM segment " + str(segment_id) + " to shape file")

            # Get cookie geometry from database and convert to ogr geometry
            if int(object_class_id) == int(BathyDbLib.COOKIE_CLASS_ID) :
                l_im_segment_wkt = OracleConnection.get_geom ( BathyDbLib.COOKIE_CLASS_ID, segment_id, BathyDbLib.COOKIE_GEOM_COL )
                l_im_id = OracleConnection.get_im_id ( BathyDbLib.COOKIE_CLASS_ID, BathyDbLib.COOKIE_IMID_COL, segment_id )
            if int(object_class_id) == int(BathyDbLib.IMSEGMENT_CLASS_ID) :
                l_im_segment_wkt = OracleConnection.get_geom ( BathyDbLib.IMSEGMENT_CLASS_ID, segment_id, BathyDbLib.IMSEG_GEOM_COL )
                l_im_id = OracleConnection.get_im_id ( BathyDbLib.IMSEGMENT_CLASS_ID, BathyDbLib.IMSEG_IMID_COL, segment_id )
            l_im_segment_ogr = ogr.CreateGeometryFromWkt ( l_im_segment_wkt )

            # Check for dateline
            if self.AcrossDateline :
                l_im_segment_ogr = ogr_geom_dateline_translate ( self.logger, l_im_segment_ogr )

            # Transform coordinates
            self.logger.info ('Coordinate transformation IM segment')
            l_source_srs = osr.SpatialReference()
            l_source_srs.ImportFromEPSG(int(epsg_code_in))
            l_trans = osr.CoordinateTransformation(l_source_srs,self.target_srs)
            l_im_segment_ogr.Transform(l_trans)

            # Cut at boundary of requested area
            # Sometimes intersection fails with shapely, in that case use Oracle Spatial
            self.logger.info("Cut IM segment at boundary")
            #l_im_segment_ogr = l_im_segment_ogr.Intersection( self.boundary_polygon_ogr )
            l_im_segment_ogr = shapely_intersection ( OracleConnection, self.logger, l_im_segment_ogr, self.boundary_polygon_ogr )

            # Union IM segment geometries to get coverage
            if self.feature_nr == 0 :
                self.cov_ogr = l_im_segment_ogr
            else :
                #self.cov_ogr = self.cov_ogr.Union(l_im_segment_ogr)
                self.cov_ogr = shapely_union ( OracleConnection, self.logger, self.cov_ogr, l_im_segment_ogr )

            # TO DO: Cut of at boundaries of product area
            # Convert boundary to ogr geometry and get intersection of geometries
            # TO DO: Generate shpae file with GAPS!!
            # - Gaps from database and gaps in product!!
            # - With attribute interpolate T/F

            # Dateline correction geometries
            self.logger.info("Write IM segment to shapefile")
            geo_list = []
            if self.AcrossDateline :
                # First split polygon on dateline
                l_east_hemisphere_ogr = ogr.CreateGeometryFromWkt(EAST_HEMISPHERE)
                #l_im_segment_ogr_east = l_im_segment_ogr.Intersection( l_east_hemisphere_ogr )
                l_im_segment_ogr_east = shapely_intersection ( OracleConnection, self.logger, l_im_segment_ogr, l_east_hemisphere_ogr )
                # l_im_segment_ogr_west = l_im_segment_ogr.Difference  ( l_im_segment_ogr_east )
                l_im_segment_ogr_west = shapely_difference ( OracleConnection, self.logger, l_im_segment_ogr, l_im_segment_ogr_east )
                if l_im_segment_ogr_west.GetArea() > 0 :
                    l_im_segment_ogr_west = ogr_geom_dateline_translate ( self.logger, l_im_segment_ogr_west )
                    geo_list.append(l_im_segment_ogr_west)
                if l_im_segment_ogr_east.GetArea() > 0 :
                    geo_list.append(l_im_segment_ogr_east)
            else :   
                geo_list.append(l_im_segment_ogr)

            # Make feature and add to shapefile
            for geometry_ogr in geo_list :
                self.logger.info("Geometry type is " + str(geometry_ogr.GetGeometryName()))
                self.feature_nr = self.feature_nr + 1
                geometry_ogr.Transform(self.trans_to_wgs)
                shape_feature_im_segment = ogr.Feature(self.featureDefn_im_segment)
                shape_feature_im_segment.SetGeometry(geometry_ogr)
                shape_feature_im_segment.SetFID(self.feature_nr)
                shape_feature_im_segment.SetField('im_id', l_im_id)
                shape_feature_im_segment.SetField('im_type', segment_type)
                self.layer_im_segment.CreateFeature(shape_feature_im_segment)
                shape_feature_im_segment.Destroy()

            self.logger.debug(str(self.feature_nr) + " features written to file")

        except Exception, err:
            self.logger.critical("Write IM segment failed:ERROR: %s\n" % str(err))
            raise

    def close ( self, OracleConnection ) :
        """Function to generate gaps file, write to coverage file and close files"""

        try :
            self.logger.info("Generate gap geometry")

            # If no features are written to file gap geometry is boundary polygon (there is no coverage)
            if int(self.feature_nr) == int(0) :
                gap_geom_ogr =  self.boundary_polygon_ogr
            else :
                # First get the gaps as difference between boundary polygon and coverage
                # gap_geom_ogr = self.boundary_polygon_ogr.Difference(self.cov_ogr)
                gap_geom_ogr = shapely_difference ( OracleConnection, self.logger, self.boundary_polygon_ogr, self.cov_ogr )

            # Create feature coverage if there is a coverage (features > 0)
            if int(self.feature_nr) > int(0) :
                self.logger.info("Write coverage geometry to shapefile")
                geo_list = []
                if self.AcrossDateline :
                    # First split polygon on dateline
                    l_east_hemisphere_ogr = ogr.CreateGeometryFromWkt(EAST_HEMISPHERE)
                    #l_cov_ogr_east        = self.cov_ogr.Intersection( l_east_hemisphere_ogr )
                    l_cov_ogr_east        = shapely_intersection ( OracleConnection, self.logger, self.cov_ogr, l_east_hemisphere_ogr )
                    #l_cov_ogr_west        = self.cov_ogr.Difference  ( l_cov_ogr_east )
                    l_cov_ogr_west        = shapely_difference ( OracleConnection, self.logger, self.cov_ogr, l_cov_ogr_east )
                    if l_cov_ogr_west.GetArea() > 0 :
                        l_cov_ogr_west = ogr_geom_dateline_translate ( self.logger, l_cov_ogr_west )
                        geo_list.append(l_cov_ogr_west)
                    if l_cov_ogr_east.GetArea() > 0 :
                        geo_list.append(l_cov_ogr_east)
                else :
                    geo_list.append( self.cov_ogr )

                # Make feature and add to shape
                for geometry_ogr in geo_list :
                    self.logger.debug("Geometry type is " + str(geometry_ogr.GetGeometryName()))
                    geometry_ogr.Transform(self.trans_to_wgs)
                    shape_feature_cov = ogr.Feature(self.featureDefn_cov)
                    shape_feature_cov.SetGeometry(geometry_ogr)
                    shape_feature_cov.SetFID(1)
                    shape_feature_cov.SetField('id', 1)
                    shape_feature_cov.SetField('type', "coverage")
                    self.layer_cov.CreateFeature(shape_feature_cov)
                    shape_feature_cov.Destroy()
                
                # Destory coverage
                self.cov_ogr.Destroy()

            # Create feature gap
            self.logger.info("Write gap geometry to shapefile")
            geo_list = []
            if self.AcrossDateline :
                # First split polygon on dateline
                l_east_hemisphere_ogr = ogr.CreateGeometryFromWkt(EAST_HEMISPHERE)
                #l_gap_ogr_east        = gap_geom_ogr.Intersection( l_east_hemisphere_ogr )
                l_gap_ogr_east        = shapely_intersection ( OracleConnection, self.logger, gap_geom_ogr, l_east_hemisphere_ogr )
                #l_gap_ogr_west        = gap_geom_ogr.Difference  ( l_gap_ogr_east )
                l_gap_ogr_west        = shapely_difference ( OracleConnection, self.logger, gap_geom_ogr, l_gap_ogr_east )
                if l_gap_ogr_west.GetArea() > 0 :
                    l_gap_ogr_west = ogr_geom_dateline_translate ( self.logger, l_gap_ogr_west )
                    geo_list.append(l_gap_ogr_west)
                if l_gap_ogr_east.GetArea() > 0 :
                    geo_list.append(l_gap_ogr_east)
            else :
                geo_list.append( gap_geom_ogr )

            # Make feature and add to shape
            for geometry_ogr in geo_list :
                self.logger.debug("Geometry type is " + str(geometry_ogr.GetGeometryName()))
                geometry_ogr.Transform(self.trans_to_wgs)
                shape_feature_gap = ogr.Feature(self.featureDefn_cov)
                shape_feature_gap.SetGeometry(geometry_ogr)
                shape_feature_gap.SetFID(2)
                shape_feature_gap.SetField('id', 2)
                shape_feature_gap.SetField('type', "gap")
                self.layer_cov.CreateFeature(shape_feature_gap)
                shape_feature_gap.Destroy()

            # Destroy features and geometries
            self.boundary_polygon_ogr.Destroy()
            if int(self.feature_nr) > int(0) :
                gap_geom_ogr.Destroy()

        except Exception, err:
            self.logger.critical("Generate gap geometry failed:ERROR: %s\n" % str(err))
            raise

        try :
            self.logger.debug("Destroy data sources")

            # Destoy data source
            self.shapeData.Destroy()
            self.shapeData_cov.Destroy()

        except Exception, err:
            self.logger.critical("Destroy data sources failed:ERROR: %s\n" % str(err))
            raise





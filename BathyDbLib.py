import BathyDbLib
#! /usr/bin/python

# standard library imports
import os
import re
import logging
import xml.dom.minidom
from htmlentitydefs import name2codepoint

# related third party imports
import cx_Oracle

# local application/library specific imports
import BathyExecutablesLib


__author__="Terlien"
__date__ ="$28-mei-2010 11:55:50$"

# Debug setting
QUERY_ON_ELEMENTS = False
#QUERY_ON_ELEMENTS = True

# Module name
BATHYTOOLS  = "BathyTools"
#BATHYTOOLS  = "MakeGridOracleInterface"
MODULE_NAME = "BathyDbLib"

# Default user and password for SENS
SENS         = "sens"
SENSPASSWORD = "senso"

# Oracle read array size
READARRAYSIZE   = 10000
SELECTARRAYSIZE = 100000

# Nr of rows to split bulk insert of depths
NR_OF_ROWS_PER_INSERT = 500000

# Delete imp_import_temp table stmt ID
DELETE_IM_IMP_TEMP_STMT_ID = 19

# Database class ID
ATTR_GROUP_CLASS_ID      = 204
VERDATIN_CLASS_ID        = 227
DATA_PROCESSING_CLASS_ID = 229
IM_CLASS_ID              = 236
QUERY_CLASS_ID           = 243
TL_CLASS_ID              = 261
CM_CLASS_ID              = 263
COOKIE_CLASS_ID          = 266
EPSG_CLASS_ID            = 273
PRODUCTTYPE_CLASS_ID     = 319
ATTRIBUTE_CLASS_ID       = 318
PRODUCTORDER_CLASS_ID    = 325
ATTR_TYPE_CLASS_ID       = 327
SURVEYGROUP_CLASS_ID     = 328
PRODUCTFORMAT_CLASS_ID   = 488
METHOD_CLASS_ID          = 489
VERDATOUT_CLASS_ID       = 490
INTERPOLATE_CLASS_ID     = 492
SEPARATOR_CLASS_ID       = 535
XYZFORMAT_CLASS_ID       = 549
WORKFLOWSTEP_CLASS_ID    = 586
ASCII_IMPORTER_CLASS_ID  = 605
NODAL_STRUCTURE_CLASS_ID = 619
GEODETIC_HORIZ_CLASS_ID  = 594
SEP_MOD_CLASS_ID         = 596
VD_MULTIFACTOR_CLASS_ID  = 597
GEODETIC_VERTI_CLASS_ID  = 598
DONAR_IMPORTER_CLASS_ID  = 602
BAG_IMPORTER_CLASS_ID    = 607
IMSEGMENT_CLASS_ID       = 642
CLIENT_DML_CLASS_ID      = 663
ATTR_VIEW_DEF_CLASS_ID   = 672
CONTOUR_INTERV_CLASS_ID  = 683
SPOTSOUND_TYPE_CLASS_ID  = 684
PROJUNIT_CLASS_ID        = 697
GEOUNIT_CLASS_ID         = 701
SEP_MOD_FILE_CLASS_ID    = 705

# Table name
SDB_INDIVIDUALMODEL   = "SDB_INDIVIDUALMODEL"
SDB_HOOGTE_DIEPTE     = "SDB_HOOGTE_DIEPTE"

# IM columns
IM_ID                 = "ID"
IM_NAME               = "NAME"
IM_STARTDATE_COL      = "SYS001"
IM_STATUS_COL         = "SYS004"
IM_HULL_GENERATED_COL = "SYS005"
IM_DATAPROCESSING_COL = "SYS008"
IM_SURVEYTYPE_COL     = "SYS009"
IM_PROC_DATA_FILE_COL = "SYS011"
IM_BATHYSP_FILE_COL   = "SYS013"
IM_ACCEPTED_COL       = "SYS015"
IM_HULL_COL           = "SYS_GEOM001"
IM_BATHYSP_TYPE_COL   = "SYS025"
IM_LINK_DISTANCE_COL  = "SYS026"
IM_ACTIVATE           = "SYS033"
IM_SURVEY_GROUP       = "SYS051"
IM_SOURCE_FILES_COL   = "SYS057"
IM_INPUT_FORMAT_COL   = "SYS064"
IM_SDFILE_NAME_COL    = "SYS067"
IM_DMAGIC_PROJ_COL    = "SYS068"
IM_WORKFLOWSTEP_COL   = "SYS069"
IM_COORD_SYS_SRC_COL  = "SYS072"
IM_IM_FORMAT_COL      = "SYS073"
IM_SEP_MODEL_COL      = "SYS074"
IM_ETRSYEAR_COL       = "SYS075"
IM_SDBLOB_COL         = "SYS076"
IM_IM_FORMAT_DB       = "SYS077"
IM_RESAMPLE_COL       = "SYS079"
IM_GRIDSIZE_COL       = "SYS080"
IM_NEIGHBOUR_COL      = "SYS081"
IM_INTERPOL_COL       = "SYS082"
IM_POINTS_USED_COL    = "SYS083"
IM_WEIGHT_FAC_COL     = "SYS084"
IM_SEARCH_DIS_COL     = "SYS085"
IM_SMOOTH_FAC_COL     = "SYS086"
IM_XMIN_COL           = "SYS087"
IM_XMAX_COL           = "SYS088"
IM_YMIN_COL           = "SYS089"
IM_YMAX_COL           = "SYS090"
IM_ZMIN_COL           = "SYS091"
IM_ZMAX_COL           = "SYS092"
IM_NR_PS_SOURCE       = "SYS093"
IM_GRID_CELL_SIZE_COL = "SYS094"
IM_GRID_NODATA_VALUE  = "SYS095"
IM_GRID_NCOLS         = "SYS096"
IM_GRID_NROWS         = "SYS097"
IM_GRID_XLLCENTER     = "SYS098"
IM_GRID_XLLCORNER     = "SYS099"
IM_GRID_YLLCENTER     = "SYS100"
IM_GRID_YLLCORNER     = "SYS101"
IM_GRID_XDIM          = "SYS102"
IM_GRID_YDIM          = "SYS103"
IM_VERDAT_SOURCE_COL  = "SYS104"
IM_VERDAT_DB_COL      = "SYS105"
IM_LINK_DIST_EST_COL  = "SYS106"
IM_POINTS_IN_MOD_COL  = "SYS107"
IM_PP_SAMPLE_COL      = "SYS108"

# Trackline class columns
TL_DATA_FILE_COL     = "SYS002"
TL_HULL_GEN_COL      = "SYS003"
TL_HULL_FILE_COL     = "SYS004"
TL_FORMAT            = "SYS007"
TL_TYPE              = "SYS010"
TL_HULL_GEOM_COL     = "SYS_GEOM001"
TL_LINK_DIST_COL     = "SYS020"
TL_IM_COL            = "SYS021"
TL_STARTDATE_COL     = "SYS022"
TL_EPSG_ID_IN        = "SYS031"
TL_IM_FORMAT         = "SYS032"
TL_SEP_MODEL_COL     = "SYS033"
TL_ETRSYEAR_COL      = "SYS034"
TL_INPUT_FORMAT_COL  = "SYS035"
TL_ENDDATE_COL       = "SYS040"
TL_XMIN_COL          = "SYS041"
TL_XMAX_COL          = "SYS042"
TL_YMIN_COL          = "SYS043"
TL_YMAX_COL          = "SYS044"
TL_ZMIN_COL          = "SYS045"
TL_ZMAX_COL          = "SYS046"
TL_NR_PS_SOURCE      = "SYS048"
TL_VERDAT_SOURCE_COL = "SYS049"

# Columns of SDB_ATTRIBUTEGROUP
ATTR_GR_NAME_COL   = "NAME"

# Columns of SDB_OBJECT_CLASS_ATTR
ATTRIBUTE_NAME_TAG = 'ATTRIBUTE_NAME'

# Columns of SDB_PRODUCTORDER table
PARAMETER_CLASS_COL    = "SYS001"
PARAMETER_INSTANCE_COL = "SYS002"

# Column SDB_COMBIMSEGMENTS
IMSEG_IM_ID_COL = "SYS001"
IMSEG_JOBID_COL = "SYS002"
IMSEG_GEOM_COL  = "SYS_GEOM001"

# Epsgcode class columns for domain values (cmdop uses text instead of epsg code)
EPSG_CODE_COL  = "SYS002"
EPSG_CMDOP_COL = "SYS001"

# Columns SDB_CLIENT_DML
DML_TEXT_COL   = "DML_TEXT"

# Ascii importer columns
IM_FORMAT_COL  = "SYS015"

# Columns table SDB_GEODETICHORIPARAMS
COORD_CLASS_COL = "SYS001"
EPSG_CODE_COL   = "SYS002"
WKT_UNFORM_COL  = "SYS022"
PROJUNIT_COL    = "SYS025"
GEOUNIT_COL     = "SYS028"

# Column table SDB_GEODETICVERTIIPARAMS
SEP_MODEL_ID_COL = "SYS001"
OFFSET_COL       = "SYS002"
M_FACTOR_COL     = "SYS003"
S_FACTOR_ID_COL  = "SYS004"

# Columns table SDB_PROJECTIONUNIT
CONV_FACTOR_COL = "SYS001"

# Columns table SDB_GEOUNIT
DEGREES_PI_COL = "SYS001"

# Columns table SDB_SEPARATIONMODEL
VERDAT_IN_COL    = "SYS001"
VERDAT_OUT_COL   = "SYS002"
HASFILE_COL      = "SYS004"
ISALGORITHM_COL  = "SYS005"

# ColumnS table SDB_VERDAT
NAME_COL         = "NAME"
MAKEGRID_COL     = "SYS002"

# Columns SDB_DONAR_IMPORTER
DONAR_TL_MAPPER_COL = "SYS001"
DONAR_IM_MAPPER_COL = "SYS002"

# Columns table SDB_VDSTANDARDFACTOR
S_FACTOR_COL     = "SYS001"

# Columns SDB_ATTRIBUTETYPE
ADDED_BY_USER_COL = "TO_BE_ADDED_BY_USER"

# Columns of table SDB_PRODUCTTYPE
FILE_FORMAT_COL  = "FILEFORMAT"

# Columns of table SDB_WORKFLOWSTEP
PRODUCTTYPE_COL  = "SYS001"

# Columns SDB_OBJECT_CLASS_ATTR
OBJECT_CLASS_COL  = "OBJECT_CLASS_ID"
ATTR_NAME_COL     = "ATTRIBUTE_NAME"
ATTR_LABEL_COL    = "ATTRIBUTE_LABEL"
USER_CREATED_COL  = "USER_CREATED"
ATTR_GROUP_ID_COL = "ATTRIBUTE_GROUP_ID"
ORDER_GROUP_COL   = "ORDERINGROUP"
DISABLED_COL      = "DISABLED"

# Columns of SDB_OBJECT_ATTRIBUTE_VIEW
VIEW_ATTR_ID_COL  = "ATTRIBUTE_ID"
VIEW_VISIBLE_COL  = "VISIBLE"

# Columns of SDB_BAGIMPORTER
BAG_IMP_BATHY_COL  = "SYS001"
BAG_IMP_META_COL   = "SYS002"
BAG_IMP_UNC_COL    = "SYS003"
BAG_METAMAPPER_COL = "SYS004"

# Columns SDB_HOOGTE_DIEPTE
POSITION           = "positie"
WDG_ID             = "wdg_id"

# Columns SDB_SEPARATIONMODELFILE
SEP_MOD_NAME_COL      = "NAME"
SEP_MOD_DESC_COL      = "DESCRIPTION"
SEP_MOD_HULL_COL      = "SYS_GEOM001"
SEP_MOD_BLOB_COL      = "SYS003"
SEP_MOD_GRID_COL      = "SYS004"
SEP_MOD_ALGO_COL      = "SYS005"
SEP_MOD_AUTH_COL      = "SYS006"
SEP_MOD_HULL_FILE_COL = "SYS007"
SEP_MOD_DATA_FILE_COL = "SYS008"
SEP_MOD_ID_COL        = "SYS009"
SEP_MOD_DIR_COL       = "SYS011"
SEP_MOD_GRIDSIZE      = "SYS012"
SEP_MOD_ALG_COL       = "SYS014"

# Columns in SDB_NODALSTRUCTURE
NOD_STR_REQUIRED_COL  = "SYS003"
NOD_STR_NUMERIC_COL   = "SYS007"

# Attribute types from SDB_ATTRIBUTETYPE
ATYPE_DOMAIN     = 1
ATYPE_BOOLEAN    = 8
ATYPE_GEOMETRY   = 111
ATYPE_BLOB       = 222
ATYPE_NO_DB      = 99

# Bathyspace type database id's (SDB_BATHYSPACETYPE)
BATHYSPACE_SD    = 14856
BATHYSPACE_PFM   = 2695
BATHYSPACE_ASCII = 2696
BATHYSPACE_COMP  = 5566
BATHYSPACE_TL    = 2704
BATHYSPACE_BAG   = 24404

# Columns SDB_COOKIE
COOKIE_CMID_COL = "SYS502"
COOKIE_IMID_COL = "SYS503"
COOKIE_GEOM_COL = "SYS_GEOM501"

# Columns SDB_COMBIMSEGMENTS
IMSEG_IMID_COL  = "SYS001"

# Columns sdb_contourintervalopt
CONTOUR_INTERVAL_COL = "SYS001"

# Columns SDB_SPOTSOUNDINGTYPE
SPOTSOUND_TYPE_COL = "NAME"

# ID's of sql statements (SDB_CLIENT_DML)
INSERT_EDGES_STMT_ID           = 8
INSERT_IM_XYZ_STMT_ID          = 9
INSERT_IM_CUBE_STMT_ID         = 10
SELECT_IM_XYZ_STMT_ID          = 11
SELECT_COOKIE_XYZ_STMT_ID      = 12
SELECT_COOKIE_POLY_XYZ_STMT_ID = 13
INSERT_IM_EMODNET_STMT_ID      = 14
SELECT_IM_DEPTH_EMODNET        = 15
SELECT_COOKIE_DEPTH_EMODNET    = 16
SELECT_IM_SEGMENT_STMT_ID      = 17
SELECT_IM_SEGMENT_POLY_STMT_ID = 18
SELECT_COOKIE_IN_IM_STMT_ID    = 20
SELECT_SM_SEGMENT_STMT_ID      = 21
SELECT_SM_DATA_STMT_ID         = 22
SELECT_IM_DATA_STMT_ID         = 23
SELECT_COOKIE_XYS_STMT_ID      = 24
SELECT_COOKIE_POLY_XYS_STMT_ID = 25
SELECT_COOKIE_XYD_STMT_ID      = 26
SELECT_COOKIE_POLY_XYD_STMT_ID = 27

# Survey type IDs (SDB_SURVEYTYPE)
MULTIBEAM_SURVEYTYPE_ID  = 796
SINGLEBEAM_SURVEYTYPE_ID = 797
LASERALTIM_SURVEYTYPE_ID = 798
TRACKLINE_SURVEYTYPE_ID  = 799
MODEL_SURVEYTYPE_ID      = 800
EXTR_MODEL_SURVEYTYPE_ID = 5135

# IM input format (table SDB_PRODUCTTYPR)
IMP_FORMAT_ESRIASCIIGRID = 64177

# Bathyspace type database id's (SDB_BATHYSPACETYPE)
BATHYSPACE_SD    = 14856
BATHYSPACE_PFM   = 2695
BATHYSPACE_ASCII = 2696
BATHYSPACE_COMP  = 5566
BATHYSPACE_TL    = 2704
BATHYSPACE_BAG   = 24404

# Ascii outputfile formats (table SDB_ASCIIOUTPUTFORMAT)
FORMAT_XYZ_SPACE     = 14813
FORMAT_YXZ_SPACE     = 14814
FORMAT_XYZ_SEMICOLON = 14815
FORMAT_YXZ_SEMICOLON = 14816
FORMAT_XYZ_PIPE      = 14817
FORMAT_YXZ_PIPE      = 14818
FORMAT_XYZ_GML       = 14819
FORMAT_YXZ_GML       = 14820
FORMAT_XYZ_COMMA     = 14823
FORMAT_YXZ_COMMA     = 14824

# AttributeOrder ID from SDB_ATTRIBUTEORDER
ATTR_ORDER_XYZ_ID   = 18409
ATTR_ORDER_YXZ_ID   = 18410
ATTR_ORDER_DMSNE_ID = 63462
ATTR_ORDER_DMSEN_ID = 63463

# Separator ids in SDB_SEPARATOR
SEP_PIPE_ID       = 18392
SEP_SEMICOLON_ID  = 18393
SEP_COMMA_ID      = 18394
SEP_WHITESPACE_ID = 18395

# Entries from SDB_IMFORMAT
IM_FRMT_XYZZZSN  = 70521
IM_FRMT_XYZU     = 70529
IM_FRMT_XYZ      = 70530
IM_FRMT_SENS     = 70749
IM_FRMT_DONAR    = 70759

# Entries SDB_PRODUCTFORMAT
PRODUCT_ASCII           = 14522
PRODUCT_ESRI_ASCII_GRID = 14521
PRODUCT_SDFILE          = 146210
PRODUCT_32BIT_GEOTIFF   = 159488
PRODUCT_RGBA_GEOTIFF    = 159490
PRODUCT_EMODNET_ASCII   = 26438
PRODUCT_EMODNET_NETCDF  = 170607

# Entries SDB_PRODUCTMODE
CM_MODE      = 70595
CONTOUR_MODE = 85157

# Entries SDB_PRODUCTTYPE
TL_SURVEY_ASCII = 14197

# Process Archive trackline
PROCESS_IMP_TL  = 486

# Trackline format
TLFORMAT_ASCII = 14197

# Column separator text
SEPARATOR_COL = "SYS001"

# EPSG code projection database
EPSG_CODE_DB    = 4326        # Unprojected WGS84
EPSG_DESC_DB    = "FG_WGS_84" # Unprojected WGS84
EPSG_PROJECTION_ID_DB = 2811  # Database ID WGS84
VERTICAL_DATUM_ID_DB  = 15140 # Database ID ETRS89

# Coordinate system classes
GEOGRAPHIC  = 64167
PROJECTED   = 64168

# Entry SDB_GEODETICVERTICALPARAMETERS
SEP_MODEL_UNKONWN = 71517

# Entry SDB_VERDAT
VERTICAL_DATUM_UNKNOWN = 14568

# Columns Cm table
CM_ISACTIVE      = "SYS002"
CM_EXCL_LIST     = "SYS004"
CM_UPD_EXCL_LIST = "SYS006"

# Column SDB_SURFACEDIFFMODEL
SD_FILE_OUT_COL    = "SDFILEOUT"

# Entries table sdb_ProcessCmOption
ACTIVATE_CM         = 25432
DEACTIVATE_CM       = 25433
UPD_EXCLUDE_LIST    = 25437

# Entries table sdb_ProcessImCmOption
ACTIVATE_IM_IN_CM   = 25449
DEACTIVATE_IM_IN_CM = 25450

# Entries table SDB_CONTOUROUTPUTFORMAT
CON_FORMAT_SHP      = 85359
CON_FORMAT_7CB      = 85361

# Entries SDB_PRODUCTTYPE 
ESRI_ASCII_GRID_TYPE = 64177

# Unkown vertical datum
VERDAT_UNKNOWN = 99

def htmlentitydecode(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint),
            lambda m: unichr(name2codepoint[m.group(1)]), s)

def htmldecode ( text_in ) :
    return str.replace( str.replace( str(text_in) , "&quot;", "\"" ),"&apos;","'")

class DbConnection:
    """Connection class to Oracle database"""
    def __init__(self, DbUser, DbPass, DbConnect, start_logging, parent_module):
        "Set up connection to Oracle database"
        self.oracle_connection = cx_Oracle.connect(DbUser, DbPass, DbConnect)
        self.oracle_cursor = self.oracle_connection.cursor()
        self.oracle_cursor.execute("select 'established' from dual")
        if start_logging :
            self.logger = logging.getLogger( parent_module + '.' + MODULE_NAME + '.DbConnection')
            self.logger.info("Db logging started")

    def start_transaction ( self ) :
        self.oracle_cursor = self.oracle_connection.cursor()

    def commit_transaction ( self ) :
        self.oracle_connection.commit()

    def write_depths_to_emodnet_grid ( self, file_out, im_id, cookie_id, product_area ) :
        """Function to write depths to file according to emodnet specs"""

        try :
            self.logger.info("Write depths as EMODNET grid")
            self.oracle_cursor.arraysize = READARRAYSIZE
            l_nr = 0

            # Get select statement
            if im_id :
                l_query = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [SELECT_IM_DEPTH_EMODNET])
                self.oracle_cursor.execute(l_query, wdgId = im_id )
            if cookie_id :
                l_query = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [SELECT_COOKIE_DEPTH_EMODNET])
                self.oracle_cursor.execute(l_query, polygon = product_area, cookieId = cookie_id )

            # Select depths from DB and write to file
            while 1 :
                l_depths = self.oracle_cursor.fetchmany()
                if not l_depths :
                    break
                else :
                    for l_depth in l_depths :
                        l_nr = l_nr + 1
                        file_out.write( str(l_depth[0]) +  "\n" )
#                    for l_depth in l_depths :
#                        l_nr = l_nr + 1
#                        file_out.write( str(l_depth[0]) + ";" + str(l_depth[1]) + ";" + str( l_depth[2] ) + ";" + str( l_depth[3] ) + ";" + str( l_depth[4] ) + ";" + str( l_depth[5] ) + ";" + str( l_depth[6] ) + ";" + str( l_depth[7] ) + ";" + str( l_depth[8] ) + ";" + str( l_depth[9] ) + ";" + str( l_depth[10] ) + ";" + str( l_depth[10] ) + ";" + "\n" )

            self.logger.info( str(l_nr) + " depths written to file")

        except Exception, err:
            self.logger.critical("Write depths as EMODNET grid failed: ERROR: " + str(err))
            raise


    def format_IM_line ( self, line_in, ascii_format, nr, epsg_out ) :
        """Function to format ascii output line"""
        
        # Initalize separator
        l_separator = None

        # Get xyz attributes
        l_attributes = line_in.rstrip().split()
        l_x = l_attributes[0]
        l_y = l_attributes[1]
        l_z = l_attributes[2]

        # Determine separator
        if not ascii_format :
            line_out = str(l_x) + " " + str(l_y) + " " + str(l_z) 
            l_separator = " "
        if int(ascii_format) == int(FORMAT_XYZ_SPACE) :
            line_out = str(l_x) + " " + str(l_y) + " " + str(l_z) 
            l_separator = " "
        if int(ascii_format) == int(FORMAT_YXZ_SPACE) :
            line_out = str(l_y) + " " + str(l_x) + " " + str(l_z) 
            l_separator = " "
        if int(ascii_format) == int(FORMAT_XYZ_SEMICOLON) :
            line_out = str(l_x) + ";" + str(l_y) + ";" + str(l_z)  
            l_separator = ";"
        if int(ascii_format) == int(FORMAT_YXZ_SEMICOLON) :
            line_out = str(l_y) + ";" + str(l_x) + ";" + str(l_z) 
            l_separator = ";"
        if int(ascii_format) == int(FORMAT_XYZ_PIPE) :
            line_out = str(l_x) + "|" + str(l_y) + "|" + str(l_z)  
            l_separator = "|"
        if int(ascii_format) == int(FORMAT_YXZ_PIPE) :
            line_out = str(l_y) + "|" + str(l_x) + "|" + str(l_z) 
            l_separator = "|"
        if int(ascii_format) == int(FORMAT_XYZ_COMMA) :
            line_out = str(l_x) + "," + str(l_y) + "," + str(l_z) 
            l_separator = ","
        if int(ascii_format) == int(FORMAT_YXZ_COMMA) :
            line_out = str(l_y) + "," + str(l_x) + "," + str(l_z) 
            l_separator = ","
        if int(ascii_format) == int(FORMAT_XYZ_GML) :
            line_out = "<gml:Point gml:id=\"" + str(nr) + "\" depth=\"" + str(l_z) + "\" srsName=\"urn:ogc:def:crs:EPSG:6.6:" + str(epsg_out) + "\"><gml:coordinates>" + str(l_x) + " " + str(l_y) + "</gml:coordinates></gml:Point>" + "\n"
        if int(ascii_format) == int(FORMAT_YXZ_GML) :
            line_out = "<gml:Point gml:id=\"" + str(nr) + "\" depth=\"" + str(l_z) + "\" srsName=\"urn:ogc:def:crs:EPSG:6.6:" + str(epsg_out) + "\"><gml:coordinates>" + str(l_y) + " " + str(l_x) + "</gml:coordinates></gml:Point>" + "\n"

        # Add remaining attributes
        if l_separator :
            for j in range( 3, len(l_attributes) ) :
                line_out = line_out + l_separator + str(l_attributes[j])

        # Return formatted line
        return line_out

    def format_output_line (self , file_out, line_in, multiplication_factor, coordTrans, ascii_format, epsg_out, nr) :
        """Function to format ascii output line"""

        l_attributes = line_in.rstrip().split()
        l_x = float(l_attributes[0])
        l_y = float(l_attributes[1])
        l_z = multiplication_factor * float(l_attributes[2])
        # If required: Coordinate transformation
        if coordTrans :
            l_point = ogr.Geometry(ogr.wkbPoint)
            l_point.AddPoint_2D (l_x,l_y)
            l_point.Transform(coordTrans)
            l_x = l_point.GetX()
            l_y = l_point.GetY()

        # Write output line
        if not ascii_format :
            line_out = str(l_x) + " " + str(l_y) + " " + str(l_z) + "\n"
        if ascii_format == FORMAT_XYZ_SPACE :
            line_out = str(l_x) + " " + str(l_y) + " " + str(l_z) + "\n"
        if ascii_format == FORMAT_YXZ_SPACE :
            line_out = str(l_y) + " " + str(l_x) + " " + str(l_z) + "\n"
        if ascii_format == FORMAT_XYZ_SEMICOLON :
            line_out = str(l_x) + ";" + str(l_y) + ";" + str(l_z) + ";" + "\n"
        if ascii_format == FORMAT_YXZ_SEMICOLON :
            line_out = str(l_y) + ";" + str(l_x) + ";" + str(l_z) + ";" + "\n"
        if ascii_format == FORMAT_XYZ_PIPE :
            line_out = str(l_x) + "|" + str(l_y) + "|" + str(l_z) + "|" + "\n"
        if ascii_format == FORMAT_YXZ_PIPE :
            line_out = str(l_y) + "|" + str(l_x) + "|" + str(l_z) + "|" + "\n"
        if ascii_format == FORMAT_XYZ_COMMA :
            line_out = str(l_x) + "," + str(l_y) + "," + str(l_z) + "," + "\n"
        if ascii_format == FORMAT_YXZ_COMMA :
            line_out = str(l_y) + "," + str(l_x) + "," + str(l_z) + "," + "\n"
        if ascii_format == FORMAT_XYZ_GML :
            line_out = "<gml:Point gml:id=\"" + str(nr) + "\" depth=\"" + str(l_z) + "\" srsName=\"urn:ogc:def:crs:EPSG:6.6:" + str(epsg_out) + "\"><gml:coordinates>" + str(l_x) + " " + str(l_y) + "</gml:coordinates></gml:Point>" + "\n"
        if ascii_format == FORMAT_YXZ_GML :
            line_out = "<gml:Point gml:id=\"" + str(nr) + "\" depth=\"" + str(l_z) + "\" srsName=\"urn:ogc:def:crs:EPSG:6.6:" + str(epsg_out) + "\"><gml:coordinates>" + str(l_y) + " " + str(l_x) + "</gml:coordinates></gml:Point>" + "\n"

        # Return
        return line_out

    def lock_survey ( self, object_class_id, survey_id ):
        """Function to lock survey"""
        self.oracle_cursor.callproc("sdb_interface_pck.lockObject", [object_class_id, survey_id ])

    def update_workflow_step ( self, process_object_class_id, object_class_id, object_instance_id ) :
        """Function to update workflow step"""
        self.oracle_cursor.callproc("sdb_interface_pck.updateWorkflowStep",[ process_object_class_id, object_class_id, object_instance_id ])

    def delete_im_temp_table ( self ) :
        """Function to delete data from temp table"""
        del_stmt = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [DELETE_IM_IMP_TEMP_STMT_ID])
        self.oracle_cursor.execute (del_stmt)

    def get_obj_attributes ( self, object_class_id, object_instance_id, attribute_list ) :
        """Function to get value of attribute for object instance"""
        l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>ID</PropertyName><Literal>" + str(object_instance_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [object_class_id, l_query_xml ])
        l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
        values = []
        for attribute in attribute_list :
            l_domain_value_tag = l_result_dom.getElementsByTagName(attribute)[0]
            # If attribute has no value catch exception and set value to None
            try :
                l_value = l_domain_value_tag.childNodes[0].nodeValue
            except :
                l_value = None
            values.append(l_value)
        return values

    def get_obj_attributes_xml ( self, object_class_id, object_instance_id ) :
        """Function to get value of attribute for object instance"""
        l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>ID</PropertyName><Literal>" + str(object_instance_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [object_class_id, l_query_xml ])
        l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
        return l_result_dom

    def get_attribute_name ( self, object_class_id, attribute_column ) :
        l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>OBJECT_CLASS_ID</PropertyName><Literal>" + str(object_class_id) + "</Literal></PropertyIsEqualTo><PropertyIsEqualTo><PropertyName>ATTRIBUTE_COLUMN</PropertyName><Literal>" + str(attribute_column) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [ ATTRIBUTE_CLASS_ID, l_query_xml ])
        l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
        l_attribute_name_tag   = l_result_dom.getElementsByTagName( ATTRIBUTE_NAME_TAG )[0]
        l_attribute_name_value = l_attribute_name_tag.childNodes[0].nodeValue
        return l_attribute_name_value

    def get_object_def ( self, object_class_id ) :
        """Function to get definition XML for object"""
        result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObjectDef", cx_Oracle.CLOB, [object_class_id])
        return result_xml

    def query_object ( self, object_class_id, query_list ) :
        """Function query for object instances based on attribute values in attribute list"""
        l_id_list = []
        l_query_xml = "<Filter><And>"
        l_query_attributes = query_list.keys()
        for l_query_attribute in l_query_attributes :
            l_query_xml = l_query_xml + "<PropertyIsEqualTo><PropertyName>" + l_query_attribute + "</PropertyName><Literal>" + str(query_list[l_query_attribute]) + "</Literal></PropertyIsEqualTo>"
        l_query_xml = l_query_xml + "</And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [object_class_id, l_query_xml ])
        if l_result_xml :
            l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
            l_result_set = l_result_dom.getElementsByTagName("ROW")
            for l_row in l_result_set :
                l_id_tag = l_row.getElementsByTagName("ID")[0]
                l_id = l_id_tag.childNodes[0].nodeValue
                l_id_list.append(l_id)
        return l_id_list

    def set_obj_attributes ( self, object_class_id, object_instance_id, attribute_list ) :
        """Function to set value of attribute for object instance"""
        try :
            self.logger.info( "Store attributes in database" )

            # Ascii implementation
            #l_mut_xml = "<ROWSET><ROW><ID>" + str(object_instance_id) + "</ID>"
            #l_attribute_keys = attribute_list.keys()
            #for l_attribute_key in l_attribute_keys :
            #    l_mut_xml = l_mut_xml + "<" + l_attribute_key + ">" + str(attribute_list[l_attribute_key]) + "</" + l_attribute_key + ">"
            #l_mut_xml = l_mut_xml + "</ROW></ROWSET>"

            # XML implementation
            
            # Build DOM
            doc = xml.dom.minidom.Document()
            rowset = doc.createElement("ROWSET")
            doc.appendChild(rowset)
            row = doc.createElement("ROW")
            rowset.appendChild(row)

            # Add ID attribute
            attribute = doc.createElement("ID")
            row.appendChild(attribute)
            value = doc.createTextNode(object_instance_id)
            attribute.appendChild(value)

            # Add attributes
            attribute_keys = attribute_list.keys()
            for attribute_key in attribute_keys :
                attribute = doc.createElement(attribute_key)
                row.appendChild(attribute)
                value = doc.createTextNode(str(attribute_list[attribute_key]))
                attribute.appendChild(value)
            
            # Get XML as string
            l_mut_xml = doc.toxml()

            # Update attributes
            self.logger.info("Update attributes")
            l_obj_id = self.oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [object_class_id, 'U', l_mut_xml ])
            l_obj_id = l_obj_id

        except Exception, err:
            self.logger.critical( "Store attributes in database failed:ERROR: %s\n" % str(err))
            raise

    def del_obj_instance ( self, object_class_id, object_instance_id ) :
        """Function to set value of attribute for object instance"""
        try :
            self.logger.info( "Delete instance " + str(object_instance_id) + " from DB" )

            # Build DOM
            doc = xml.dom.minidom.Document()
            rowset = doc.createElement("ROWSET")
            doc.appendChild(rowset)
            row = doc.createElement("ROW")
            rowset.appendChild(row)

            # Add ID attribute
            attribute = doc.createElement("ID")
            row.appendChild(attribute)
            value = doc.createTextNode(object_instance_id)
            attribute.appendChild(value)

            # Get XML as string
            l_mut_xml = doc.toxml()

            # Update attributes
            self.logger.info("Update attributes")
            l_obj_id = self.oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [object_class_id, 'D', l_mut_xml ])
            l_obj_id = l_obj_id

        except Exception, err:
            self.logger.critical( "Store attributes in database failed:ERROR: %s\n" % str(err))
            raise

    def ins_obj_attributes ( self, object_class_id, attribute_list ) :
        """Function to set value of attribute for object instance"""
        try :
            self.logger.info( "Insert attributes in database" )
            if object_instance_id :
                l_mut_xml = "<ROWSET><ROW>"
                l_attribute_keys = attribute_list.keys()
                for l_attribute_key in l_attribute_keys :
                    l_mut_xml = l_mut_xml + "<" + l_attribute_key + ">" + str(attribute_list[l_attribute_key]) + "</" + l_attribute_key + ">"
                l_mut_xml = l_mut_xml + "</ROW></ROWSET>"
                # Insert attributes
                l_obj_id = self.oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [object_class_id, 'U', l_mut_xml ])
                return l_obj_id
        except Exception, err:
            self.logger.critical( "Insert attributes in database failed:ERROR: %s\n" % str(err))
            raise


    def get_im_id ( self, object_class_id, im_attribute, object_instance_id ) :
            attributes = [ im_attribute ]
            values = self.get_obj_attributes ( object_class_id, object_instance_id, attributes )
            im_id = values[0]
            return im_id

    def get_epsg_code_db ( self ) :
        """Function to get epsg code from database"""
        l_epsg_code = self.oracle_cursor.callfunc("sdb_interface_pck.getepsgcodedb", cx_Oracle.NUMBER)
        return l_epsg_code

    def get_wkt_epsg_code ( self, epsg_code ) :
        """Function to get epsg code from database"""
        l_query_xml  = "<Filter><And>"
        l_query_xml  = l_query_xml + "<PropertyIsEqualTo><PropertyName>" + str(EPSG_CODE_COL) + "</PropertyName><Literal>" + str(epsg_code) + "</Literal></PropertyIsEqualTo>"
        l_query_xml  = l_query_xml + "</And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [GEODETIC_HORIZ_CLASS_ID, l_query_xml ])
        if l_result_xml :
            l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
            l_result_set = l_result_dom.getElementsByTagName("ROW")
            for l_row in l_result_set :
                l_wkt_tag = l_row.getElementsByTagName(WKT_UNFORM_COL)[0]
                l_wkt     = l_wkt_tag.childNodes[0].nodeValue
        if l_wkt :
            l_wkt_epsg_code = htmldecode(l_wkt)
            #l_wkt_epsg_code = l_wkt
        else :
            l_wkt_epsg_code = None
        return l_wkt_epsg_code

    def get_wkt_coord_sys_id ( self, coord_sys_id ) :
        """Function to get epsg code from database"""
        l_query_xml  = "<Filter><And>"
        l_query_xml  = l_query_xml + "<PropertyIsEqualTo><PropertyName>ID</PropertyName><Literal>" + str(coord_sys_id) + "</Literal></PropertyIsEqualTo>"
        l_query_xml  = l_query_xml + "</And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [GEODETIC_HORIZ_CLASS_ID, l_query_xml ])
        if l_result_xml :
            l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
            l_result_set = l_result_dom.getElementsByTagName("ROW")
            for l_row in l_result_set :
                l_wkt_tag = l_row.getElementsByTagName(WKT_UNFORM_COL)[0]
                l_wkt     = l_wkt_tag.childNodes[0].nodeValue
        if l_wkt :
            l_wkt_epsg_code = htmldecode(l_wkt)
            #l_wkt_epsg_code = l_wkt
        else :
            l_wkt_epsg_code = None
        return l_wkt_epsg_code

    def get_coord_sys_id_db ( self ) :
        """Function to get epsg code from database"""
        l_coord_sys_id_db = self.oracle_cursor.callfunc("sdb_interface_pck.getCoordSysIdDb", cx_Oracle.NUMBER)
        return l_coord_sys_id_db

    def get_attribute_type ( self, object_class_id, attribute_name ) :
        attribute_type_id = self.oracle_cursor.callfunc("sdb_interface_pck.getAttrTypeId", cx_Oracle.NUMBER, [ object_class_id, attribute_name ] )
        return attribute_type_id

    def get_domain_value ( self, object_class_id, attribute_name, attribute_id ) :
        domain_value = self.oracle_cursor.callfunc("sdb_interface_pck.getDomainValue", cx_Oracle.STRING, [ object_class_id, attribute_name, attribute_id ] )
        return domain_value

    def get_attribute_properties ( self, object_class_id, attribute_name ) :
        """Function to test whether attribute is system attribute"""
        attr_is_visible = False
        # First get attribute id
        l_query_xml = "<Filter><And>"
        l_query_xml = l_query_xml + "<PropertyIsEqualTo><PropertyName>" + OBJECT_CLASS_COL + "</PropertyName><Literal>" + str(object_class_id) + "</Literal></PropertyIsEqualTo>"
        l_query_xml = l_query_xml + "<PropertyIsEqualTo><PropertyName>" + ATTR_NAME_COL + "</PropertyName><Literal>" + str(attribute_name) + "</Literal></PropertyIsEqualTo>"
        l_query_xml = l_query_xml + "</And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [ATTRIBUTE_CLASS_ID, l_query_xml ])
        if l_result_xml :
            l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
            l_result_set = l_result_dom.getElementsByTagName("ROW")
            for l_row in l_result_set :
                l_tag         = l_row.getElementsByTagName("ID")[0]
                try :
                    l_attr_id     = l_tag.childNodes[0].nodeValue
                except :
                    l_attr_id     = None
                l_tag         = l_row.getElementsByTagName(ATTR_LABEL_COL)[0]
                try :
                    l_attr_lb     = l_tag.childNodes[0].nodeValue
                except :
                    l_attr_lb     = None
                l_tag         = l_row.getElementsByTagName(ATTR_GROUP_ID_COL)[0]
                try :
                    l_attr_gr_id  = l_tag.childNodes[0].nodeValue
                except :
                    l_attr_gr_id  = Noe
                l_tag         = l_row.getElementsByTagName(ORDER_GROUP_COL)[0]
                try :
                    l_order_gr_id = l_tag.childNodes[0].nodeValue
                except :
                    l_order_gr_id = None

        # Now query attribute view table to see whether attribute is visible
        l_query_xml = "<Filter><And>"
        l_query_xml = l_query_xml + "<PropertyIsEqualTo><PropertyName>" + VIEW_ATTR_ID_COL + "</PropertyName><Literal>" + str(l_attr_id) + "</Literal></PropertyIsEqualTo>"
        l_query_xml = l_query_xml + "</And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [ATTR_VIEW_DEF_CLASS_ID, l_query_xml ])
        if l_result_xml :
            l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
            l_result_set = l_result_dom.getElementsByTagName("ROW")
            for l_row in l_result_set :
                l_tag     = l_row.getElementsByTagName(VIEW_VISIBLE_COL)[0]
                l_visible = l_tag.childNodes[0].nodeValue
                if str(l_visible) == "T" :
                    attr_is_visible = True
        return attr_is_visible, l_attr_lb, l_attr_gr_id, l_order_gr_id

    def write_emodnet_points_to_db ( self, import_file, nr_columns, separator, im_id ) :
        """Function write points to database"""
        try :
            self.logger.info( "Write points to database")
            
            # Determine insert statement based on number of columns (3 of 12)
            self.logger.info ( "Build insert statememt" )            
            if int(nr_columns) == int(3) :
                insert_stmt = 'insert into sdb_im_import_temp ( x, y, z ) values ( :1, :2, :3 )'    
            if int(nr_columns) == int(12) :
                insert_stmt = 'insert into sdb_im_import_temp ( x, y, z, '
                insert_stmt = insert_stmt + ' customattribute0, customattribute1, customattribute2, customattribute3, customattribute4, '
                insert_stmt = insert_stmt + ' customattribute5, customattribute6, customattribute7, customattribute8 ) '                
                insert_stmt = insert_stmt + ' values ( :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12 )'
          
            # Count number of points
            self.logger.info ( "Count number of points in grid" )
            file = open(import_file,'r')
            nr_of_lines = 0
            for line in file :
                nr_of_lines = nr_of_lines + 1
                if nr_of_lines % 10000000 == 0 :
                    self.logger.info(str(nr_of_lines) + " counted")
            file.close()
            self.logger.info("Total number of points in grid: " + str(nr_of_lines))               
            
            # Now read points from file and insert into array
            self.logger.info ( "Start inserting points into database" )
            skipped_file = 'c:/emodnet/skipped_rows.txt'
            depths = []
            i = 0
            j = 0
            fIn = open(import_file,'r')  
            fOut = open(skipped_file,'w')  
            
            # Loop through file
            for line in fIn : 

                # Split line into columns
                c = line.rstrip().split(separator)

                # Write columns to array type(i) is float
                try :
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
                        depths.append( ( float(c[0]), float(c[1]), float(c[4]), str(c[3]), str(c[2]), str(c[5]), str(c[6]), str(c[7]), str(c[8]), str(c[9]), str(c[10]), str(c[11]) ) )
                        i = i + 1
                    if nr_columns == 13 :
                        depths.append( ( float(c[0]), float(c[1]), float(c[2]), str(c[3]), str(c[4]), str(c[5]), str(c[6]), str(c[7]), str(c[8]), str(c[9]), str(c[10]), str(c[11]), str(c[12]) ) )
                        i = i + 1
                except Exception, err :
                    fOut.write(line + '\n')
                    j = j + 1
                
                if i % 1000000 == 0 or i == int(nr_of_lines):
                    self.oracle_cursor.prepare( insert_stmt )
                    self.oracle_cursor.executemany(None, depths)                    
                    self.logger.info(str(i) + " points written to database")
                    depths = []
            self.logger.info(str(j) + " points skipped")
                
            # Close file when all points are inserted and create spatial index on database
            fIn.close()
            fOut.close()
            
            self.logger.info("Generate HH codes and spatial index on database")
            self.oracle_cursor.callproc("sdb_load_data_pck.load_emodnetgrid", [ im_id ]) 
           
            return i
            
        except Exception, err:
            self.logger.critical( "Write points to database failed:ERROR: %s\n" % str(err))
            raise


    def insert_im_hull( self, object_class_id, survey_id, hull_wkt, epsg_id_source, link_distance ):
        """Function to insert hull into Oracle database"""
        # Update attribute hull generated to T and insert hull geometry
        if object_class_id == IM_CLASS_ID :
            l_hull_gen_col  = IM_HULL_GENERATED_COL
            l_hull_col      = IM_HULL_COL
            l_link_dist_col = IM_LINK_DISTANCE_COL
        l_mut_xml = "<ROWSET><ROW><ID>" + str(survey_id) + "</ID><" + l_hull_gen_col + ">T</" + l_hull_gen_col + "><" + l_link_dist_col + ">" + str(link_distance) + "</" + l_link_dist_col + "></ROW></ROWSET>"
        l_sdo_wkt = self.oracle_cursor.var(cx_Oracle.CLOB)
        l_sdo_wkt.setvalue(0, hull_wkt)
        # Store geometry
        self.oracle_cursor.callproc("sdb_interface_pck.setGeom",[object_class_id, survey_id, l_hull_col, l_sdo_wkt, epsg_id_source])
        # Update attributes
        l_obj_id = self.oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [object_class_id, 'U', l_mut_xml ])

    def store_hull ( self, object_class_id, object_instance_id, wkt_geom ) :
        geom = self.oracle_cursor.var(cx_Oracle.CLOB)
        geom.setvalue(0, wkt_geom)
        geom_col = 'SYS_GEOM001'
        self.oracle_cursor.callproc("sdb_interface_pck.setGeom",[object_class_id, object_instance_id, geom_col, geom])   	
	
    def add_im_to_personal_cm ( self, im_id ) :
	self.oracle_cursor.callproc(" sdb_continuous_model_pck.add_im_to_personal_cm",[im_id])

    def insert_hull( self, object_class_id, object_instance_id, hull_wkt, geom_col, epsg_id_source ):
        """Function to insert hull into Oracle database"""
        # Update attribute hull generated to T and insert hull geometry
        l_mut_xml = "<ROWSET><ROW><ID>" + str(object_instance_id) + "</ID></ROW></ROWSET>"
        l_sdo_wkt = self.oracle_cursor.var(cx_Oracle.CLOB)
        l_sdo_wkt.setvalue(0, hull_wkt)
        # Store geometry
        self.oracle_cursor.callproc("sdb_interface_pck.setGeom",[object_class_id, object_instance_id, geom_col, l_sdo_wkt, epsg_id_source])

    def add_trackline_to_im ( self, im_id, trackline_list ) :
        """Function to add tracklines to IM"""
        l_tr_list = trackline_list.split(',')
        for l_tr_id in l_tr_list :
            l_mut_xml = "<ROWSET><ROW><ID>" + str(l_tr_id) + "</ID><" + TL_IM_COL + ">" + str(im_id) + "</" + TL_IM_COL + "></ROW></ROWSET>"
            l_obj_id = self.oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [TL_CLASS_ID, 'U', l_mut_xml ])

    def remove_tracklines_from_im ( self, im_id ) :
        """Function to remove tracklines from IM"""
        self.oracle_cursor.callproc("sdb_interface_pck.deleteItemFromList",[TL_CLASS_ID, TL_IM_COL, im_id])


    def set_bathyspace ( self, survey_id, bathyspace_file, bathyspace_type, epsg_id, source_files, cellsize, file_format_id) :
        """Function to store bathyspace parameters"""
        bathyspace_file = convert_special_char_for_xml ( bathyspace_file )
        source_files = convert_special_char_for_xml ( source_files )
        l_mut_xml = "<ROWSET><ROW><ID>" + str(survey_id) + "</ID><" + IM_GRID_CELL_SIZE_COL + ">" + str(cellsize) + "</" + IM_GRID_CELL_SIZE_COL + "><" + IM_SOURCE_FILES_COL + ">" + source_files + "</" + IM_SOURCE_FILES_COL + "><" + IM_BATHYSP_FILE_COL + ">" + bathyspace_file + "</" + IM_BATHYSP_FILE_COL + "><" + IM_BATHYSP_TYPE_COL + ">" + str(bathyspace_type) + "</" + IM_BATHYSP_TYPE_COL + "><" + IM_INPUT_FORMAT_COL + ">" + str(file_format_id) + "</" + IM_INPUT_FORMAT_COL + "></ROW></ROWSET>"
        # Update attributes
        l_obj_id = self.oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [IM_CLASS_ID, 'U', l_mut_xml ])

    def set_dataprocessing_param_im ( self, survey_id, verdat_id_in, verdat_id_db, epsg_id_db, processed_data_file, data_processing_method) :
        """Function to store data processing paarmeters"""
        processed_data_file = convert_special_char_for_xml ( processed_data_file )
        l_mut_xml = "<ROWSET><ROW><ID>" + str(survey_id) + "</ID><" + IM_PROC_DATA_FILE_COL + ">" + processed_data_file + "</" + IM_PROC_DATA_FILE_COL + "><" + IM_DATAPROCESSING_COL + ">" + str(data_processing_method) + "</" + IM_DATAPROCESSING_COL + "><" + IM_ACCEPTED_COL + ">T</" + IM_ACCEPTED_COL + "></ROW></ROWSET>"
        # Update attributes
        l_obj_id = self.oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [IM_CLASS_ID, 'U', l_mut_xml ])

    def get_trackline ( self, object_class_id, object_id ) :
        """Function to retrieve geometries from database and write to file"""
        l_trackline_col = TL_HULL_GEOM_COL
        l_tr_cursor = self.oracle_connection.cursor()
        l_tr_cursor = self.oracle_cursor.callfunc("sdb_interface_pck.getGeomAsWkt", cx_Oracle.CURSOR, [object_class_id, object_id, l_trackline_col])
        l_tr_geom = None
        for l_tr in l_tr_cursor :
            l_tr_geom = str(l_tr[1])
        return l_tr_geom

    def get_geom ( self, object_class_id, object_id, geom_col ) :
        """Function to retrieve geometries from database and write to file"""
        l_geom_cursor = self.oracle_connection.cursor()
        l_geom_cursor = self.oracle_cursor.callfunc("sdb_interface_pck.getGeomAsWkt", cx_Oracle.CURSOR, [object_class_id, object_id, geom_col])
        for l_geom in l_geom_cursor :
            l_geom_wkt = str(l_geom[1])
        return l_geom_wkt

    def get_intersection ( self, geom_wkt_1, geom_wkt_2) :
        # Function to calculate intersection between 2 geometries
        l_epsg_code_db = int(self.get_epsg_code_db())
        geom_1         = self.oracle_cursor.var(cx_Oracle.CLOB)
        geom_1.setvalue(0, geom_wkt_1)
        geom_2         = self.oracle_cursor.var(cx_Oracle.CLOB)
        geom_2.setvalue(0, geom_wkt_2)
        l_geom_wkt     = self.oracle_cursor.callfunc("sdb_interface_pck.getIntersectGeometry", cx_Oracle.CLOB, [geom_1, geom_2, l_epsg_code_db])
        return str(l_geom_wkt)

    def get_difference ( self, geom_wkt_1, geom_wkt_2) :
        # Function to calculate intersection between 2 geometries
        l_epsg_code_db = int(self.get_epsg_code_db())
        geom_1         = self.oracle_cursor.var(cx_Oracle.CLOB)
        geom_1.setvalue(0, geom_wkt_1)
        geom_2         = self.oracle_cursor.var(cx_Oracle.CLOB)
        geom_2.setvalue(0, geom_wkt_2)
        l_geom_wkt     = self.oracle_cursor.callfunc("sdb_interface_pck.getDifferenceGeometry", cx_Oracle.CLOB, [geom_1, geom_2, l_epsg_code_db])
        return str(l_geom_wkt)

    def get_union ( self, geom_wkt_1, geom_wkt_2) :
        # Function to calculate intersection between 2 geometries
        l_epsg_code_db = int(self.get_epsg_code_db())
        geom_1         = self.oracle_cursor.var(cx_Oracle.CLOB)
        geom_1.setvalue(0, geom_wkt_1)
        geom_2         = self.oracle_cursor.var(cx_Oracle.CLOB)
        geom_2.setvalue(0, geom_wkt_2)
        l_geom_wkt     = self.oracle_cursor.callfunc("sdb_interface_pck.getUnionGeometry", cx_Oracle.CLOB, [geom_1, geom_2, l_epsg_code_db])
        return str(l_geom_wkt)

    def generate_imsegments ( self, im_list, db_priority, approximate_date, job_id ) :
        """Function to generate cookie based on survey list en approximate date"""
        try :
            # First generate cookies, cookies are stored in temp table in database
            self.oracle_cursor.callproc("sdb_interface_pck.construct_combined_im", [ im_list, db_priority, approximate_date, job_id ])
        except Exception, err:
            print "Generate IM segments failed failed: ERROR: " + str(err)
            raise

    def get_topological_relation ( self, geom_wkt_1, geom_wkt_2 ) :
        # Function to calculate intersection between 2 geometries
        l_epsg_code_db = int(self.get_epsg_code_db())
        geom_1         = self.oracle_cursor.var(cx_Oracle.CLOB)
        geom_1.setvalue(0, geom_wkt_1)
        geom_2         = self.oracle_cursor.var(cx_Oracle.CLOB)
        geom_2.setvalue(0, geom_wkt_2)
        topological_relation  = self.oracle_cursor.callfunc("sdb_interface_pck.getTopologicalRelation", cx_Oracle.CLOB, [geom_1, geom_2, l_epsg_code_db])
        return str(topological_relation)

    def write_separation_model_file ( self, fOut, shape_file_name, sep_model_id, is_algorithm  ) :
        """Function to get list of file_ids from database for separation model"""

        self.logger.info("Get separation model points from DB for separation model " + str(sep_model_id) )

        l_separator = " "

        # Generate sm file segments
        self.oracle_cursor.callproc("sdb_interface_pck.construct_sep_model", [ sep_model_id ] )

        # Get query
        l_query_sm_file = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [SELECT_SM_SEGMENT_STMT_ID])
        l_query_sm_data = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [SELECT_SM_DATA_STMT_ID])

        # Get list of sm file segments
        self.logger.info("Get list of sm file segments")
        l_sm_file_list = {}
        self.oracle_cursor.arraysize = 100000
        self.oracle_cursor.execute( l_query_sm_file )
        l_sm_files = self.oracle_cursor.fetchmany()
        for l_sm_file in l_sm_files :
            l_sm_file_id  = int(l_sm_file[0])
            l_sm_seg_geom = str(l_sm_file[1])
            l_sm_file_list[ l_sm_file_id ] = l_sm_seg_geom

        # Write separation model boundary as shapefile
        self.logger.info("Write separation model boundary as shapefile")
        l_epsg_code_db = self.get_epsg_code_db()
        BathyExecutablesLib.ogr_write_separation_model_to_shape ( self.oracle_connection, self.logger, l_sm_file_list, shape_file_name, l_epsg_code_db )

        # If it is not an algorithm, for each segment get points
        self.logger.info("Get points when separation model is grid")
        if str(is_algorithm) == "F" :
            l_nr = 0
            self.oracle_cursor.arraysize = 100000
            self.oracle_cursor.execute(l_query_sm_data)
            while 1 :
                l_depths = self.oracle_cursor.fetchmany()
                if not l_depths :
                    break
                else :
                    for l_depth in l_depths :
                        l_nr = l_nr + 1
                        fOut.write( str(l_depth[0]) + str(l_separator) + str(l_depth[1]) + str(l_separator) + str( l_depth[2] ) + "\n" )
            self.logger.info( "Number of points in separation model: " + str(l_nr) )

    def get_imsegments_list ( self, job_id ) :
        """Function te get list of cookies from database for IM with wkt polygon"""
        l_cookie_list = []
        #l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>" + COOKIE_CMID_COL + "</PropertyName><Literal>" + str(cm_id) + "</Literal></PropertyIsEqualTo><PropertyIsEqualTo><PropertyName>" + COOKIE_GEOM_COL + "</PropertyName><Literal>2003</Literal></PropertyIsEqualTo></And></Filter>"
        l_query_xml  = "<Filter><And><PropertyIsEqualTo><PropertyName>" + IMSEG_JOBID_COL + "</PropertyName><Literal>" + str(job_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [IMSEGMENT_CLASS_ID, l_query_xml ])
        if l_result_xml :
            l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
            l_result_set = l_result_dom.getElementsByTagName("ROW")
            for l_row in l_result_set :
                l_id_tag = l_row.getElementsByTagName("ID")[0]
                l_id = l_id_tag.childNodes[0].nodeValue
                l_cookie_list.append(l_id)
        return l_cookie_list
    
#####################################################

    def get_personal_cookie_list ( self, user_id ) : 
	    l_stmt = 'select t1.id from sdb_cookie t1, sdb_continuousmodel t2 where t2.id = t1.sys502 and t2.sys003 = ' + str(user_id)
	    l_cookie_list = []
	    self.oracle_cursor.arraysize = 100000
	    self.oracle_cursor.execute( l_stmt )
	    l_cookie_rows = self.oracle_cursor.fetchmany()	
	    for l_cookie_row in l_cookie_rows :
		l_cookie_list.append(int(l_cookie_row[0]))
	    return l_cookie_list
     
    def write_depths_to_product_source_file ( self, l_cookie_id, fOut ) :
	l_stmt = "select hod.positie.sdo_point.x, hod.positie.sdo_point.y, hod.depth"
	l_stmt = l_stmt + " from   sdb_hoogte_diepte hod"
	l_stmt = l_stmt + " ,      sdb_cookie        coo"
	l_stmt = l_stmt + " where  hod.wdg_id = coo.SYS503"
	l_stmt = l_stmt + " and    sdo_anyinteract ( hod.positie, coo.SYS_GEOM501) = \'TRUE\'"
	l_stmt = l_stmt + " and    coo.ID = :cookieId"	
	
	# Execute query
	self.oracle_cursor.arraysize = 100000
	self.oracle_cursor.execute(l_stmt, cookieId = l_cookie_id )

	# Write points to file 
	separator = ' '
	l_nr = 0
	while 1 :
	    l_depths = self.oracle_cursor.fetchmany()
	    if not l_depths :
		break
	    else :
		for l_depth in l_depths :
		    l_nr = l_nr + 1
		    fOut.write( str(l_depth[0]) + str(separator) + str(l_depth[1]) + str(separator) + str( l_depth[2] ) + "\n" )
	return l_nr	
    
###############################################################################

    def aggregate_im_seg_geometry ( self, object_instance_id_list ) :
        """Function to aggregate geometry from im segment list"""
        nr_segments = 0
        for object_instance_id in object_instance_id_list :
            # Get im_id of im segment
            attributes = [ IMSEG_IM_ID_COL  ]
            values = self.get_obj_attributes ( IMSEGMENT_CLASS_ID, object_instance_id, attributes )
            im_id = values[0]
            if int(nr_segments) == int(0) :
                im_list = im_id
                nr_segments = nr_segments + 1
            else :
                im_list = im_list + str(",") + im_id
        geom_wkt = self.oracle_cursor.callfunc("sdb_interface_pck.get_im_list_mbr", cx_Oracle.CLOB, [ im_list ])
        return str(geom_wkt)

    def write_xyz_depths_to_file_for_cookie_in_im ( self, fOut, survey_id, cookie_id, separator ) :
        """Function to write depths in union cookie IM to file"""
        try :

            self.logger.debug("Get query")

            # Get query
#            l_query = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [SELECT_COOKIE_IN_IM_STMT_ID])
            l_attributes   = [ DML_TEXT_COL ]
            l_values       = self.get_obj_attributes ( CLIENT_DML_CLASS_ID, SELECT_COOKIE_IN_IM_STMT_ID, l_attributes )
            l_query        = str(l_values[0])

            # Remove html escaped characters
            l_query = htmldecode ( l_query )
            self.logger.debug( "Cookie_id = " + str(cookie_id) )
            self.logger.debug( "Survey_id = " + str(survey_id) )

            # Execute query
            self.oracle_cursor.arraysize = 100000
            self.oracle_cursor.execute(l_query, cookieId = cookie_id, surveyId = survey_id )

            self.logger.debug( "Query executed")

            # Write points to file
            l_nr = 0
            while 1 :
                l_depths = self.oracle_cursor.fetchmany()
                if not l_depths :
                    break
                else :
                    for l_depth in l_depths :
                        l_nr = l_nr + 1
                        fOut.write( str(l_depth[0]) + str(separator) + str(l_depth[1]) + str(separator) + str( l_depth[2] ) + "\n" )
            return l_nr

        except Exception, err:
            self.logger.critical( "Writing depths to file failed: ERROR: " + str(err) )
            raise

    def element_query ( self, query_in, im_id ) :
        #self.logger.info("IN: " + str(query_in) )
        if QUERY_ON_ELEMENTS :
            query_out = query_in.replace('sdb_cookie','sdb_cookieelements')
            query_out = query_out.replace('coo.SYS_GEOM501','coo.SYS_GEOM001')
            query_out = query_out.replace('coo.ID','coo.SYS001')
            query_out = query_out.replace('hod.wdg_id = coo.SYS503','hod.wdg_id = ' + str(im_id))
        else :
            query_out = query_in
        #self.logger.info("IN: " + str(query_out) )
        return query_out

    def write_xyz_depths_to_file ( self, fOut, survey_id, product_area, cookie_id, im_segment_id, separator, sampling_method ) :
        """Function to write trackline depths to file"""
        try :

            # If you are dealing with cookies and grid sampling method is used, check if model is SENS grid
            # If it is a SENS grid, you can use the shallowest or deepest point in a grid
            # Check if cookie geometry = IM geometry, if TRUE avoid spatial query
            if cookie_id :
                attributes = [ IM_IM_FORMAT_DB, COOKIE_IMID_COL ]
                values     = self.get_obj_attributes ( COOKIE_CLASS_ID, cookie_id, attributes )
                im_format  = values[0]
                l_im_id    = values[1]
                if product_area :
                    l_cookie_geom_wkt = self.get_geom(COOKIE_CLASS_ID, cookie_id, COOKIE_GEOM_COL)
                    l_im_geom_wkt = self.get_geom(IM_CLASS_ID, l_im_id, IM_HULL_COL)
                    l_topological_relation = self.get_topological_relation(l_im_geom_wkt, l_cookie_geom_wkt)
                    if l_topological_relation == "EQUAL"  :
                        survey_id = l_im_id
                        cookie_id = None
                        product_area = None

            # Individual models
            if survey_id and product_area and not cookie_id and not im_segment_id :
                self.logger.info("Retrieve all points for survey within polygon")
                l_poly_wkt = self.oracle_cursor.var(cx_Oracle.CLOB)
                l_poly_wkt.setvalue(0, product_area)
                l_query = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [SELECT_IM_DATA_STMT_ID])
                self.oracle_cursor.arraysize = 100000
                self.oracle_cursor.execute(l_query, wdgId = survey_id, polygon = l_poly_wkt )
            if survey_id and not product_area and not cookie_id and not im_segment_id :
                self.logger.info("Retrieve all points for survey")
                l_query = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [SELECT_IM_XYZ_STMT_ID])
                self.oracle_cursor.arraysize = 100000
                self.oracle_cursor.execute(l_query, wdgId = survey_id )

            # Cookies; for ccokies check if you have to use shallowest/deepest depth for contours and spot soundings
            if not survey_id and not product_area and not im_segment_id and cookie_id :
                self.logger.info("Retrieve all points for a cookie")
                if sampling_method == BathyExecutablesLib.MG_SHALLOWEST_VAL and int(im_format) == int(IM_FRMT_SENS)  :
                    self.logger.info("Use shallowest depth")
                    l_stmt_id = SELECT_COOKIE_XYS_STMT_ID
                elif sampling_method == BathyExecutablesLib.MG_DEEPEST_VAL and int(im_format) == int(IM_FRMT_SENS)  :
                    self.logger.info("Use deepest depth")
                    l_stmt_id = SELECT_COOKIE_XYD_STMT_ID
                else :
                    l_stmt_id = SELECT_COOKIE_XYZ_STMT_ID
                l_query = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [l_stmt_id])
                l_query = self.element_query( l_query, l_im_id )
                self.oracle_cursor.arraysize = 100000
                self.oracle_cursor.execute(l_query, cookieId = cookie_id )
            if not survey_id and not im_segment_id and product_area and cookie_id :
                self.logger.info("Retrieve points for cookie within product area")
                if sampling_method == BathyExecutablesLib.MG_SHALLOWEST_VAL and int(im_format) == int(IM_FRMT_SENS)  :
                    self.logger.info("Use shallowest depth")
                    l_stmt_id = SELECT_COOKIE_POLY_XYS_STMT_ID
                elif sampling_method == BathyExecutablesLib.MG_DEEPEST_VAL and int(im_format) == int(IM_FRMT_SENS)  :
                    self.logger.info("Use deepest depth")
                    l_stmt_id = SELECT_COOKIE_POLY_XYD_STMT_ID
                else :
                    l_stmt_id = SELECT_COOKIE_POLY_XYZ_STMT_ID
                l_poly_wkt = self.oracle_cursor.var(cx_Oracle.CLOB)
                l_poly_wkt.setvalue(0, product_area)
                l_query = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [l_stmt_id])
                l_query = self.element_query( l_query, l_im_id )
                self.oracle_cursor.arraysize = 100000
                self.logger.info("Polygon = "   + str(product_area))
                self.logger.info("Cookie ID = " + str(cookie_id))
                self.oracle_cursor.execute(l_query, polygon = l_poly_wkt, cookieId = cookie_id )

            # IM segments
            if not survey_id and not cookie_id and not product_area and im_segment_id :
                self.logger.info("Retrieve points for generated IM segment")
                l_query = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [SELECT_IM_SEGMENT_STMT_ID])
                self.oracle_cursor.arraysize = 100000
                self.oracle_cursor.execute(l_query, segmentId = im_segment_id  )
            if not survey_id and not cookie_id and product_area and im_segment_id :
                self.logger.info("Retrieve points for generated IM segment within product area")
                l_poly_wkt = self.oracle_cursor.var(cx_Oracle.CLOB)
                l_poly_wkt.setvalue(0, product_area)
                l_query = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [SELECT_IM_SEGMENT_POLY_STMT_ID])
                self.oracle_cursor.arraysize = 100000
                self.oracle_cursor.execute(l_query, segmentId = im_segment_id, polygon = l_poly_wkt  )

            # Write points to file
            l_nr = 0
            while 1 :
                l_depths = self.oracle_cursor.fetchmany()
                if not l_depths :
                    break
                else :
                    for l_depth in l_depths :
                        l_nr = l_nr + 1
                        fOut.write( str(l_depth[0]) + str(separator) + str(l_depth[1]) + str(separator) + str( l_depth[2] ) + "\n" )
            return l_nr

        except Exception, err:
            self.logger.critical( "Writing depths to file failed: ERROR: " + str(err) )
            raise

    def write_IM_depths_to_file ( self, output_file, im_id, im_format_id, ascii_format_id, point_in_hull, include_attr, depth_positive ) :
        # Write depths to intermediate table on database
        try :
            # First build the insert statement based on im_fomat to import
            self.logger.info( "Export im " + str(im_id) + " with format " + str(im_format_id) )
            select_stmt, nr_columns = self.get_select_statement ( im_format_id )
            select_stmt = select_stmt.upper()

            if str(point_in_hull) == "T" :
                # Change statement, join with geometry of IM
                select_clause = select_stmt.rstrip().split('FROM')[0]
                select_clause = select_clause + " from " + SDB_HOOGTE_DIEPTE + " hod, " + SDB_INDIVIDUALMODEL + " im "
                select_stmt   = select_clause + " where im." + IM_ID + " = hod." + WDG_ID + " and hod." + WDG_ID + " = :wdgId and sdo_anyinteract ( hod." + POSITION + ", im." + IM_HULL_COL + ") = \'TRUE\' "
            #self.logger.debug( select_stmt )
            self.logger.debug( select_stmt )
            self.logger.debug( "Number of columns " + str(nr_columns) )

            # Get epsg_code database
            epsg_code = self.get_epsg_code_db ()

            # Open file
            fOut = open(output_file,'w')
            nr = 0

            # Execute query
            self.oracle_cursor.arraysize = SELECTARRAYSIZE
            self.oracle_cursor.execute(select_stmt, wdgId = im_id )

            # Loop through rows and convert
            self.logger.info( "Start selecting points" )
            while 1 :
                depths = self.oracle_cursor.fetchmany()
                if not depths :
                    break
                else :
                    for depth in depths :
                        nr = nr + 1
                        line = ""
                        if str(include_attr) == "T" :
                            for i in range ( 0, int(nr_columns) ) :
                                if i == 2 and depth_positive == "T" :
                                    depth_value = float(-1.0) * float(depth[i])
                                    line = line + " " + str(depth_value)
                                else :
                                    line = line + " " + str(depth[i])
                            line = line + "\n"
                        else :
                            if depth_positive == "T" :
                                line = str(depth[0]) + " " + str(depth[1]) + " " + str( float(-1.0)*float(depth[2]) ) + "\n"
                            else :
                                line = str(depth[0]) + " " + str(depth[1]) + " " + str(depth[2]) + "\n"
                        line_out = self.format_IM_line (  line, ascii_format_id, nr, epsg_code  ) + "\n"
                        fOut.write( line_out )

            # All depths are written to file
            fOut.close()

            # return
            return nr

        except Exception, err:
            self.logger.critical( "Writing depths to file failed: ERROR: " + str(err) )
            raise

    def get_attribute_param_list ( self, object_class_id, attribute_name ) :
        """Function to build list with attributes"""
        try :
            stmt      = "select distinct a.attribute_group_id, nvl(a.orderingroup,999), a.attribute_label, a.attribute_type_id from sdb_object_class_attr a , sdb_object_attribute_view v where a.object_class_id = " + str(object_class_id) + " and a.id = v.attribute_id and v.visible = \'T\' and a.attribute_name = \'" + str(attribute_name) + "\' "
            resultset = self.oracle_cursor.execute(stmt)
            a_attribute_group_id   = None
            a_order_in_group       = None
            a_attribute_label      = None
            a_attribute_type       = None
            if resultset :
                for row in resultset :
                    if row :
                        a_attribute_group_id   = int(row[0])
                        a_order_in_group       = int(row[1])
                        a_attribute_label      = str(row[2])
                        a_attribute_type       = int(row[3])
            return a_attribute_group_id, a_order_in_group, a_attribute_label, a_attribute_type
        except Exception, err:
            self.logger.critical("Error building attribute list: ERROR: " + str(err))
            raise

    def set_blob ( self, object_class_id, object_instance_id, attribute_name, blob_file, file_name ) :
        """Function to store BLOB"""
        try :
            inputs = []
            inputs.append(open(blob_file, 'rb'))
            for input in inputs:
                binary_data = input.read()
                blobfile = self.oracle_cursor.var(cx_Oracle.BLOB)
                blobfile.setvalue(0, binary_data)
                self.oracle_cursor.callproc("sdb_interface_pck.setBlob", [object_class_id, object_instance_id, attribute_name, file_name, blobfile ])
        except Exception, err:
            print "Error storing BLOB: ERROR: " + str(err)
            raise

    def get_blob ( self, object_class_id, object_instance_id, attribute_name, blob_file ) :
        """Function to retieve BLOB"""
        try :
          # First open file, then get blob from database and then write to file
          fBlob  = open(blob_file, 'wb')
          blob = self.oracle_cursor.callfunc("sdb_interface_pck.getBlob", cx_Oracle.BLOB, [ object_class_id, object_instance_id, attribute_name ])
          blob_data = blob.read()
          fBlob.write( blob_data )
          fBlob.close()
        except Exception, err:
            print "Error retrieveing BLOB: ERROR: " + str(err)
            raise

    def generate_hull_from_edges ( self, object_class_id, survey_id, link_distance ):
        """Function to start hull generation from edges in database"""
        self.oracle_cursor.callproc("sdb_interface_pck.construct_hull_for_survey", [ object_class_id, survey_id ])
        # Insert link distance into database
        if object_class_id == IM_CLASS_ID :
            l_link_distance_col = IM_LINK_DISTANCE_COL
        if object_class_id == TL_CLASS_ID :
            l_link_distance_col = TL_LINK_DIST_COL
        l_mut_xml = "<ROWSET><ROW><ID>" + str(survey_id) + "</ID><" + l_link_distance_col + ">" + str(link_distance) + "</" + l_link_distance_col + "></ROW></ROWSET>"
        l_obj_id = self.oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [object_class_id, 'U', l_mut_xml ])


    def insert_edges ( self, edges ):
        """Function to insert edges into database"""
        l_insert = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [INSERT_EDGES_STMT_ID])
        self.oracle_cursor.prepare( l_insert )
        self.oracle_cursor.executemany(None, edges)

    def insert_depths (self, insert_stmt_id, depths ) :
        """Function to insert epths read from file into database"""
        l_insert = self.oracle_cursor.callfunc("sdb_interface_pck.getclientdml", str, [insert_stmt_id])
        self.oracle_cursor.prepare( l_insert )
        self.oracle_cursor.executemany(None, depths)

    def get_insert_statement ( self, im_format_id) :
        l_insert  = self.oracle_cursor.callfunc("sdb_interface_pck.getInsertStatement", str, [im_format_id])
        l_nr_cols = self.oracle_cursor.callfunc("sdb_interface_pck.getNrOfColsIm", cx_Oracle.NUMBER, [im_format_id])
        return l_insert, l_nr_cols

    def get_select_statement ( self, im_format_id) :
        l_select  = self.oracle_cursor.callfunc("sdb_interface_pck.getSelectStatement", str, [im_format_id])
        l_nr_cols = self.oracle_cursor.callfunc("sdb_interface_pck.getNrOfColsIm", cx_Oracle.NUMBER, [im_format_id])
        return l_select, l_nr_cols

    def insert_depth ( self, insert_stmt, depths ) :
        """Function to insert depths read from file into database"""
        self.oracle_cursor.prepare( insert_stmt )
        self.oracle_cursor.executemany(None, depths)

    def import_survey ( self, object_class_id, survey_id, subtask_id, multiplication_factor, tiling ):
        """Function to import survey into database"""
        #self.oracle_cursor.callproc("sdb_interface_pck.startImportSurveyDirect", [object_class_id, new_file_name, survey_id, subtask_id, multiplication_factor, tiling ])
        self.oracle_cursor.callproc("sdb_interface_pck.startImportImData", [object_class_id, survey_id, subtask_id, multiplication_factor, tiling ])

    def get_im_dimensions ( self, im_id, epsg_code, factor ) :
        """Function to get dimensions of IM"""
        try:
            self.logger.info( "Get Im dimensions from database" )
            l_cursor_out = self.oracle_connection.cursor()
            l_cursor_out = self.oracle_cursor.callfunc("sdb_interface_pck.getImDimensions", cx_Oracle.CURSOR, [im_id, epsg_code])
            for l_row in l_cursor_out :
                x_min = float(l_row[0])
                x_max = float(l_row[1])
                y_min = float(l_row[2])
                y_max = float(l_row[3])
                z_min = float(l_row[4])
                z_max = float(l_row[5])
            
            # Correct if depths are positive
            z_min = factor * z_min
            z_max = factor * z_max
            if z_min > z_max :
                z_min_tmp = z_min
                z_min     = z_max
                z_max     = z_min_tmp
            self.logger.info ( "IM dimensions: X: " + str(x_min) + ", " + str(x_max) + " Y: " + str(y_min) + ", " + str(y_max) + " Z: " + str(z_min) + ", " + str(z_max) )

            # Return dimensions
            return x_min, x_max, y_min, y_max, z_min, z_max

        except Exception, err:
            self.logger.critical( "Get Im dimensions from database failed: ERROR: " + str(err) )
            raise

    def get_cookie_list ( self, cm_id, wkt_polygon ) :
        """Function te get list of cookies from database for IM with wkt polygon"""
        l_cookie_list = []
        #l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>" + COOKIE_CMID_COL + "</PropertyName><Literal>" + str(cm_id) + "</Literal></PropertyIsEqualTo><PropertyIsEqualTo><PropertyName>" + COOKIE_GEOM_COL + "</PropertyName><Literal>2003</Literal></PropertyIsEqualTo></And></Filter>"
        l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>" + COOKIE_CMID_COL + "</PropertyName><Literal>" + str(cm_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_poly_wkt = self.oracle_cursor.var(cx_Oracle.CLOB)
        l_poly_wkt.setvalue(0, wkt_polygon)
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [COOKIE_CLASS_ID, l_query_xml, l_poly_wkt ])
        if l_result_xml :
            l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
            l_result_set = l_result_dom.getElementsByTagName("ROW")
            for l_row in l_result_set :
                l_id_tag = l_row.getElementsByTagName("ID")[0]
                l_id = l_id_tag.childNodes[0].nodeValue
                l_cookie_list.append(l_id)
        return l_cookie_list

    def get_imsegments_list ( self, job_id ) :
        """Function te get list of cookies from database for IM with wkt polygon"""
        l_cookie_list = []
        #l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>" + COOKIE_CMID_COL + "</PropertyName><Literal>" + str(cm_id) + "</Literal></PropertyIsEqualTo><PropertyIsEqualTo><PropertyName>" + COOKIE_GEOM_COL + "</PropertyName><Literal>2003</Literal></PropertyIsEqualTo></And></Filter>"
        l_query_xml  = "<Filter><And><PropertyIsEqualTo><PropertyName>" + IMSEG_JOBID_COL + "</PropertyName><Literal>" + str(job_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [IMSEGMENT_CLASS_ID, l_query_xml ])
        if l_result_xml :
            l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
            l_result_set = l_result_dom.getElementsByTagName("ROW")
            for l_row in l_result_set :
                l_id_tag = l_row.getElementsByTagName("ID")[0]
                l_id = l_id_tag.childNodes[0].nodeValue
                l_cookie_list.append(l_id)
        return l_cookie_list

    def get_trackline_list ( self, im_id ) :
        """Function to get list of tracklines for IM"""
        l_tr_list = []
        #l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>" + COOKIE_CMID_COL + "</PropertyName><Literal>" + str(cm_id) + "</Literal></PropertyIsEqualTo><PropertyIsEqualTo><PropertyName>" + COOKIE_GEOM_COL + "</PropertyName><Literal>2003</Literal></PropertyIsEqualTo></And></Filter>"
        l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>" + TL_IM_COL + "</PropertyName><Literal>" + str(im_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [TL_CLASS_ID, l_query_xml ])
        if l_result_xml :
            l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
            l_result_set = l_result_dom.getElementsByTagName("ROW")
            for l_row in l_result_set :
                l_id_tag = l_row.getElementsByTagName("ID")[0]
                l_id = l_id_tag.childNodes[0].nodeValue
                l_tr_list.append(l_id)
        return l_tr_list

    def get_survey_type ( self, object_class_id, object_instance_id ) :
        """Function to get type of survey"""
        l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>ID</PropertyName><Literal>" + str(object_instance_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [object_class_id, l_query_xml ])
        l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
        l_domain_value_tag = l_result_dom.getElementsByTagName(IM_SURVEYTYPE_COL)[0]
        l_surveytype = l_domain_value_tag.childNodes[0].nodeValue
        return l_surveytype

    def get_im_attributes ( self, object_class_id, object_instance_id ) :
        """Function to get type of survey"""
        l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>ID</PropertyName><Literal>" + str(object_instance_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [object_class_id, l_query_xml ])
        l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
        l_domain_value_tag = l_result_dom.getElementsByTagName(IM_SURVEYTYPE_COL)[0]
        l_surveytype = l_domain_value_tag.childNodes[0].nodeValue
        l_domain_value_tag = l_result_dom.getElementsByTagName(IM_SEP_MODEL_COL)[0]
        l_verref_id_db = l_domain_value_tag.childNodes[0].nodeValue
        return l_surveytype, l_verref_id_db

    def get_bathyspace  ( self, object_class_id, object_instance_id ) :
        """Function to bathyspace attribues of survey"""
        l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>ID</PropertyName><Literal>" + str(object_instance_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [object_class_id, l_query_xml ])
        l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
        l_domain_value_tag = l_result_dom.getElementsByTagName(IM_BATHYSP_TYPE_COL)[0]
        l_bathyspace_type = l_domain_value_tag.childNodes[0].nodeValue
        l_domain_value_tag = l_result_dom.getElementsByTagName(IM_BATHYSP_FILE_COL)[0]
        l_bathyspace_file = l_domain_value_tag.childNodes[0].nodeValue
        l_domain_value_tag = l_result_dom.getElementsByTagName(IM_INPUT_FORMAT_COL)[0]
        l_input_file_format = l_domain_value_tag.childNodes[0].nodeValue
        return l_bathyspace_type, l_bathyspace_file, l_input_file_format

    def get_bathyspace_type_id  ( self, object_class_id, object_instance_id ) :
        """Function to bathyspace attribues of survey"""
        l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>ID</PropertyName><Literal>" + str(object_instance_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [object_class_id, l_query_xml ])
        l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
        l_domain_value_tag = l_result_dom.getElementsByTagName(IM_BATHYSP_TYPE_COL)[0]
        l_bathyspace_type = l_domain_value_tag.childNodes[0].nodeValue
        return l_bathyspace_type

    def get_bathyspace_file  ( self, object_class_id, object_instance_id ) :
        """Function to bathyspace attribues of survey"""
        l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>ID</PropertyName><Literal>" + str(object_instance_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [object_class_id, l_query_xml ])
        l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
        l_domain_value_tag = l_result_dom.getElementsByTagName(IM_BATHYSP_FILE_COL)[0]
        l_bathyspace_file = l_domain_value_tag.childNodes[0].nodeValue
        return l_bathyspace_file

    def get_insert_stmt_id ( self, object_class_id, object_instance_id ) :
        """Function to get type of survey"""
        # First get data processing ID of IM
        l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>ID</PropertyName><Literal>" + str(object_instance_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [object_class_id, l_query_xml ])
        l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
        l_domain_value_tag = l_result_dom.getElementsByTagName(IM_DATAPROCESSING_COL)[0]
        l_data_processing_id = l_domain_value_tag.childNodes[0].nodeValue
        # Now get insert statement ID from data processing table based on data processing ID
        l_query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>ID</PropertyName><Literal>" + str(l_data_processing_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [DATA_PROCESSING_CLASS_ID, l_query_xml ])
        l_result_dom = xml.dom.minidom.parseString(str(l_result_xml))
        l_domain_value_tag = l_result_dom.getElementsByTagName(DPM_INSERT_STMT_ID_COL)[0]
        l_stmt_id = l_domain_value_tag.childNodes[0].nodeValue
        return l_stmt_id

    def has_sep_model_files (self, sep_model_id) :
        """Function to count number of separation model files for separation model"""
        l_query_xml  = "<Filter><And><PropertyIsEqualTo><PropertyName>" + str(SEP_MOD_ID_COL) + "</PropertyName><Literal>" + str(sep_model_id) + "</Literal></PropertyIsEqualTo></And></Filter>"
        l_result_xml = self.oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [SEP_MOD_FILE_CLASS_ID, l_query_xml ])
        if l_result_xml :
            return True
        else :
            return False

    def commit( self ) :
	"""Function to commit and close connection"""
        self.oracle_connection.commit()

    def commit_close( self ) :
	"""Function to commit and close connection"""
        self.oracle_connection.commit()
        self.oracle_connection.close()



import os.path
#! /usr/bin/python

# standard library imports 
import os
import shutil
import logging

# related third party imports

# local application/library specific imports
import BathyExecutablesLib
import BathyToolsLib
import BathyDbLib


__author__="Terlien"
__date__ ="$28-mei-2010 11:51:55$"

# Module name
BATHYTOOLS        = "BathyTools"
BATHYPROCESSESLIB = "BathyProcessesLib"

# Database process ID
EXP_ASCII_IM           = 272 # Deprecated
ARCHIVE_IM             = 485
ARCHIVE_TRACKLINE      = 486
IMPORT_ASCII_NO_ATTR   = 517 # Deprecated
IMPORT_ASCII_UNC_ATTR  = 518 # Deprecated
IMPORT_ESRI_ASCII_GRID = 519 # Deprecated
IMPORT_EMODNET         = 520 # Deprecated
GENERATE_HULL          = 521
ADD_TRACKLINE_TO_IM    = 532 # Deprecated
IMPORT_PFM             = 533 # Deprecated
IMPORT_GML             = 537 # Deprecated
CM_PROCESSING          = 556
ACTIVATE_IM_IN_CM      = 558
CREATE_PFM             = 561 # Deprecated
EXPORT_EMODNET_GRID    = 564 # Deprecated
IMPORT_BAG             = 555 # Deprecated
EXPORT_EMODNET_GRID_CM = 565 # Deprecated
EXPORT_SDFILE_IM       = 571 
EXPORT_GEOTIFF_IM      = 572 # Deprecated
IMPIM_ESRIASCIIGRID    = 601 
IMPIM_DONAR            = 608 # Deprecated
IMPIM_ASCII            = 609
IMPIM_BAG              = 610
GENERATE_PRODUCTS      = 626
POSTPROCESS_IM         = 629
DEACTIVATE_IM_IN_CM    = 631
ADD_TRACKLINES_TO_IM   = 636
IMPIM_GML              = 637
IMPIM_METADATACSV      = 638
IMPIM_METADATAISOXML   = 639
IMPIM_SQL              = 685 # Deprecated
IMPIM_SD               = 700
SURFACE_DIFF_PROD      = 703
SEP_MODEL_FILE_IMP     = 707
SURFACE_DIFF_MODEL     = 710
EXPORT_EMODNET_CM      = 740
UPDATE_PERSONAL_LAYER  = 824

# Database process list
DB_PROCESS_DESC = { 272: "ExportAsciiIm"
                  , 485: "ArchiveIm"
                  , 486: "ArchiveTrackline"
                  , 517: "CreateBathyspaceAsciiNoAttr"
                  , 518: "CreateBathyspaceAsciiUncAttr"
                  , 519: "CreateBathyspaceEsriAsciiGrid"
                  , 520: "CreateBathyspaceEmodnet"
                  , 521: "GenerateHull"
                  , 532: "AddTracklineToIm"
                  , 533: "CreateBathyspacePfm"
                  , 537: "CreateBathyspaceGml"
                  , 555: "CreateBathyspaceBag"
                  , 556: "ProcessCm"
                  , 558: "ActivateImInCm"
                  , 561: "PfmCreator"
                  , 564: "ExportEMODNETGrid"
                  , 565: "ExportEMODNETGridCm"
                  , 571: "ExportSdFileIm"
                  , 572: "ExportGeotiffIm"
                  , 601: "ImpImESRIASCIIGRID"
                  , 608: "ImpImDONAR"
                  , 609: "ImpImASCII"
                  , 610: "ImpImBAG"
                  , 626: "GenerateProducts"
                  , 629: "PostprocessIm"
                  , 631: "DeactivateImInCm"
                  , 636: "AddTracklinesToIm"
                  , 637: "ImpImGML"
                  , 638: "ImpImMetadataCsv"
                  , 639: "ImpImMetadataIsoXml"
                  , 685: "ImpImSql"
                  , 700: "ImpImSd"
                  , 703: "SurfaceDiffModelProd"
                  , 707: "SepModelFileImp"
                  , 710: "SurfaceDifferenceModel"
                  , 740: "ExportEMODNETGridCm"
                  , 824: "updatePersonalLayer"
                  }

class BathyProcessObject :
    def __init__(self, ParameterList):

        try :

            # Initialize logger for process
            self.logger = logging.getLogger( BATHYTOOLS + '.' + BATHYPROCESSESLIB + '.' + DB_PROCESS_DESC [ int(ParameterList[ BathyToolsLib.PROCESSID ]) ] )
            self.logger.info ('Start ' + str(DB_PROCESS_DESC [ int(ParameterList[ BathyToolsLib.PROCESSID ]) ]) )

            # If importing data, you have to logon as SENS schema owner
            self.logger.info('Determine user to logon');
            if int(ParameterList[ BathyToolsLib.PROCESSID ]) == int(ARCHIVE_IM) or int(ParameterList[ BathyToolsLib.PROCESSID ]) == int( UPDATE_PERSONAL_LAYER ) or int(ParameterList[ BathyToolsLib.PROCESSID ]) == int(IMPIM_DONAR) or int(ParameterList[ BathyToolsLib.PROCESSID ]) == int(SEP_MODEL_FILE_IMP)  :
                dbuser     = BathyDbLib.SENS
                dbpassword = BathyDbLib.SENSPASSWORD
            else :
                # Establish database connection
                dbuser     = ParameterList [ BathyToolsLib.DBUSER ]
                dbpassword = ParameterList [ BathyToolsLib.DBPASSWORD ]

            # Build connection
            self.logger.info( "Log on as " + str(dbuser) )
            dbconnect  = ParameterList [ BathyToolsLib.DBCONNECT ]
            self.DbConnection = BathyDbLib.DbConnection ( dbuser, dbpassword, dbconnect, True, BATHYTOOLS )

            # Set parameter list
            self.ParameterList = ParameterList

        except Exception, err:
            print "Initializing bathy process failed:ERROR: %s\n" % str(err)
            raise

    def commit_close ( self ) :

        try :
            # Commit and close database connection
            self.logger.info("Commit and close database connection")
            try :
                self.DbConnection.commit_close()
            except Exception, err:
                 self.logger.info("Connection already closed")
        except Exception, err:
            self.logger.critical( "Commit and close database connection failed:ERROR: %s\n" % str(err) )
            raise

class updatePersonalLayer ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_task_id    = self.ParameterList[ BathyToolsLib.TASKID ]
            l_im_id      = self.ParameterList[ 'IM' ]
            l_temp_dir   = self.ParameterList[ BathyToolsLib.TEMPDIR ]
            l_sens_home_dir = str(BathyToolsLib.getenv_system('SENS_HOME'))
            self.logger.info ('Working directory is ' + str(l_temp_dir) )
            self.logger.info ('Home directory is ' + str(l_sens_home_dir) )
            
            # Get IM attributes
            self.logger.info ('Get IM Attributes from database')
            l_attributes = [ 'SYS050', 'SYS117',  'SYS119' ]
            l_values = self.DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attributes )
            l_xyz_file_name  = l_values[0]   
            l_user_id        = l_values[1] 
            l_cdi_record     = l_values[2]
            
            self.logger.info('Generate personal datm for user ' + str(l_user_id));
            
            
            # Get BLOB (SYS050) and write XYZ file
            self.logger.info ('Get xyz file as BLOB from database')
            l_xyz_file = BathyToolsLib.get_working_dir( self.logger, l_temp_dir ) + "\\" + str(l_xyz_file_name)
            self.DbConnection.get_blob ( BathyDbLib.IM_CLASS_ID, l_im_id, 'SYS050', l_xyz_file ) 
            
            # Generate hull (Makegrid) 
            self.logger.info ('Run Makegrid to generate hull')
            l_hull_file = BathyToolsLib.get_working_dir( self.logger, l_temp_dir ) + "\\hull.shp"
            BathyExecutablesLib.makegrid_generate_hull ( self.DbConnection, self.logger, l_xyz_file, l_hull_file ) 

            # Now extract the hull from the shapefile
            self.logger.info ('Extract hull from generated shapefile')
            l_hull_wkt = BathyExecutablesLib.ogr_extract_hull_from_shape ( self.logger, l_hull_file ) 
            
            # Don't forget to store the hull
            self.logger.info ('Store hull in database')
            self.DbConnection.store_hull ( BathyDbLib.IM_CLASS_ID, l_im_id, l_hull_wkt )             
            
            # Generate EMODNET grid from XYZ file (Makegrid)
            self.logger.info ('Generate EMODNET grid from XYZ file')
            l_emodnet_file = BathyToolsLib.get_working_dir( self.logger, l_temp_dir ) + "\\emodnet.grd"
            BathyExecutablesLib.makegrid_generate_emodnet_grid ( self.DbConnection, self.logger, l_xyz_file, l_emodnet_file, l_cdi_record ) 
            
            # Store EMODNET grid in database
            self.logger.info ('Store EMODNET grid in database')            
            nr_of_points = self.DbConnection.write_emodnet_points_to_db ( l_emodnet_file, 12, ';', l_im_id )  
            self.logger.info("Number of points in grid: " + str(nr_of_points)) 
            
            # Add IM to CM of user (sdb_continuous_model_pck.add_im_to_personal_cm)
            self.logger.info ('Add IM to personal CM')
            self.DbConnection.add_im_to_personal_cm ( l_im_id ) 
            
            # Generate EMODNET grid for whole CM (Python only)
            self.logger.info ('Read cookies for CM from database')
            l_cookie_list = self.DbConnection.get_personal_cookie_list ( l_user_id ) 
            self.logger.info(str(len(l_cookie_list)) + ' surveys in personal DTM')
            
            # Generate xyz source file for products
            self.logger.info ('Generate xyz source file for products')
            l_product_source_file = BathyToolsLib.get_working_dir( self.logger, l_temp_dir ) + "\\" + str(l_user_id) + ".xyz"
            #l_product_source_file = "C:/SENSData/Temp" + "\\" + str(l_user_id) + ".xyz"
            fOut = open ( l_product_source_file, 'w')
            for l_cookie_id in l_cookie_list :
                l_nr = self.DbConnection.write_depths_to_product_source_file ( l_cookie_id, fOut ) 
                self.logger.info (str(l_nr) + ' points written to file')
            fOut.close()
            
            # Generate Geotiff (Makegrid)
            self.logger.info ('Generate Personal GeoTIFF')
            l_geotif_file = BathyToolsLib.get_working_dir( self.logger, l_temp_dir ) + "\\" + str(l_user_id) + ".tif"
            #l_geotif_file = "C:/SENSData/Temp" + "\\" + str(l_user_id) + ".tif"
            l_colour_file =  l_sens_home_dir + '/colorsinterp.cmap'
            BathyExecutablesLib.makegrid_generate_geotif ( self.DbConnection, self.logger, l_product_source_file, l_geotif_file, l_colour_file ) 
            
            # Generate Esri Ascii Grid (Makegrid)
            self.logger.info ('Generate Personal Esri Ascii Grid')
            l_esri_ascii_file = BathyToolsLib.get_working_dir( self.logger, l_temp_dir ) + "\\" + str(l_user_id) + ".asc"
            #l_esri_ascii_file = "C:/SENSData/Temp" + "\\" + str(l_user_id) + ".asc"
            BathyExecutablesLib.makegrid_generate_esri_ascii_grid ( self.DbConnection, self.logger, l_product_source_file, l_esri_ascii_file )             

            # Upload personal DTM
            self.logger.info ('Upload personal geotif file')
            BathyToolsLib.upload_personal_dtm (  self.logger, l_user_id, "tif", l_geotif_file ) 
            self.logger.info ('Upload personal esri ascii grid file')
            BathyToolsLib.upload_personal_dtm (  self.logger, l_user_id, "asc", l_esri_ascii_file )             
            
            # Publish Geotif on personal layer for user
            self.logger.info ('Publish Personal DTM on Geoserver')
            BathyToolsLib.upload_to_geoserver (  self.logger, l_user_id, l_geotif_file ) 

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ArchiveIm ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_task_id    = self.ParameterList[ BathyToolsLib.TASKID ]
            l_im_id      = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]

            # Get datafile to import from database
            l_attributes   = [ BathyDbLib.IM_PROC_DATA_FILE_COL, BathyDbLib.IM_IM_FORMAT_DB ]
            l_values       = self.DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attributes )
            l_data_file    = l_values[0]
            l_im_format_id = l_values[1]

            # Check if directory exists
            l_bathyspace_dir    = os.path.dirname(l_data_file)
            if not os.path.isdir( l_bathyspace_dir ) :
                self.logger.critical( "Bathyspace directory is NOT on this client")
                sys.exit("Execution stopped")

            # Import IM into database
            self.logger.info ( 'Write IM into database' )
            BathyToolsLib.write_depths_to_database  ( self.DbConnection, self.logger, l_data_file, l_im_format_id )

            # Import IM into database
            self.logger.info ( 'Create spatial index on database' )
            BathyToolsLib.create_spatial_index_on_database ( self.DbConnection, self.logger, BathyDbLib.IM_CLASS_ID, l_im_id, l_task_id  )

            # Update workflowstep
            self.DbConnection.update_workflow_step ( self.ParameterList[ BathyToolsLib.PARAMETER_PROCESS_ID ], BathyDbLib.IM_CLASS_ID, l_im_id )

            # Bathyspace is dropped and set file refernce to bathyspace to NULL
            if str(self.ParameterList[ "DropBathyspaceFiles" ]) == "T" :
                l_bathyspace_dir = os.path.dirname( l_data_file )
                BathyToolsLib.drop_bathyspace_dir ( self.logger, l_bathyspace_dir ) 
                l_attribute_list = {}
                l_attribute_list [ BathyDbLib.IM_PROC_DATA_FILE_COL ] = ''
                l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = ''
                self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ArchiveTrackline ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :
        
        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_task_id               = self.ParameterList[ BathyToolsLib.TASKID ]
            l_im_id                 = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_input_file            = self.ParameterList[ BathyToolsLib.PARAMETER_INPUT_FILE ]
            l_coord_sys_id          = self.ParameterList[ BathyToolsLib.PARAMETER_COORD_SYS ]
            l_etrsyear              = self.ParameterList[ BathyToolsLib.PARAMETER_ETRSYEAR ]
            l_vert_ref_id           = self.ParameterList[ BathyToolsLib.PARAMETER_VERT_REF ] 
            l_ascii_imp_id          = self.ParameterList[ BathyToolsLib.PARAMETER_ASCII_IMP ]
            l_startdate             = self.ParameterList[ BathyToolsLib.PARAMETER_STARTDATE ]
            l_enddate               = self.ParameterList[ BathyToolsLib.PARAMETER_ENDDATE ]

            # Create bathyspace directory
            l_bathyspace_dir   = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )
            l_bathyspace_file = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII

            # Write trackline attributes to database
            self.logger.info ( 'Write trackline attributes to database')
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.TL_EPSG_ID_IN ]       = l_coord_sys_id
            l_attribute_list [ BathyDbLib.TL_DATA_FILE_COL ]    = l_input_file
            l_attribute_list [ BathyDbLib.TL_SEP_MODEL_COL ]    = l_vert_ref_id
            l_attribute_list [ BathyDbLib.TL_ETRSYEAR_COL ]     = l_etrsyear
            l_attribute_list [ BathyDbLib.TL_STARTDATE_COL ]    = l_startdate
            l_attribute_list [ BathyDbLib.TL_ENDDATE_COL ]      = l_enddate
            l_attribute_list [ BathyDbLib.TL_INPUT_FORMAT_COL ] = self.ParameterList[ BathyToolsLib.PARAMETER_FILE_FORMAT ]
            l_attribute_list [ BathyDbLib.TL_FORMAT ]           = self.ParameterList[ BathyToolsLib.PARAMETER_TL_FORMAT ]
            l_attribute_list [ BathyDbLib.TL_TYPE ]             = self.ParameterList[ BathyToolsLib.PARAMETER_TL_TYPE ]
            l_attribute_list [ BathyDbLib.TL_VERDAT_SOURCE_COL ]= self.ParameterList[ BathyToolsLib.PARAMETER_VERDAT_SOURCE ]
            self.DbConnection.set_obj_attributes ( BathyDbLib.TL_CLASS_ID, l_im_id, l_attribute_list )

            # First update the workflowstep to status Archived, when inserting geometry correct business rules are executed
            self.logger.info ( 'Update workflowstep using process id ' + str(self.ParameterList[ BathyToolsLib.PARAMETER_PROCESS_ID ]) )
            self.DbConnection.update_workflow_step ( self.ParameterList[ BathyToolsLib.PARAMETER_PROCESS_ID ], BathyDbLib.TL_CLASS_ID, l_im_id )

            # Apply ascii importer
            self.logger.info ( 'Apply Ascii importer' )
            BathyExecutablesLib.sens_ascii_importer ( self.DbConnection, self.logger, self.ParameterList, l_bathyspace_file )
            l_coord_sys_class_id = BathyToolsLib.get_coord_sys_class ( self.DbConnection, self.logger, self.ParameterList[ BathyToolsLib.PARAMETER_COORD_SYS ] )
            self.logger.info ("Coordinate system class is " + str(l_coord_sys_class_id) )
            BathyToolsLib.gen_bathyspace_files ( self.logger, l_bathyspace_file, l_im_id, l_coord_sys_class_id )

            # Extract and store boundaries
            self.logger.info ( 'Store Bathyspace dimensions' )
            BathyToolsLib.store_bathyspace_dimensions ( self.logger, self.DbConnection, BathyDbLib.TL_CLASS_ID, l_bathyspace_dir, l_im_id, l_coord_sys_class_id )

            # Get parameters for Makegrid
            self.logger.info ( 'Get geodetic parameters for conversion' )
            l_epsg_code_in              = BathyToolsLib.get_epsg_code ( self.DbConnection, self.logger, l_coord_sys_id )
            l_wkt_in                    = self.DbConnection.get_wkt_coord_sys_id ( l_coord_sys_id )
            l_epsg_code_out             = self.DbConnection.get_epsg_code_db ()
            l_wkt_out                   = self.DbConnection.get_wkt_epsg_code ( l_epsg_code_out )
            l_ver_dat_in, l_ver_dat_out, l_offset, l_m_factor = BathyToolsLib.get_separation_model ( self.DbConnection, self.logger, l_vert_ref_id )

            # Run Makegrid for geodetic transformations
            self.logger.info ( 'Apply coordinate transformation and apply separation model' )
            l_sep_model_name, l_direction, l_gridsize, l_algorithm_id = BathyExecutablesLib.makegrid_separation_model_file ( self.DbConnection, self.logger, l_bathyspace_dir, l_vert_ref_id, None, None )
            l_input_file                                              = os.path.basename( l_bathyspace_file )
            l_output_file                                             = BathyExecutablesLib.makegrid_geo_conv ( self.logger, l_input_file, l_bathyspace_dir, l_epsg_code_in, l_epsg_code_out, l_ver_dat_in, l_ver_dat_out, l_offset, l_m_factor, l_etrsyear, ";", ";", l_wkt_in, l_wkt_out, l_sep_model_name, l_direction, l_gridsize, l_algorithm_id )
            self.logger.info ('File to import into database: ' + str(l_output_file) )

            # Get IM format for nodal mapping from ascii importer
            l_attributes = [ BathyDbLib.IM_FORMAT_COL ]
            l_values = self.DbConnection.get_obj_attributes ( BathyDbLib.ASCII_IMPORTER_CLASS_ID, l_ascii_imp_id, l_attributes )
            l_im_format_id  = l_values[0]

            # Import trackline into database
            self.logger.info ( 'Write trackline into database' )
            BathyToolsLib.write_depths_to_database  ( self.DbConnection, self.logger, l_output_file, l_im_format_id )

            # Import trackline into database
            self.logger.info ( 'Create spatial index on database' )
            BathyToolsLib.create_spatial_index_on_database ( self.DbConnection, self.logger, BathyDbLib.TL_CLASS_ID, l_im_id, l_task_id  )

            # Write trackline attributes to database
            self.logger.info ( 'Update trackline format attribute in database')
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.TL_IM_FORMAT ]        = l_im_format_id
            self.DbConnection.set_obj_attributes ( BathyDbLib.TL_CLASS_ID, l_im_id, l_attribute_list )

            # Bathyspace is dropped
            BathyToolsLib.drop_bathyspace_dir ( self.logger, l_bathyspace_dir )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class PfmCreator ( BathyProcessObject ):
    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )
        
    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )
            
            # Get coordinate system description from database
            l_epsg_id_db = self.ParameterList[ "CoordinateSystemId" ]
            l_attributes = [ BathyDbLib.EPSG_CMDOP_COL ]
            l_values = self.DbConnection.get_obj_attributes ( BathyDbLib.EPSG_CLASS_ID, l_epsg_id_db, l_attributes )
            l_icoordsys = l_values[0]
            self.logger.info ('Coordinate system PFM is ' + str(l_icoordsys))

            # Get temporary directory to create project directory in
            l_project_directory = BathyToolsLib.get_working_dir( self.logger, self.ParameterList [ BathyToolsLib.TEMPDIR ] ) + "\\" + self.ParameterList[ "ProjectName" ]
            
            # Run cmdop create project
            BathyExecutablesLib.cmdop_projectcreate ( self.DbConnection, self.logger, l_project_directory, l_icoordsys  )

            # Add parameters for cmdop create add file to project
            l_input_file = self.ParameterList[ "InputFile" ]

            # Run cmdop to add file to project
            BathyExecutablesLib.cmdop_projectaddsource ( self.DbConnection, self.logger, l_project_directory, l_input_file, l_icoordsys  )

            # Update IM attributes in database
            l_im_id = self.ParameterList[ "SurveyId" ]
            attribute_list = {}
            attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ] = BathyDbLib.BATHYSPACE_PFM
            attribute_list [ BathyDbLib.IM_SOURCE_FILES_COL ] = l_input_file
            attribute_list [ BathyDbLib.IM_DMAGIC_PROJ_COL ]  = l_project_directory
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, attribute_list )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ExportEMODNETGrid ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_im_id    = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_file_out = self.ParameterList[ BathyToolsLib.OUTPUTDIRECTORY ] + "\\" + self.ParameterList[ BathyToolsLib.OUTPUTFILE ] + BathyExecutablesLib.FILE_EXT_ASCII

            # Lock IM
            self.DbConnection.lock_survey( BathyDbLib.IM_CLASS_ID, l_im_id)

            # Open file and write depths to file
            fOut = open(l_file_out, 'w')
            self.DbConnection.write_depths_to_emodnet_grid ( fOut, l_im_id, None, None )
            fOut.close()

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ExportEMODNETGridCm ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_cm_id        = self.ParameterList[ BathyToolsLib.PARAMETER_CM_ID ]
            l_product_area = self.ParameterList[ BathyToolsLib.PARAMETER_PRODUCT_AREA ]
            l_file_out     = self.ParameterList[ BathyToolsLib.OUTPUTDIRECTORY ] + "\\" + self.ParameterList[ BathyToolsLib.OUTPUTFILE ] + BathyExecutablesLib.FILE_EXT_ASCII

            # Lock CM
            self.DbConnection.lock_survey( BathyDbLib.CM_CLASS_ID, l_cm_id)

            # Get cookie list
            l_cookie_list = self.DbConnection.get_cookie_list ( l_cm_id, l_product_area )

            # Open file
            fOut = open(l_file_out, 'w')

            # Loop trough cookie list, select depths within cookie and write to file
            for l_cookie_id in l_cookie_list :
                self.logger.info ("Process IM segment " + str(l_cookie_id) )
                self.DbConnection.write_depths_to_emodnet_grid ( fOut, None, l_cookie_id, l_product_area )

            # Close file
            fOut.close()

            # Convert to NetCDF
            if str(self.ParameterList[ BathyToolsLib.PARAMETER_TO_NETCDF ]) == "T" :
                self.logger.info ("Conver to NetCDF " )
                (l_filepath, l_filename) = os.path.split(l_file_out)
                l_shortname              = os.path.splitext(l_filename)[0]
                l_netcdf_file            = l_filepath + "\\" + l_shortname + BathyExecutablesLib.FILE_EXT_NC
                l_gridsize               = BathyExecutablesLib.EMODNET_GRIDSIZE
                BathyExecutablesLib.netcdf_generate_emodnet_grid ( self.logger, l_file_out, l_netcdf_file, l_gridsize, self.ParameterList )
                os.remove(l_file_out)

            # Zip the outputfile
            l_output_file = self.ParameterList[ BathyToolsLib.OUTPUTDIRECTORY ] + "\\" + self.ParameterList[ BathyToolsLib.OUTPUTFILE ]
            BathyToolsLib.zip_files ( self.logger, l_output_file )
            
        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ExportAsciiIm ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_im_id            = self.ParameterList[ BathyToolsLib.PARAMETER_SURVEY_ID ]
            l_ascii_file       = self.ParameterList[ BathyToolsLib.OUTPUTDIRECTORY ] + "\\" + self.ParameterList[ BathyToolsLib.OUTPUTFILE ] 
            l_ascii_format_id  = self.ParameterList[ "AsciiExportFormat" ]
            l_points_in_hull   = self.ParameterList[ "OnlyPointsWithinHull" ]
            l_include_attr     = self.ParameterList[ "IncludeAttributes" ]
            l_depth_positive   = self.ParameterList[ "DepthPositive" ]

            # Check outputfile for extension, if not add extension
            if int(l_ascii_format_id) == int(BathyDbLib.FORMAT_XYZ_GML) or int(l_ascii_format_id) == int(BathyDbLib.FORMAT_YXZ_GML) :
                # Remove extension from file from parameter list
                l_ascii_file, l_file_ext = os.path.splitext( l_ascii_file )
                l_file_ext = BathyExecutablesLib.FILE_EXT_GML
            else :
                l_file_ext = self.ParameterList[ BathyToolsLib.PARAMETER_FILE_MASK ]
            l_ascii_file = BathyToolsLib.add_file_ext ( l_ascii_file, l_file_ext )
            self.logger.info ( 'Outputfile is ' + str(l_ascii_file) )

            # Get IM format
            l_attributes   = [ BathyDbLib.IM_IM_FORMAT_DB ]
            l_values       = self.DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attributes )
            l_im_format_id = l_values[0]

            # Start writing data
            self.logger.info ("Start writing depth to file " + str(l_ascii_file) + " using IM format " + str(l_im_format_id) )
            nr = self.DbConnection.write_IM_depths_to_file ( l_ascii_file, l_im_id, l_im_format_id, l_ascii_format_id, l_points_in_hull, l_include_attr, l_depth_positive )

            # Write IM metadata to file
            l_output_file, l_file_ext = os.path.splitext( l_ascii_file )
            l_file_ext    = BathyExecutablesLib.FILE_EXT_META
            l_output_file = l_output_file + "_im_" + str(l_im_id) + l_file_ext
            BathyToolsLib.write_metadata_file ( self.DbConnection, self.logger, l_output_file, BathyDbLib.IM_CLASS_ID, l_im_id )
            
            # Zip all files 
            l_output_file, l_file_ext = os.path.splitext( l_ascii_file )
            BathyToolsLib.zip_files ( self.logger, l_output_file )

            self.logger.info ("Generation " + str(l_ascii_file) + " completed")
            self.logger.info (str(nr) + " points written to file")

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ExportSdFileIm ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_im_id      = self.ParameterList[ BathyToolsLib.PARAMETER_SURVEY_ID ]
            l_sd_file    = self.ParameterList[ BathyToolsLib.OUTPUTDIRECTORY ] + "\\" + self.ParameterList[ BathyToolsLib.OUTPUTFILE ] 

            # Check outputfile for extension, if not add extension
            l_sd_file = BathyToolsLib.add_file_ext ( l_sd_file, self.ParameterList[ BathyToolsLib.PARAMETER_FILE_MASK ] )
            self.logger.info ( 'Outputfile is ' + str(l_sd_file) )

            # Get SD file as binary from database
            self.DbConnection.get_blob ( BathyDbLib.IM_CLASS_ID, l_im_id, BathyDbLib.IM_SDBLOB_COL, l_sd_file )

            self.logger.info ("Generation " + str(l_sd_file) + " completed")

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ExportGeotiffIm ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )
            self.logger.info ("To be implemented")
        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise


class GenerateHull ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_im_id         = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_link_distance = self.ParameterList[ "LinkDistance" ]

            # Get survey type and bathyspace attributes
            l_attributes = [ BathyDbLib.IM_SURVEYTYPE_COL,  BathyDbLib.IM_BATHYSP_FILE_COL,  BathyDbLib.IM_BATHYSP_TYPE_COL,  BathyDbLib.IM_SDFILE_NAME_COL,  BathyDbLib.IM_COORD_SYS_SRC_COL, BathyDbLib.IM_INPUT_FORMAT_COL, BathyDbLib.IM_ETRSYEAR_COL ]
            l_values = self.DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attributes )
            l_survey_type        = l_values[0]
            l_bathyspace_file    = l_values[1]
            l_bathyspace_type_id = l_values[2]
            l_sd_file            = l_values[3]
            l_coord_sys_id       = l_values[4]
            l_inputfile_format   = l_values[5]
            l_etrs_year          = l_values[6]

            # Get Bathyspace directory from bathyspace file
            l_bathyspace_dir    = os.path.dirname(l_bathyspace_file)

            # Check if directory exists
            if not os.path.isdir( l_bathyspace_dir ) :
                self.logger.critical( "Bathyspace directory is NOT on this client")
                os.sys.exit("Execution stopped")

            # Get epsg_code
            l_epsg_code          = BathyToolsLib.get_epsg_code ( self.DbConnection, self.logger, l_coord_sys_id )
            l_wkt_in             = self.DbConnection.get_wkt_coord_sys_id ( l_coord_sys_id )
            l_epsg_code_out      = self.DbConnection.get_epsg_code_db ()
            l_wkt_out            = self.DbConnection.get_wkt_epsg_code ( l_epsg_code_out )
            l_coord_sys_class_id = BathyToolsLib.get_coord_sys_class ( self.DbConnection, self.logger, l_coord_sys_id )

            # For backwards compatibility, generate bathyspace files when boundary file is NOT correct
            if not BathyToolsLib.bounds_file_up_to_date ( self.logger, l_bathyspace_file, l_im_id ) :
                self.logger.info("Regenerate SENS version 1.3 bathyspace")
                BathyToolsLib.gen_bathyspace_files ( self.logger, l_bathyspace_file, l_im_id, l_coord_sys_class_id )

            # Check link distance
            l_min_link_distance, l_max_link_distance = BathyToolsLib.get_link_distance_limits ( self.DbConnection, self.logger, l_im_id, l_coord_sys_id, l_coord_sys_class_id, l_bathyspace_file)

            if int(l_min_link_distance) > int(l_max_link_distance) :
                # You have too little points so use max link distance to calculate limits
                l_min_link_distance = int ( 0.9 * float(l_max_link_distance) )
                l_max_link_distance = int ( 1.1 * float(l_max_link_distance) )

            # Check if link distance is between boundary values
            if int(l_link_distance) > int (l_min_link_distance) and  int(l_link_distance) < int(l_max_link_distance) :
                self.logger.info ( "Link distance is between boundaries " + str(l_min_link_distance) + " and " + str(l_max_link_distance) )
                self.logger.info ( "Link distance correct" )
            else :
                self.logger.warning ( "Link distance is NOT between estimated boundaries " + str(l_min_link_distance) + " and " + str(l_max_link_distance) )

            # Temporary files for hull generation
            l_edges_file_tmp     = l_bathyspace_dir + "\\" + "edges_" + l_im_id + BathyExecutablesLib.FILE_EXT_ASCII

            # Set boolean to continue
            l_continue  = True
            l_cell_size = None

            # For ASCII bathyspace, generate first SD file to generate hull on
            if int(l_bathyspace_type_id) == int(BathyDbLib.BATHYSPACE_ASCII) :

                # Generate SD file for Ascci files
                self.logger.info ("Generate SD file for Ascii file and check coordinate system")

                # cmdop gridder runs only on xyz file, so extract xyz file from bathyspace ascii
                l_ascii_file_tmp    = BathyToolsLib.get_temp_file_name ( self.logger, l_bathyspace_dir, l_im_id )
                
                # Extract boundaries and create tmp file for hull generation
                l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax = BathyToolsLib.get_bathyspace_dimensions ( self.logger, l_bathyspace_dir, l_im_id )
                l_y         = float(l_ymin) + ( ( float(l_ymax) - float(l_ymin) ) / float(2.0) )
                l_cell_size = BathyToolsLib.convert_cell_size ( self.logger, l_coord_sys_class_id, l_link_distance, l_y )

                # Check coordinate system
                coordinate_system_correct = BathyToolsLib.coordinate_system_correct ( self.logger, l_ascii_file_tmp, l_epsg_code, l_coord_sys_class_id )

                # Generate SD file is coordinate system is correct
                if coordinate_system_correct :

                    # For Esri ascii grids, an SD file already exists
                    #if str(l_inputfile_format) <> str(BathyDbLib.IMP_FORMAT_ESRIASCIIGRID) :

                    self.logger.info ("Generate SD file")
                    l_sd_file   = l_bathyspace_dir + "\\" + "tmp_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
                    BathyExecutablesLib.cmdop_gridder ( self.DbConnection, self.logger, l_ascii_file_tmp, l_sd_file, l_epsg_code, l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax, l_cell_size)
                    l_sd_file_to_store = l_sd_file

                    # If visualisation file has to be generated
                    if str( self.ParameterList[ BathyToolsLib.PARAMETER_VIS_TF ] ) == "T" :
                        self.logger.info ("Generate SD file for visualization")
                        l_sd_file_vis   = l_bathyspace_dir + "\\" + "tmp_vis_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
                        l_cell_size_vis = BathyToolsLib.convert_cell_size ( self.logger, l_coord_sys_class_id, self.ParameterList[ BathyToolsLib.PARAMETER_VIS_GRIDSIZE ] , l_y )
                        self.logger.info ("Use cellsize " + str(l_cell_size_vis) )
                        BathyExecutablesLib.cmdop_gridder ( self.DbConnection, self.logger, l_ascii_file_tmp, l_sd_file_vis, l_epsg_code, l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax, l_cell_size_vis)
                        l_sd_file_to_store = l_sd_file_vis

                    # Store location of temporary SD file and BLOB in database (IM_SDFILE_NAME_COL)
                    self.logger.info ("Storing SD file in DB")
                    l_blob_file_name = "BLOB" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
                    l_attribute_list = {}
                    l_attribute_list [  BathyDbLib.IM_SDFILE_NAME_COL ]    = l_sd_file_to_store
                    self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )
                    self.DbConnection.set_blob ( BathyDbLib.IM_CLASS_ID, l_im_id, BathyDbLib.IM_SDBLOB_COL, l_sd_file_to_store, l_blob_file_name )

                else :
                    self.logger.critical("Coordinate system survey does not match coordinates in file")
                    os.sys.exit("Execution stopped")

            # Now for each survey you have an SD file or an PFM file
            if l_continue :

                # Get minimum gap area
                if not l_cell_size :
                    l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax = BathyToolsLib.get_bathyspace_dimensions ( self.logger, l_bathyspace_dir, l_im_id )
                    l_y         = ( float(l_ymax) - float(l_ymin) ) / float(2.0)
                    l_cell_size = BathyToolsLib.convert_cell_size ( self.logger, l_coord_sys_class_id, l_link_distance, l_y )
                l_gap_radius   = ( float(l_cell_size) / 2.0 )
                #l_min_gap_area = BathyToolsLib.get_minimum_gap_area ( self.logger, l_cell_size )

                # Now generate hull: for single beam use cgal else use cmdop
                if int(l_survey_type) == int(BathyDbLib.SINGLEBEAM_SURVEYTYPE_ID) or int(l_survey_type) == int(BathyDbLib.TRACKLINE_SURVEYTYPE_ID) :
                    self.logger.info ("Generate hull for singlebeam or trackline survey")
                    # Start hull generation
                    l_hull_edges = BathyExecutablesLib.cgal_generate_hull_edges ( self.DbConnection, self.logger, l_ascii_file_tmp, l_gap_radius )
                    # Check if list contains edges
                    if l_hull_edges :
                        # Coordinate conversion
                        self.logger.info ("Coordinate conversion hull")
                        l_hull_edges_conv = []
                        BathyExecutablesLib.cgal_coordinate_conversion_edges ( self.logger, l_hull_edges, l_edges_file_tmp, l_epsg_code, l_epsg_code_out, l_etrs_year, l_wkt_in, l_wkt_out, l_hull_edges_conv )
                        # Store hull in database
                        self.logger.info ("Store hull in database")
                        self.DbConnection.insert_edges ( l_hull_edges_conv )
                        self.DbConnection.generate_hull_from_edges ( BathyDbLib.IM_CLASS_ID, l_im_id, l_link_distance )
                    else :
                        self.logger.critical ("Hull could not be generated")
                        os.sys.exit("Execution stopped")
                else :
                    self.logger.info ("Generate hull for gridded survey")
                    # Determine if file to generate hull on is SD or PFM file
                    if int(l_bathyspace_type_id) == int(BathyDbLib.BATHYSPACE_PFM) :
                        l_option = '-pfm'
                        l_bathyspace_file_hull = l_bathyspace_file
                    if int(l_bathyspace_type_id) == int(BathyDbLib.BATHYSPACE_SD) :
                        l_option = '-dtm'
                        l_bathyspace_file_hull = l_sd_file
                    if int(l_bathyspace_type_id) == int(BathyDbLib.BATHYSPACE_BAG) :
                        l_option = '-dtm'
                        l_bathyspace_file_hull = l_sd_file
                    if int(l_bathyspace_type_id) == int(BathyDbLib.BATHYSPACE_ASCII) :
                        l_option = '-dtm'
                        l_bathyspace_file_hull = l_sd_file
                    # Now start hull generation based on SD file
                    l_hull_file_tmp      = l_bathyspace_dir + "\\" + "hull_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_TMP
                    l_hull_file_tmp_conv = l_bathyspace_dir + "\\" + "hull_conv_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_TMP
                    BathyExecutablesLib.cmdop_createcoveragevectors ( self.DbConnection, self.logger, l_option, l_bathyspace_file_hull, l_hull_file_tmp )
                    # Check if fgenerated file contains coordinates
                    if os.path.getsize( l_hull_file_tmp ) :
                        # Coordinate conversion
                        self.logger.info ("Coordinate conversion hull")
                        BathyExecutablesLib.cmdop_coordinate_conversion_hull ( self.logger, l_hull_file_tmp, l_edges_file_tmp, l_epsg_code, l_epsg_code_out, l_etrs_year, l_wkt_in, l_wkt_out, l_hull_file_tmp_conv )
                        # Recalculate gap area based on geographic coordinate system
                        #l_cell_size    = BathyToolsLib.convert_cell_size ( self.logger, BathyDbLib.GEOGRAPHIC, l_link_distance, 0 )
                        #l_min_gap_area = BathyToolsLib.get_minimum_gap_area ( self.logger, l_cell_size )
                        # Finally convert hull to wkt, remove holes larger than min_gap_area and store hull in database
                        self.logger.info ("Store hull in database")
                        l_hull = BathyExecutablesLib.ogr_convert_hull_to_wkt ( self.DbConnection, self.logger, l_hull_file_tmp_conv )
                        self.DbConnection.insert_im_hull ( BathyDbLib.IM_CLASS_ID, l_im_id, l_hull, l_epsg_code_out, l_link_distance )
                    else :
                        self.logger.critical ("Hull could not be generated")
                        os.sys.exit("Execution stopped")

                # Update workflowstep
                self.DbConnection.update_workflow_step ( self.ParameterList[ BathyToolsLib.PARAMETER_PROCESS_ID ], BathyDbLib.IM_CLASS_ID, l_im_id )

                # Dump hull to shapefile in bathyspace directory
                l_shape_file = l_bathyspace_dir + "\\" + "hull_" + l_im_id + BathyExecutablesLib.FILE_EXT_SHP
                l_hull_wkt = self.DbConnection.get_geom ( BathyDbLib.IM_CLASS_ID, l_im_id, BathyDbLib.IM_HULL_COL )
                BathyExecutablesLib.ogr_dump_hull_to_shape ( self.logger, l_im_id, l_epsg_code_out, l_shape_file, l_hull_wkt )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            os.sys.exit("Execution stopped")

class CreateBathyspaceEsriAsciiGrid ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Set bathyspace type
            l_bathyspace_type = BathyDbLib.BATHYSPACE_SD

            # Get parameters from list
            l_im_id                 = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_file_format           = self.ParameterList[ "FileFormat" ]
            l_input_file            = self.ParameterList[ "FileIn" ]
            l_epsg_id               = self.ParameterList[ "EpsgIn" ]
            l_multiplication_factor = self.ParameterList[ "MultiplicationFactor" ]
            l_verdat_in_id          = self.ParameterList[ "VerdatIn" ]

            # Get coordinate description for IM
            l_icoordsys, l_epsg_code = BathyToolsLib.get_coordinate_desc ( self.DbConnection, self.logger, l_epsg_id )

            # Create bathyspace directory
            l_bathyspace_dir = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )
            
            # Extract boundaries and write to bounds file (necessary for later hull generation)
            l_cell_size, l_no_data_value = BathyToolsLib.write_metadata_from_esri_ascii_grid ( self.logger, l_input_file, l_bathyspace_dir, l_im_id  )

            # Now convert ascii grid to sd file
            l_sdfile_out = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
            BathyExecutablesLib.cmdop_gasciitoscalar ( self.DbConnection, self.logger, l_input_file, l_sdfile_out, l_icoordsys, l_no_data_value )

            # Now convert sd file to ascii xyz file
            l_bathyspace_file = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII
            BathyExecutablesLib.cmdop_exportsurface ( self.DbConnection, self.logger, l_sdfile_out, l_bathyspace_file )

            # Store Bathyspace attributes in database
            self.logger.info("Store bathyspace parameters in database")
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_GRID_CELL_SIZE_COL ] = l_cell_size
            l_attribute_list [ BathyDbLib.IM_SOURCE_FILES_COL ]   = l_input_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = l_bathyspace_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = l_bathyspace_type
            l_attribute_list [ BathyDbLib.IM_INPUT_FORMAT_COL ]   = l_file_format
            l_attribute_list [ BathyDbLib.IM_SDFILE_NAME_COL ]    = l_sdfile_out
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class CreateBathyspaceAsciiNoAttr ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Set bathyspace type
            l_bathyspace_type = BathyDbLib.BATHYSPACE_ASCII

            # Get parameters from list
            l_im_id                 = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_input_file            = self.ParameterList[ "FileIn" ]
            l_file_format           = self.ParameterList[ "FileFormat" ]
            l_epsg_id               = self.ParameterList[ "EpsgIn" ]
            l_multiplication_factor = self.ParameterList[ "MultiplicationFactor" ]
            l_verdat_in_id          = self.ParameterList[ "VerdatIn" ]
            l_attribute_order_id    = self.ParameterList[ "AttributeOrder" ]
            l_separator_id          = self.ParameterList[ "Separator" ]

            # Get separtor from database
            l_attributes = [ BathyDbLib.SEPARATOR_COL ]
            l_values = self.DbConnection.get_obj_attributes ( BathyDbLib.SEPARATOR_CLASS_ID, l_separator_id, l_attributes )
            l_separator = l_values[0]
            self.logger.info("Separator is " + str(l_separator) )

            # Create bathyspace directory
            l_bathyspace_dir  = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )
            l_bathyspace_file = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII

            # Ungridded ascii files are translated into ascii bathyspace format:
            # x <space> y <space> z <space> attr1 <space> attr2 <space> etc.
            # New file is copied to temporary bathyspace directory
            self.logger.info("Translate file into ascii bathyspace format")
            fIn = open( l_input_file,'r' )
            l_check_line = fIn.readline()
            self.logger.info("ASCII file format: " + str(l_check_line))
            fIn.close()

            # Determine nr of attributes
            l_nr_attr = len(l_check_line.rstrip().split( l_separator ))

            # Convert file to bathyspace if file format is correct
            if l_nr_attr >= 3 :
                fIn = open( l_input_file,'r' )
                fOut = open( l_bathyspace_file, 'w' )
                i = 0
                for l_line in fIn:
                    l_output_line = BathyToolsLib.process_imp_ascii_no_attr_line ( self.logger, l_line, l_attribute_order_id, l_separator, l_separator_id, float(l_multiplication_factor) )
                    if l_output_line :
                        fOut.write ( l_output_line )
                        i = i + 1
                        if i % BathyDbLib.NR_OF_ROWS_PER_INSERT == 0 :
                            self.logger.info( str(i) + " points processed" )
                
                # Log total number of points imported and close files
                self.logger.info ( str(i) + " points written to bathyspace " + l_bathyspace_file )
                fIn.close()
                fOut.close()
            else :
                self.logger.critical("Wrong file format; Bathyspace can not be created")
                raise

            # Store Bathyspace attributes in database
            self.logger.info("Store bathyspace parameters in database")
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_SOURCE_FILES_COL ]   = l_input_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = l_bathyspace_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = l_bathyspace_type
            l_attribute_list [ BathyDbLib.IM_INPUT_FORMAT_COL ]   = l_file_format
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class CreateBathyspaceBag ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Set bathyspace type
            l_bathyspace_type = BathyDbLib.BATHYSPACE_BAG

            # Get parameters from list
            l_im_id          = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_input_file     = self.ParameterList[ "FileIn" ]
            l_file_format    = self.ParameterList[ "FileFormat" ]
            l_epsg_id        = self.ParameterList[ "EpsgIn" ]
            l_verdat_in_id   = self.ParameterList[ "VerdatIn" ]

            # Create bathyspace directory
            l_bathyspace_dir   = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )
            l_sdfile_out       = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
            l_asciifile_out    = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII
            l_metadata_xml_out = l_asciifile_out + ".xml"

            # Convert BAG to SD file
            BathyExecutablesLib.cmdop_bagtoscalar ( self.logger, l_input_file, l_sdfile_out )

            # Convert BAG to ASCII file and extract metadata XML
            BathyExecutablesLib.cmdop_bagtoascii ( self.logger, l_input_file, l_asciifile_out )

            # Extract metadata from BAG metadata XML
            l_epsg_id, l_verdat_in_id = BathyToolsLib.extract_metadata_from_bag ( self.DbConnection, self.logger, l_metadata_xml_out, l_epsg_id, l_verdat_in_id )

            # Store Bathyspace attributes in database
            self.logger.info("Store bathyspace parameters in database")
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_SOURCE_FILES_COL ]   = l_input_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = l_asciifile_out
            l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = l_bathyspace_type
            l_attribute_list [ BathyDbLib.IM_INPUT_FORMAT_COL ]   = l_file_format
            l_attribute_list [ BathyDbLib.IM_SDFILE_NAME_COL ]    = l_sdfile_out
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class CreateBathyspaceAsciiUncAttr ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Set bathyspace type
            l_bathyspace_type = BathyDbLib.BATHYSPACE_ASCII

            # Get parameters from list
            l_im_id                 = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_input_file            = self.ParameterList[ "FileIn" ]
            l_file_format           = self.ParameterList[ "FileFormat" ]
            l_epsg_id               = self.ParameterList[ "EpsgIn" ]
            l_verdat_in_id          = self.ParameterList[ "VerdatIn" ]
            l_attribute_order_id    = self.ParameterList[ "AttributeOrder" ]
            l_multiplication_factor = self.ParameterList[ "MultiplicationFactor" ]
            l_separator_id          = self.ParameterList[ "Separator" ]

            # Get separtor from database
            l_attributes = [ BathyDbLib.SEPARATOR_COL ]
            l_values = self.DbConnection.get_obj_attributes ( BathyDbLib.SEPARATOR_CLASS_ID, l_separator_id, l_attributes )
            l_separator = l_values[0]
            self.logger.info("Separator is " + str(l_separator) )

            # Create bathyspace directory
            l_bathyspace_dir  = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )
            l_bathyspace_file = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII

            # Ungridded ascii files are translated into ascii bathyspace format:
            # x <space> y <space> z <space> attr1 <space> attr2 <space> etc.
            # New file is copied to temporary bathyspace directory
            self.logger.info("Translate file into ascii bathyspace format")
            fIn = open( l_input_file,'r' )
            l_check_line = fIn.readline()
            self.logger.info("ASCII file format: " + str(l_check_line))
            fIn.close()

            # Determine nr of attributes
            l_nr_attr = len(l_check_line.rstrip().split( l_separator ))

            # Convert file to bathyspace if file format is correct
            if l_nr_attr >= 4 :
                fIn = open( l_input_file,'r' )
                fOut = open( l_bathyspace_file, 'w' )
                i = 0
                for l_line in fIn:
                    l_output_line = BathyToolsLib.process_imp_ascii_unc_attr_line ( self.logger, l_line, l_attribute_order_id, l_separator, l_separator_id, float(l_multiplication_factor) )
                    if l_output_line :
                        fOut.write ( l_output_line )
                        i = i + 1
                        if i % BathyDbLib.NR_OF_ROWS_PER_INSERT == 0 :
                            self.logger.info( str(i) + " points processed" )
                
                # Log total number of points imported and close files
                self.logger.info ( str(i) + " points written to bathyspace " + l_bathyspace_file )
                fIn.close()
                fOut.close()
            else :
                self.logger.critical("Wrong file format; Bathyspace can not be created")
                raise

            # Store Bathyspace attributes in database
            self.logger.info("Store bathyspace parameters in database")
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_SOURCE_FILES_COL ]   = l_input_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = l_bathyspace_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = l_bathyspace_type
            l_attribute_list [ BathyDbLib.IM_INPUT_FORMAT_COL ]   = l_file_format
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class CreateBathyspacePfm ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Set bathyspace type
            l_bathyspace_type = BathyDbLib.BATHYSPACE_PFM

            # Get parameters from list
            l_im_id                 = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_input_file            = self.ParameterList[ "FileIn" ]
            l_file_format           = self.ParameterList[ "FileFormat" ]
            l_epsg_id               = self.ParameterList[ "EpsgIn" ]
            l_verdat_in_id          = self.ParameterList[ "VerdatIn" ]
            l_multiplication_factor = self.ParameterList[ "MultiplicationFactor" ]

            # Store Bathyspace attributes in database
            self.logger.info("Store bathyspace parameters in database")
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_SOURCE_FILES_COL ]   = l_input_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = l_input_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = l_bathyspace_type
            l_attribute_list [ BathyDbLib.IM_INPUT_FORMAT_COL ]   = l_file_format
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class CreateBathyspaceGml ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Set bathyspace type
            l_bathyspace_type = BathyDbLib.BATHYSPACE_ASCII

            # Get parameters from list
            l_im_id                 = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_input_file            = self.ParameterList[ "FileIn" ]
            l_file_format           = self.ParameterList[ "FileFormat" ]
            l_epsg_id               = self.ParameterList[ "EpsgIn" ]
            l_verdat_in_id          = self.ParameterList[ "VerdatIn" ]
            l_multiplication_factor = self.ParameterList[ "MultiplicationFactor" ]
            l_depth_attribute_name  = self.ParameterList[ "DepthAttributeName" ]

            # Create bathyspace directory
            l_bathyspace_dir  = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )
            l_bathyspace_file = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII

            # Read lines from GML file and write to ascii bathyspace file
            fIn = open( l_input_file,'r' )
            fOut = open( l_bathyspace_file, 'w' )
            i = 0
            for l_line in fIn:
                l_output_line = BathyToolsLib.process_imp_gml_line ( self.logger, l_line, l_depth_attribute_name, float(l_multiplication_factor) )
                if l_output_line :
                    fOut.write ( l_output_line )
                    i = i + 1
                    if i % BathyDbLib.NR_OF_ROWS_PER_INSERT == 0 :
                        self.logger.info( str(i) + " points processed" )

            # Log total number of points imported and close files
            self.logger.info ( str(i) + " points written to bathyspace " + l_bathyspace_file )
            fIn.close()
            fOut.close()

            # Store Bathyspace attributes in database
            self.logger.info("Store bathyspace parameters in database")
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_SOURCE_FILES_COL ]   = l_input_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = l_bathyspace_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = l_bathyspace_type
            l_attribute_list [ BathyDbLib.IM_INPUT_FORMAT_COL ]   = l_file_format
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class CreateBathyspaceEmodnet ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Set bathyspace type
            l_bathyspace_type = BathyDbLib.BATHYSPACE_ASCII

            # Get parameters from list
            l_im_id                 = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_input_file            = self.ParameterList[ "FileIn" ]
            l_file_format           = self.ParameterList[ "FileFormat" ]
            l_epsg_id               = self.ParameterList[ "EpsgIn" ]
            l_verdat_in_id          = self.ParameterList[ "VerdatIn" ]
            l_multiplication_factor = self.ParameterList[ "MultiplicationFactor" ]
            l_cell_size             = self.ParameterList[ "CellSize" ]

            # Create bathyspace directory
            l_bathyspace_dir  = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )
            l_bathyspace_file = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII

            # Emodnet grid files are translated into ascii bathyspace format:
            # New file is copied to temporary bathyspace directory
            self.logger.info("Translate file into ascii bathyspace format")
            fIn = open( l_input_file,'r' )
            l_check_line = fIn.readline()
            self.logger.info("Emodnet file format: " + str(l_check_line))
            fIn.close()

            # Determine nr of attributes
            l_nr_attr = len(l_check_line.rstrip().split( ";" ))

            # Convert file to bathyspace if file format is correct
            if l_nr_attr >= 12 :
                # Read lines from GML file and write to ascii bathyspace file
                fIn = open( l_input_file,'r' )
                fOut = open( l_bathyspace_file, 'w' )
                i = 0
                for l_line in fIn:
                    l_output_line = BathyToolsLib.process_imp_emodnet_line ( self.logger, l_line, float(l_multiplication_factor) )
                    if l_output_line :
                        fOut.write ( l_output_line )
                        i = i + 1
                        if i % BathyDbLib.NR_OF_ROWS_PER_INSERT == 0 :
                            self.logger.info( str(i) + " points processed" )

                # Log total number of points imported and close files
                self.logger.info ( str(i) + " points written to bathyspace " + l_bathyspace_file )
                fIn.close()
                fOut.close()
            else :
                self.logger.critical("Wrong file format; Bathyspace can not be created")
                raise

            # Store Bathyspace attributes in database
            self.logger.info("Store bathyspace parameters in database")
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_SOURCE_FILES_COL ]   = l_input_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = l_bathyspace_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = l_bathyspace_type
            l_attribute_list [ BathyDbLib.IM_INPUT_FORMAT_COL ]   = l_file_format
            l_attribute_list [ BathyDbLib.IM_GRID_CELL_SIZE_COL ] = l_cell_size
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class AddTracklineToIm ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_im_id           = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_trackline_list  = self.ParameterList[ "TracklineList" ]

            # Call database procedure
            self.DbConnection.add_trackline_to_im ( l_im_id, l_trackline_list )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ProcessCm ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_cm_id           = self.ParameterList[ "ContinuousModelId" ]
            l_cm_option       = self.ParameterList[ "ProcessCmOption" ]
            l_exclude_list    = self.ParameterList[ "ExcludeImList" ]

            if int(l_cm_option) == int(BathyDbLib.ACTIVATE_CM) :
                # Update on CM table
                self.logger.info("Activate CM")
                l_attribute_list = {}
                l_attribute_list [ BathyDbLib.CM_ISACTIVE ]    = 'T'
                self.DbConnection.set_obj_attributes ( BathyDbLib.CM_CLASS_ID, l_cm_id, l_attribute_list )

            if int(l_cm_option) == int(BathyDbLib.DEACTIVATE_CM) :
                # Update on CM table
                self.logger.info("Deactivate CM")
                l_attribute_list = {}
                # Delete cookies
                l_attribute_list [ BathyDbLib.CM_ISACTIVE ]    = 'F'
                self.DbConnection.set_obj_attributes ( BathyDbLib.CM_CLASS_ID, l_cm_id, l_attribute_list )

            if int(l_cm_option) == int(BathyDbLib.UPD_EXCLUDE_LIST) :
                # Update on CM table
                self.logger.info("Update exclude list")
                l_attribute_list = {}
                l_attribute_list [ BathyDbLib.CM_UPD_EXCL_LIST ]    = 'T'
                l_attribute_list [ BathyDbLib.CM_EXCL_LIST ]        = l_exclude_list
                self.DbConnection.set_obj_attributes ( BathyDbLib.CM_CLASS_ID, l_cm_id, l_attribute_list )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ActivateImInCm ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_im_id           = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]

#            if int(l_cm_option) == int(BathyDbLib.ACTIVATE_IM_IN_CM) :
            # Update on IM table
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_ACTIVATE ]    = 'T'
            # Date IM activated => SYSDATE
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

#            if int(l_cm_option) == int(BathyDbLib.DEACTIVATE_IM_IN_CM) :
#                # Update on IM table
#                l_attribute_list = {}
#                l_attribute_list [ BathyDbLib.IM_ACTIVATE ]    = 'F'
#                # Date IM activated => NULL
#                self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

            # Update workflowstep
            self.DbConnection.update_workflow_step ( self.ParameterList[ BathyToolsLib.PARAMETER_PROCESS_ID ], BathyDbLib.IM_CLASS_ID, l_im_id )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class DeactivateImInCm ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_im_id           = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]

            # Update on IM table
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_ACTIVATE ]    = 'F'
            # Date IM activated => NULL
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

            # Update workflowstep with process ID of archive CM to set workflowstep back to Archive IM
            self.DbConnection.update_workflow_step ( ARCHIVE_IM, BathyDbLib.IM_CLASS_ID, l_im_id )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class AddTracklinesToIm ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_im_id           = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_trackline_list  = self.ParameterList[ BathyToolsLib.PARAMETER_TRACKLINES ]

            # Call database procedure
            self.DbConnection.remove_tracklines_from_im ( l_im_id )
            self.DbConnection.add_trackline_to_im ( l_im_id, l_trackline_list )

            # Set bathyspace type and coordinate system class ( EPSG is always wgs84 )
            l_bathyspace_type    = BathyDbLib.BATHYSPACE_ASCII
            l_coord_sys_class_id = BathyDbLib.GEOGRAPHIC
            l_coord_sys_id       = self.DbConnection.get_coord_sys_id_db()

            # Create bathyspace directory
            l_bathyspace_dir  = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )
            l_bathyspace_file = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII

            # Write tracklines to bathyspace file and generate rest of bathyspace files
            BathyToolsLib.write_tracklines_to_file ( self.DbConnection, self.logger, l_im_id, l_bathyspace_file, BathyToolsLib.BATHYSPACE_SEP ) 
            BathyToolsLib.gen_bathyspace_files ( self.logger, l_bathyspace_file, l_im_id, l_coord_sys_class_id )

            # Store IM Bathyspace attributes
            self.logger.info("Store IM bathyspace parameters")
            BathyToolsLib.store_bathyspace_dimensions ( self.logger, self.DbConnection, BathyDbLib.IM_CLASS_ID, l_bathyspace_dir, l_im_id, l_coord_sys_class_id ) 

            # IM format is always XYZ
            l_im_format = BathyDbLib.IM_FRMT_XYZ
            # Vertical datum source unknown
            l_verdat_source_id = BathyDbLib.VERTICAL_DATUM_UNKNOWN
            # Separation model unknown
            l_sep_model_id = BathyDbLib.SEP_MODEL_UNKONWN
            # Surveytype = trackline
            l_survey_type = BathyDbLib.TRACKLINE_SURVEYTYPE_ID

            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = l_bathyspace_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = l_bathyspace_type
            l_attribute_list [ BathyDbLib.IM_IM_FORMAT_COL ]      = l_im_format
            l_attribute_list [ BathyDbLib.IM_INPUT_FORMAT_COL ]   = self.ParameterList[ BathyToolsLib.PARAMETER_FILE_FORMAT ]
            l_attribute_list [ BathyDbLib.IM_COORD_SYS_SRC_COL ]  = l_coord_sys_id
            l_attribute_list [ BathyDbLib.IM_SEP_MODEL_COL ]      = l_sep_model_id
            l_attribute_list [ BathyDbLib.IM_STARTDATE_COL ]      = self.ParameterList[ BathyToolsLib.PARAMETER_STARTDATE ]
            l_attribute_list [ BathyDbLib.IM_SOURCE_FILES_COL ]   = l_trackline_list
            l_attribute_list [ BathyDbLib.IM_SURVEYTYPE_COL ]     = l_survey_type
            l_attribute_list [ BathyDbLib.IM_VERDAT_SOURCE_COL ]  = l_verdat_source_id
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

            # Estimate link distance
            link_distance_estimate = BathyToolsLib.get_link_distance_estimate ( self.DbConnection, self.logger, l_im_id, l_coord_sys_id, l_bathyspace_file )

            # Insert link distance estimate
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_LINK_DIST_EST_COL ]  = link_distance_estimate
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

            # Update workflowstep
            self.DbConnection.update_workflow_step ( self.ParameterList[ BathyToolsLib.PARAMETER_PROCESS_ID ], BathyDbLib.IM_CLASS_ID, self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ] )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ImpImESRIASCIIGRID ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Set bathyspace type based on survey type
            # For Esri grid with singlebeam data bathyspace type is set to Ascii 
            # so that it is possible to run TIN hull generation on data from ESRI grid
            #if int(self.ParameterList [ BathyToolsLib.PARAMETER_SURVEYTYPE ]) == int(BathyDbLib.SINGLEBEAM_SURVEYTYPE_ID) :
            #    l_bathyspace_type = BathyDbLib.BATHYSPACE_ASCII
            #else :
            #    l_bathyspace_type = BathyDbLib.BATHYSPACE_SD
            l_bathyspace_type = BathyDbLib.BATHYSPACE_ASCII

            # Get parameters from list
            l_im_id                 = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_input_file            = self.ParameterList[ BathyToolsLib.PARAMETER_INPUT_FILE ]
            l_coord_sys_id          = self.ParameterList[ BathyToolsLib.PARAMETER_COORD_SYS ]

            # Import file
            self.logger.info ( 'Importing file ' + l_input_file )

            # Get coordinate system paraemters input file
            self.logger.info ( 'Get epsg_id source' )
            l_epsg_code_in  = BathyToolsLib.get_epsg_code ( self.DbConnection, self.logger, l_coord_sys_id )

            # Create bathyspace directory
            l_bathyspace_dir = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )

            # Extract boundaries and write to bounds file (necessary for later hull generation)
            l_grid_paramter_list = BathyToolsLib.write_metadata_from_esri_ascii_grid ( self.logger, l_input_file, l_bathyspace_dir, l_im_id  )
            l_no_data_value = l_grid_paramter_list [ BathyDbLib.IM_GRID_NODATA_VALUE ]

            # Now convert ascii grid to sd file
            l_sdfile_out = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
            BathyExecutablesLib.cmdop_gasciitoscalar ( self.DbConnection, self.logger, l_input_file, l_sdfile_out, l_epsg_code_in, l_no_data_value )

            # Now convert sd file to ascii xyz file
            l_bathyspace_file = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII
            BathyExecutablesLib.cmdop_exportsurface ( self.DbConnection, self.logger, l_sdfile_out, l_bathyspace_file )

            # Add separator and extract dimensions
            self.logger.info ("Generate bathyspace files")
            l_coord_sys_class_id = BathyToolsLib.get_coord_sys_class ( self.DbConnection, self.logger, self.ParameterList[ BathyToolsLib.PARAMETER_COORD_SYS ] )
            self.logger.info ("Coordinate system class is " + str(l_coord_sys_class_id) )
            BathyToolsLib.gen_bathyspace_files ( self.logger, l_bathyspace_file, l_im_id, l_coord_sys_class_id )

            # Extract and store boundaries
            self.logger.info ("Store bathyspace dimensions")
            BathyToolsLib.store_bathyspace_dimensions ( self.logger, self.DbConnection, BathyDbLib.IM_CLASS_ID, l_bathyspace_dir, l_im_id, l_coord_sys_class_id )

            # Store IM Bathyspace attributes
            self.logger.info("Store IM bathyspace parameters")
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = l_bathyspace_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = l_bathyspace_type
            l_attribute_list [ BathyDbLib.IM_SDFILE_NAME_COL ]    = l_sdfile_out
            l_attribute_list [ BathyDbLib.IM_IM_FORMAT_COL ]      = BathyDbLib.IM_FRMT_XYZ
            l_attribute_list [ BathyDbLib.IM_SURVEYTYPE_COL ]     = self.ParameterList [ BathyToolsLib.PARAMETER_SURVEYTYPE ]
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

            # Store grid parameter
            self.logger.info("Store source grid parameters")
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_grid_paramter_list )

            # Store BLOB of SD file
            self.logger.info("Store SD file BLOB in database")
            l_blob_file_name = "BLOB" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
            self.DbConnection.set_blob ( BathyDbLib.IM_CLASS_ID, l_im_id, BathyDbLib.IM_SDBLOB_COL, l_sdfile_out, l_blob_file_name )

            # Store IM attribues from import wizard and update workflow step
            BathyToolsLib.store_im_attributes_from_import ( self.DbConnection, self.logger, self.ParameterList )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ImpImASCII ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Set bathyspace type
            l_bathyspace_type = BathyDbLib.BATHYSPACE_ASCII

            # Get parameters from list
            l_im_id         = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_ascii_imp_id  = self.ParameterList[ BathyToolsLib.PARAMETER_ASCII_IMP ]

            # Import file
            self.logger.info ( 'Importing file ' + self.ParameterList[ BathyToolsLib.PARAMETER_INPUT_FILE ] )

            # Create bathyspace directory
            l_bathyspace_dir  = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )
            l_bathyspace_file = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII

            # Run Ascii importer
            BathyExecutablesLib.sens_ascii_importer ( self.DbConnection, self.logger, self.ParameterList, l_bathyspace_file )

            # Generate bathyspace files
            l_coord_sys_class_id = BathyToolsLib.get_coord_sys_class ( self.DbConnection, self.logger, self.ParameterList[ BathyToolsLib.PARAMETER_COORD_SYS ] )
            BathyToolsLib.gen_bathyspace_files ( self.logger, l_bathyspace_file, l_im_id, l_coord_sys_class_id )

            # Extract and store boundaries
            BathyToolsLib.store_bathyspace_dimensions ( self.logger, self.DbConnection, BathyDbLib.IM_CLASS_ID, l_bathyspace_dir, l_im_id, l_coord_sys_class_id )

            # Get IM format for nodal mapping from ascii importer
            l_attributes   = [ BathyDbLib.IM_FORMAT_COL ]
            l_values       = self.DbConnection.get_obj_attributes ( BathyDbLib.ASCII_IMPORTER_CLASS_ID, l_ascii_imp_id, l_attributes )
            l_im_format_id = l_values[0]

            # Store IM Bathyspace attributes
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ] = l_bathyspace_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ] = l_bathyspace_type
            l_attribute_list [ BathyDbLib.IM_IM_FORMAT_COL ]    = l_im_format_id
            l_attribute_list [ BathyDbLib.IM_SURVEYTYPE_COL ]   = self.ParameterList [ BathyToolsLib.PARAMETER_SURVEYTYPE ]
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

            # Store IM attribues from import wizard and add workflow steps
            BathyToolsLib.store_im_attributes_from_import ( self.DbConnection, self.logger, self.ParameterList )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ImpImSd ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Set bathyspace type
            l_bathyspace_type = BathyDbLib.BATHYSPACE_SD

            # Get parameters from list
            l_im_id         = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_input_file    = self.ParameterList[ BathyToolsLib.PARAMETER_INPUT_FILE ]
            l_survey_type   = self.ParameterList [ BathyToolsLib.PARAMETER_SURVEYTYPE ]

            # Import file
            self.logger.info ( 'Importing file ' + str(l_input_file) )

            # Create bathyspace directory
            l_bathyspace_dir  = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )
            l_sdfile_out      = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
            l_asciifile_out   = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII

            # Copy SD file to bathyspace directory
            self.logger.info ( 'Copy SD file to bathyspace directory ' + str(l_bathyspace_dir) )
            shutil.copyfile(l_input_file, l_sdfile_out)

            # Extract bathyspace file from sd file and add separator
            self.logger.info ( 'Extract bathyspace file from SD file')
            BathyExecutablesLib.cmdop_exportsurface ( self.DbConnection, self.logger, l_input_file, l_asciifile_out )

            # Add separator and extract dimensions
            self.logger.info ("Generate bathyspace files")
            l_coord_sys_class_id = BathyToolsLib.get_coord_sys_class ( self.DbConnection, self.logger, self.ParameterList[ BathyToolsLib.PARAMETER_COORD_SYS ] )
            self.logger.info ("Coordinate system class is " + str(l_coord_sys_class_id) )
            BathyToolsLib.gen_bathyspace_files ( self.logger, l_asciifile_out, l_im_id, l_coord_sys_class_id )

            # Extract and store boundaries
            self.logger.info ("Store bathyspace dimensions")
            BathyToolsLib.store_bathyspace_dimensions ( self.logger, self.DbConnection, BathyDbLib.IM_CLASS_ID, l_bathyspace_dir, l_im_id, l_coord_sys_class_id )

            # IM format is always XYZ
            l_im_format = BathyDbLib.IM_FRMT_XYZ

            # Store IM Bathyspace attributes
            self.logger.info("Store IM bathyspace parameters")
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ] = l_asciifile_out
            l_attribute_list [ BathyDbLib.IM_SDFILE_NAME_COL ]  = l_sdfile_out
            l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ] = l_bathyspace_type
            l_attribute_list [ BathyDbLib.IM_SURVEYTYPE_COL ]   = l_survey_type
            l_attribute_list [ BathyDbLib.IM_IM_FORMAT_COL ]    = l_im_format
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

            # Store BLOB of SD file
            self.logger.info("Store SD file BLOB in database")
            l_blob_file_name = "BLOB" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
            self.DbConnection.set_blob ( BathyDbLib.IM_CLASS_ID, l_im_id, BathyDbLib.IM_SDBLOB_COL, l_sdfile_out, l_blob_file_name )

            # Store IM attribues from import wizard and add workflow steps
            BathyToolsLib.store_im_attributes_from_import ( self.DbConnection, self.logger, self.ParameterList )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class SurfaceDiffModelProd ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )
            self.logger.info ("To be implemented" )

            # Get parameters
            l_im_id_base   = self.ParameterList[ BathyToolsLib.PARAMETER_SURVEY_ID ]
            l_cm_id_base   = self.ParameterList[ BathyToolsLib.PARAMETER_CM_ID ]
            l_mbr_wkt      = self.ParameterList[ BathyToolsLib.PARAMETER_PRODUCT_AREA ]
            l_cm_id        = self.ParameterList[ BathyToolsLib.PARAMETER_CM_ID_COMPARE ]
            l_gridsize     = self.ParameterList[ BathyToolsLib.PARAMETER_GRIDSIZE ]
            l_temp_dir     = self.ParameterList[ BathyToolsLib.OUTPUTDIRECTORY ]
            l_epsg_code_db = self.DbConnection.get_epsg_code_db()
            l_output_file  = self.ParameterList[ BathyToolsLib.OUTPUTFILE ]

            self.logger.info ( "IM baseline: " + l_im_id_base )
            self.logger.info ( "CM baseline: " + l_cm_id_base )
            self.logger.info ( "CM compare:  " + l_cm_id )

            if l_im_id_base :
                l_im_base = True
                l_cm_base = False
                l_base_id = l_im_id_base
            else :
                l_im_base = False
                l_cm_base = True
                l_base_id = l_cm_id_base

            # Get points for IM baseline from database
            if l_im_base : 
                self.logger.info ( "Get IM baseline data from DB" )
                l_baseline_file = l_temp_dir + "\\" + "baseline_" + str(l_base_id) + BathyExecutablesLib.FILE_EXT_ASC
                fOut = open( l_baseline_file, 'w')
                l_nr = self.DbConnection.write_xyz_depths_to_file ( fOut, l_im_id_base, None, None, None, BathyToolsLib.SPACE_SEP, False )
                fOut.close()
                self.logger.info( str(l_nr) + " points in IM")
                l_mbr_wkt = self.DbConnection.get_geom ( BathyDbLib.IM_CLASS_ID, l_im_id_base, BathyDbLib.IM_HULL_COL )

            # Get points for IM baseline from database
            if l_cm_base :
                self.logger.info ( "Get CM baseline data from DB" )
                l_nr = 0
                l_cookie_id_list = self.DbConnection.get_cookie_list( l_cm_id, l_mbr_wkt )
                l_baseline_file = l_temp_dir + "\\" + "baseline_" + str(l_base_id) + BathyExecutablesLib.FILE_EXT_ASC
                fOut = open( l_baseline_file, 'w')
                for l_cookie_id in l_cookie_id_list :
                    l_cookie_nr = 0
                    l_cookie_nr = self.DbConnection.write_xyz_depths_to_file ( fOut, None, l_mbr_wkt, l_cookie_id, None, BathyToolsLib.SPACE_SEP, False )
                    self.logger.info (str(l_cookie_nr) + ' points exported'  )
                    l_nr = l_nr + l_cookie_nr
                fOut.close()
                self.logger.info (str(l_nr) + ' points in CM'  )

            # Get CM data from DB
            self.logger.info ( "Get CM data from DB" )
            l_nr = 0
            l_cookie_id_list = self.DbConnection.get_cookie_list( l_cm_id, l_mbr_wkt )
            l_ascii_file_cm = l_temp_dir + "\\" + "cm_compare_" + str(l_cm_id) + BathyExecutablesLib.FILE_EXT_ASC
            fOut = open( l_ascii_file_cm, 'w' )
            for l_cookie_id in l_cookie_id_list :
                l_cookie_nr = 0
                if l_im_base :
                    l_cookie_nr = self.DbConnection.write_xyz_depths_to_file_for_cookie_in_im ( fOut, l_im_id_base, l_cookie_id, BathyToolsLib.SPACE_SEP )
                if l_cm_base :
                     l_cookie_nr = self.DbConnection.write_xyz_depths_to_file ( fOut, None, l_mbr_wkt, l_cookie_id, None, BathyToolsLib.SPACE_SEP, False )
                self.logger.info (str(l_cookie_nr) + ' points exported'  )
                l_nr = l_nr + l_cookie_nr
            fOut.close()
            self.logger.info (str(l_nr) + ' points in CM'  )

            # Generate SD file for CM
            if int(l_nr) > int (0) :

                # Generate SD file for baseline
                self.logger.info ('Generate SD file for baseline with gridsize ' + str(l_gridsize) )
                l_sd_baseline_file  = l_temp_dir + "\\" + "baseline_" + str(l_base_id) + BathyExecutablesLib.FILE_EXT_SD
                l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax = BathyToolsLib.scan_file_for_dimensions ( self.logger, l_baseline_file, BathyToolsLib.SPACE_SEP )
                if float(l_gridsize) > float(BathyToolsLib.DEGREE_TO_METER_SWITCH) :
                    # Assume gridsize is in meters so convert to decimal degrees
                    l_gridsize = BathyToolsLib.convert_cell_size ( self.logger, BathyDbLib.GEOGRAPHIC, l_gridsize, ( float(l_ymax) - float(l_ymin) ) /2 )
                if os.path.exists ( l_sd_baseline_file ) :
                    os.remove( l_sd_baseline_file )
                BathyExecutablesLib.cmdop_gridder ( self.DbConnection, self.logger, l_baseline_file, l_sd_baseline_file, l_epsg_code_db, l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax, l_gridsize )
                os.remove( l_baseline_file )

                # Generate SD file for CM
                self.logger.info ('Generate SD file for CM with gridsize ' + str(l_gridsize)  )
                l_sd_file_cm = l_temp_dir + "\\" + "cm_compare_" + str(l_cm_id) + BathyExecutablesLib.FILE_EXT_SD
                l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax = BathyToolsLib.scan_file_for_dimensions ( self.logger, l_ascii_file_cm, BathyToolsLib.SPACE_SEP )
                if float(l_gridsize) > float(BathyToolsLib.DEGREE_TO_METER_SWITCH) :
                    # Assume gridsize is in meters so convert ot decimal degrees
                    l_gridsize = BathyToolsLib.convert_cell_size ( self.logger, BathyDbLib.GEOGRAPHIC, l_gridsize, ( float(l_ymax) - float(l_ymin) ) / float(2.0) )
                if os.path.exists ( l_sd_file_cm ) :
                    os.remove( l_sd_file_cm )
                BathyExecutablesLib.cmdop_gridder ( self.DbConnection, self.logger, l_ascii_file_cm, l_sd_file_cm, l_epsg_code_db, l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax, l_gridsize )
                os.remove( l_ascii_file_cm )

                # Generate surface difference model
                self.logger.info ('Generate surface difference model '  )
                self.logger.info ("Baseline SD file " + str(l_sd_baseline_file) )
                self.logger.info ("CM SD file " + str(l_sd_file_cm) )
                l_sd_file_out = l_output_file
                os.chdir(l_temp_dir)
                l_sd_file_cm       = os.path.basename ( l_sd_file_cm )
                l_sd_baseline_file = os.path.basename ( l_sd_baseline_file )
                BathyExecutablesLib.cmdop_surfacedifference ( self.DbConnection, self.logger, l_sd_file_cm, l_sd_baseline_file, l_sd_file_out )
                self.logger.info ("SD file surface difference " + str(l_sd_file_out) )
                self.logger.info ("Deeper is negative")

                # Remove temp files
                os.remove ( l_sd_file_cm )
                os.remove ( l_sd_baseline_file )

                # Zip output (remove .sd extension)
                l_output_file_zip = l_output_file.rstrip().split(".")[0]
                BathyToolsLib.zip_files ( self.logger, l_temp_dir + "\\" + l_output_file_zip  )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            os.sys.exit("Execution stopped")


class SurfaceDifferenceModel ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters
            l_im_id       = self.ParameterList[ BathyToolsLib.PARAMETER_SURVEY_ID ]
            l_cm_id       = self.ParameterList[ BathyToolsLib.PARAMETER_CM_ID ]
            l_gridsize    = self.ParameterList[ BathyToolsLib.PARAMETER_GRIDSIZE ]

            # Get survey type and bathyspace attributes
            l_attributes = [  BathyDbLib.IM_BATHYSP_FILE_COL, BathyDbLib.IM_PROC_DATA_FILE_COL ]
            l_values = self.DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attributes )
            l_bathyspace_file = l_values[0]
            l_processed_file  = l_values[1]
            l_epsg_code_db    = self.DbConnection.get_epsg_code_db()

            # Get Bathyspace directory from bathyspace file
            l_bathyspace_dir    = os.path.dirname(l_bathyspace_file)

            # Check if directory exists
            if not os.path.isdir( l_bathyspace_dir ) :
                self.logger.critical( "Bathyspace directory is NOT on this client")
                os.sys.exit("Execution stopped")

            # Get MBR IM as WKT
            self.logger.info ('Get IM hull '  )
            l_im_mbr_wkt = self.DbConnection.get_geom ( BathyDbLib.IM_CLASS_ID, l_im_id, BathyDbLib.IM_HULL_COL )

            # Get CM data from DB
            self.logger.info ('Get CM data from DB '  )
            l_nr = 0
            l_cookie_id_list = self.DbConnection.get_cookie_list( l_cm_id, l_im_mbr_wkt )
            l_ascii_file_cm = l_bathyspace_dir + "\\" + "cm_compare_" + str(l_cm_id) + BathyExecutablesLib.FILE_EXT_ASC
            fOut = open( l_ascii_file_cm, 'w' )
            for l_cookie_id in l_cookie_id_list :
                l_cookie_nr = 0
                self.logger.info("Export points in IM segment " + str(l_cookie_id) + " from CM " + str(l_cm_id) )
                #l_nr = self.DbConnection.write_xyz_depths_to_file_for_cm ( fOut, None, l_im_mbr_wkt, l_cookie_id, None, BathyToolsLib.BATHYSPACE_SEP )
                l_cookie_nr = self.DbConnection.write_xyz_depths_to_file_for_cookie_in_im ( fOut, l_im_id, l_cookie_id, BathyToolsLib.BATHYSPACE_SEP )
                self.logger.info (str(l_cookie_nr) + ' points exported '  )
                l_nr = l_nr + l_cookie_nr
            fOut.close()
            self.logger.info (str(l_nr) + ' points in CM '  )

            # Generate SD file for CM
            if int(l_nr) > int (0) :

                # Generate SD file for IM
                self.logger.info ('Generate SD file for IM ')
                l_sd_file_im  = l_bathyspace_dir + "\\" + "im_compare_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
                l_ascii_file_tmp_im, l_ascii_file_bounds_im = BathyToolsLib.get_pp_bounds_file_names ( self.logger, l_bathyspace_dir, l_im_id )
                l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax = BathyToolsLib.gen_xyz_tmp_file_geographic( self.logger, l_processed_file, l_ascii_file_tmp_im, l_ascii_file_bounds_im )
                if float(l_gridsize) > float(BathyToolsLib.DEGREE_TO_METER_SWITCH) :
                    # Assume gridsize is in meters so convert to decimal degrees
                    l_gridsize = BathyToolsLib.convert_cell_size ( self.logger, BathyDbLib.GEOGRAPHIC, l_gridsize, ( float(l_ymax) - float(l_ymin) ) /2 )
                self.logger.info ('Generate SD file for IM with gridsize ' + str(l_gridsize) )
                if os.path.exists ( l_sd_file_im ) :
                    os.remove( l_sd_file_im )
                BathyExecutablesLib.cmdop_gridder ( self.DbConnection, self.logger, l_ascii_file_tmp_im, l_sd_file_im, l_epsg_code_db, l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax, l_gridsize )

                # Generate SD file for CM
                self.logger.info ('Generate SD file for CM '  )
                l_sd_file_cm = l_bathyspace_dir + "\\" + "cm_compare_" + str(l_cm_id) + BathyExecutablesLib.FILE_EXT_SD
                l_ascii_file_tmp_cm    = l_bathyspace_dir + "\\" + "tmp_cm_" + l_cm_id + BathyExecutablesLib.FILE_EXT_ASCII
                l_ascii_file_bounds_cm = l_bathyspace_dir + "\\" + "bounds_cm_" + l_cm_id + BathyExecutablesLib.FILE_EXT_ASCII
                if os.path.exists ( l_ascii_file_tmp_cm ) :
                    os.remove( l_ascii_file_tmp_cm )
                if os.path.exists ( l_ascii_file_bounds_cm ) :
                    os.remove( l_ascii_file_bounds_cm )
                l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax = BathyToolsLib.gen_xyz_tmp_file_geographic( self.logger, l_ascii_file_cm, l_ascii_file_tmp_cm, l_ascii_file_bounds_cm )
                if float(l_gridsize) > float(1.0) :
                    # Assume gridsize is in meters so convert ot decimal degrees
                    l_gridsize = BathyToolsLib.convert_cell_size ( self.logger, BathyDbLib.GEOGRAPHIC, l_gridsize, ( float(l_ymax) - float(l_ymin) ) / float(2.0) )
                self.logger.info ('Generate SD file for CM with gridsize ' + str(l_gridsize) )
                if os.path.exists ( l_sd_file_cm ) :
                    os.remove( l_sd_file_cm )
                BathyExecutablesLib.cmdop_gridder ( self.DbConnection, self.logger, l_ascii_file_tmp_cm, l_sd_file_cm, l_epsg_code_db, l_xmin, l_xmax, l_ymin, l_ymax, l_zmin, l_zmax, l_gridsize )
                os.remove( l_ascii_file_cm )
                os.remove( l_ascii_file_tmp_cm )
                os.remove( l_ascii_file_bounds_cm )

                # Generate surface difference model
                self.logger.info ('Generate surface difference model '  )
                self.logger.info ("IM SD file " + str(l_sd_file_im) )
                self.logger.info ("CM SD file " + str(l_sd_file_cm) )
                l_sd_file_out = "surface_difference_model_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
                os.chdir(l_bathyspace_dir)
                BathyExecutablesLib.cmdop_surfacedifference ( self.DbConnection, self.logger, l_sd_file_cm, l_sd_file_im, l_sd_file_out )
                self.logger.info ("SD file surface difference " + str(l_sd_file_out) )
                self.logger.info ("Deeper is negative")

                # Store file location in database
                if os.path.exists ( l_sd_file_out ) :
                    l_attributes   = [ BathyDbLib.PARAMETER_CLASS_COL, BathyDbLib.PARAMETER_INSTANCE_COL ]
                    l_values       = self.DbConnection.get_obj_attributes ( BathyDbLib.PRODUCTORDER_CLASS_ID, self.ParameterList [ BathyToolsLib.ID ], l_attributes )
                    l_process_id   = l_values[0]
                    l_instance_id  = l_values[1]
                    l_attribute_list = {}
                    l_attribute_list [ BathyDbLib.SD_FILE_OUT_COL ]  = str(l_bathyspace_dir) + "/" + str(l_sd_file_out)
                    self.DbConnection.set_obj_attributes ( l_process_id, l_instance_id, l_attribute_list )
                    self.logger.info ("Instance " + str(l_instance_id) + " for parameter class " + str(l_process_id) + " updated" )
                else :
                    self.logger.critical ( "Generation of surface difference model failed")
                    os.sys.exit("Execution stopped")

                # Remove files
                os.remove( l_sd_file_im )
                os.remove( l_sd_file_cm )

            else :
                self.logger.warning ("IM does not overlap CM; No surface difference model generated" )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            os.sys.exit("Execution stopped")

class SepModelFileImp ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from parameter object
            l_task_id      = self.ParameterList[ BathyToolsLib.TASKID ]
            l_sep_file_id  = self.ParameterList[ BathyToolsLib.PARAMETER_SEP_FILE_ID ]
            l_coord_sys_id = self.ParameterList[ BathyToolsLib.PARAMETER_COORD_SYS ]
            l_etrsyear     = self.ParameterList[ BathyToolsLib.PARAMETER_ETRSYEAR ]

            # Get seperation model file attributes from database
            self.logger.info("Get seperation model file attributes from database")
            l_attributes = [  BathyDbLib.SEP_MOD_HULL_FILE_COL, BathyDbLib.SEP_MOD_DATA_FILE_COL, BathyDbLib.SEP_MOD_ID_COL ]
            l_values = self.DbConnection.get_obj_attributes ( BathyDbLib.SEP_MOD_FILE_CLASS_ID, l_sep_file_id, l_attributes )
            l_hull_file  = l_values[0]
            l_data_file  = l_values[1]
            l_sep_mod_id = l_values[2]
                        
            # Set direction positive
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.SEP_MOD_DIR_COL ]       = "1"
            self.DbConnection.set_obj_attributes ( BathyDbLib.SEP_MOD_FILE_CLASS_ID, l_sep_file_id, l_attribute_list )

            # Create bathyspace directory
            l_bathyspace_dir  = BathyToolsLib.create_bathyspace_dir ( self.logger, l_sep_file_id )

            # Get coordinate system paraemters input file
            self.logger.info ( 'Get epsg_id source' )
            l_epsg_code_in       = BathyToolsLib.get_epsg_code ( self.DbConnection, self.logger, l_coord_sys_id )
            l_coord_sys_class_id = BathyToolsLib.get_coord_sys_class ( self.DbConnection, self.logger, self.ParameterList[ BathyToolsLib.PARAMETER_COORD_SYS ] )
            l_wkt_in             = self.DbConnection.get_wkt_coord_sys_id ( l_coord_sys_id )
            l_epsg_code_db       = self.DbConnection.get_epsg_code_db ()
            l_wkt_db             = self.DbConnection.get_wkt_epsg_code ( l_epsg_code_db )

            # Extract boundaries and write to bounds file and convert cellsize to decimal degrees
            l_grid_paramter_list = BathyToolsLib.write_metadata_from_esri_ascii_grid ( self.logger, l_data_file, l_bathyspace_dir, l_sep_file_id  )
            if int(l_coord_sys_class_id) <> int( BathyDbLib.GEOGRAPHIC ) :
                if l_grid_paramter_list.has_key( BathyDbLib.IM_GRID_CELL_SIZE_COL ) :
                    l_y_gridsize = float ( l_grid_paramter_list[ BathyDbLib.IM_GRID_CELL_SIZE_COL ] )
                if l_grid_paramter_list.has_key( BathyDbLib.IM_GRID_YDIM ) :
                    l_y_gridsize = float ( BathyDbLib.IM_GRID_YDIM )
                if l_grid_paramter_list.has_key( BathyDbLib.IM_GRID_YLLCENTER ) :
                    l_y_avg = ( float( l_grid_paramter_list [ BathyDbLib.IM_GRID_YLLCENTER ] ) - 0.5 * l_y_gridsize ) + ( 0.5 * float( l_grid_paramter_list [ BathyDbLib.IM_GRID_NROWS ] ) * l_y_gridsize )
                if l_grid_paramter_list.has_key( BathyDbLib.IM_GRID_YLLCORNER ) :
                    l_y_avg = ( float( l_grid_paramter_list [ BathyDbLib.IM_GRID_YLLCORNER ] ) ) + ( 0.5 * float( l_grid_paramter_list [ BathyDbLib.IM_GRID_NROWS ] ) * l_y_gridsize )
                l_gridsize = BathyToolsLib.convert_cell_size ( self.logger, BathyDbLib.GEOGRAPHIC, l_y_gridsize, l_y_avg )
            if int(l_coord_sys_class_id) == int( BathyDbLib.GEOGRAPHIC ) :
                if l_grid_paramter_list.has_key( BathyDbLib.IM_GRID_CELL_SIZE_COL ) :
                    l_gridsize = float ( l_grid_paramter_list[ BathyDbLib.IM_GRID_CELL_SIZE_COL ] )
                if l_grid_paramter_list.has_key( BathyDbLib.IM_GRID_YDIM ) :
                    l_y_gridsize = float ( BathyDbLib.IM_GRID_YDIM )
                    l_x_gridsize = float ( BathyDbLib.IM_GRID_XDIM )
                    if l_x_gridsize > l_y_gridsize :
                        l_gridsize = l_x_gridize
                    else :
                        l_gridsize = l_y_gridize
            self.logger.info ( 'Gridize in decimal degrees = ' + str(l_gridsize) )

            # Now convert ascii grid to sd file
            self.logger.info ( 'Convert Esri Ascii grid to SD file' )
            l_sdfile_out = l_bathyspace_dir + "\\" + "separation_model_file_" + str(l_sep_file_id) + BathyExecutablesLib.FILE_EXT_SD
            BathyExecutablesLib.cmdop_gasciitoscalar ( self.DbConnection, self.logger, l_data_file, l_sdfile_out, l_epsg_code_in, l_grid_paramter_list[ BathyDbLib.IM_GRID_NODATA_VALUE ] )

            # Now convert sd file to ascii xyz file
            self.logger.info ( 'Convert SD file to Ascii xyz file' )
            l_bathyspace_file = l_bathyspace_dir + "\\" + "separation_model_file_" + str(l_sep_file_id) + BathyExecutablesLib.FILE_EXT_ASCII
            BathyExecutablesLib.cmdop_exportsurface ( self.DbConnection, self.logger, l_sdfile_out, l_bathyspace_file )
            BathyToolsLib.gen_bathyspace_files ( self.logger, l_bathyspace_file, l_sep_file_id, l_coord_sys_class_id )

            # Get hull from shape file and apply coordinate transformation
            self.logger.info ( 'Get separation model hull from shape file and apply coordinate transformation' )
            l_hull_wkt = BathyExecutablesLib.ogr_extract_hull_from_shapefile ( self.logger, l_hull_file, l_sep_file_id, l_bathyspace_dir, l_wkt_in, l_wkt_db, l_etrsyear,l_epsg_code_in, l_epsg_code_db )

            # Insert hull
            self.logger.info ( 'Insert separation model hull into database' )
            self.DbConnection.insert_hull( BathyDbLib.SEP_MOD_FILE_CLASS_ID, l_sep_file_id, l_hull_wkt, BathyDbLib.SEP_MOD_HULL_COL, l_epsg_code_db )

            # Store location of temporary SD file and BLOB in database 
            self.logger.info ("Insert SD file into database")
            l_blob_file_name = "BLOB" + str(l_sep_file_id) + BathyExecutablesLib.FILE_EXT_SD
            self.DbConnection.set_blob ( BathyDbLib.SEP_MOD_FILE_CLASS_ID, l_sep_file_id, BathyDbLib.SEP_MOD_BLOB_COL, l_sdfile_out, l_blob_file_name )

            # Run Makegrid for geodetic transformations
            self.logger.info ( 'Apply coordinate transformation' )
            l_input_file  = os.path.basename( l_bathyspace_file )
            l_output_file = BathyExecutablesLib.makegrid_geo_conv (self.logger, l_input_file, l_bathyspace_dir, l_epsg_code_in, l_epsg_code_db, BathyDbLib.VERDAT_UNKNOWN, BathyDbLib.VERDAT_UNKNOWN, 0, 1, l_etrsyear, ";", ";", l_wkt_in, l_wkt_db, None, None, None, None )
            self.logger.info ('File to import into database: ' + str(l_output_file) )

            # Import separation model file into database
            self.logger.info ( 'Write separation model data into DB' )
            l_im_format_id = BathyDbLib.IM_FRMT_XYZ
            BathyToolsLib.write_depths_to_database  ( self.DbConnection, self.logger, l_output_file, l_im_format_id )
            BathyToolsLib.create_spatial_index_on_database ( self.DbConnection, self.logger, BathyDbLib.SEP_MOD_FILE_CLASS_ID, l_sep_file_id, l_task_id  )

            # Update attributes
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.SEP_MOD_GRIDSIZE ] = l_gridsize
            self.DbConnection.set_obj_attributes ( BathyDbLib.SEP_MOD_FILE_CLASS_ID, l_sep_file_id, l_attribute_list )

            # Bathyspace is dropped
            BathyToolsLib.drop_bathyspace_dir ( self.logger, l_bathyspace_dir )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            # First delete inserted separation model file
            self.DbConnection.del_obj_instance ( BathyDbLib.SEP_MOD_FILE_CLASS_ID, l_sep_file_id )
            # Then delete separation model if it has no separation model files anymore
            if not self.DbConnection.has_sep_model_files ( l_sep_mod_id ) :
                self.DbConnection.del_obj_instance ( BathyDbLib.SEP_MOD_CLASS_ID, l_sep_mod_id )
            self.DbConnection.commit_close()
            BathyToolsLib.drop_bathyspace_dir ( self.logger, l_bathyspace_dir )
            raise

class ImpImBAG ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Set bathyspace type
            # l_bathyspace_type = BathyDbLib.BATHYSPACE_BAG
            l_bathyspace_type = BathyDbLib.BATHYSPACE_ASCII

            # Get parameters from list
            l_im_id                 = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_input_file            = self.ParameterList[ BathyToolsLib.PARAMETER_INPUT_FILE ]
            l_bag_imp_id            = self.ParameterList[ BathyToolsLib.PARAMETER_BAGIMPORTER ]

            # Import file
            self.logger.info ( 'Importing file ' + l_input_file )

            # Get BAG importer parameters SDB_BAGIMPORTER
            attributes   = [ BathyDbLib.BAG_IMP_BATHY_COL, BathyDbLib.BAG_IMP_META_COL, BathyDbLib.BAG_IMP_UNC_COL ,BathyDbLib.BAG_METAMAPPER_COL  ]
            values       = self.DbConnection.get_obj_attributes ( BathyDbLib.BAG_IMPORTER_CLASS_ID, l_bag_imp_id, attributes )
            l_imp_bathy_data = values[0]
            l_imp_meta_data  = values[1]
            l_imp_unc_data   = values[2]
            l_metamapper_id  = values[3]

            # Add metadatamapper ID to paraemterlist
            self.ParameterList[ BathyToolsLib.PARAMETER_METADATAMAPPER ] = l_metamapper_id

            # Check is data has to be imported
            if str(l_imp_bathy_data) == "T" :

                # Create bathyspace directory
                l_bathyspace_dir   = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )
                l_sdfile_out       = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
                l_asciifile_out    = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII
                l_metadata_xml_out = l_asciifile_out + ".xml"

                # Convert BAG to SD file
                BathyExecutablesLib.cmdop_bagtoscalar ( self.logger, l_input_file, l_sdfile_out )

                # Convert BAG to ASCII file and extract metadata XML
                BathyExecutablesLib.cmdop_bagtoascii ( self.logger, l_input_file, l_asciifile_out )

                # Add separator and extract dimensions
                self.logger.info ("Generate bathyspace files")
                l_coord_sys_class_id = BathyToolsLib.get_coord_sys_class ( self.DbConnection, self.logger, self.ParameterList[ BathyToolsLib.PARAMETER_COORD_SYS ] )
                self.logger.info ("Coordinate system class is " + str(l_coord_sys_class_id) )
                BathyToolsLib.gen_bathyspace_files ( self.logger, l_asciifile_out, l_im_id, l_coord_sys_class_id )

                # Extract and store boundaries
                self.logger.info ("Store bathyspace dimensions")
                BathyToolsLib.store_bathyspace_dimensions ( self.logger, self.DbConnection, BathyDbLib.IM_CLASS_ID, l_bathyspace_dir, l_im_id, l_coord_sys_class_id )

                # Check if uncertainty is required
                if str(l_imp_unc_data) == "T" :
                    l_im_format = BathyDbLib.IM_FRMT_XYZU
                else :
                    l_im_format = BathyDbLib.IM_FRMT_XYZ
                    #BathyToolsLib.remove_uncertainty_attribute ( self.logger, l_asciifile_out )

                # Extract epsg_id from BAG metadata XML
                l_epsg_id_db = BathyToolsLib.extract_metadata_from_bag ( self.DbConnection, self.logger, l_metadata_xml_out )

                # Store IM Bathyspace file location first
                l_attribute_list = {}
                l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ] = l_asciifile_out
                l_attribute_list [ BathyDbLib.IM_SURVEYTYPE_COL ]   = BathyDbLib.MODEL_SURVEYTYPE_ID
                self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

                # Store IM attribues from import wizard and update workflow step first
                BathyToolsLib.store_im_attributes_from_import ( self.DbConnection, self.logger, self.ParameterList )

                # Store Bathyspace attributes in database, epsg_id from import parameters is overwritten with epsg from BAG
                # For BAG im_type = Model
                self.logger.info("Store bathyspace parameters in database")
                l_attribute_list = {}
                l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = l_asciifile_out
                l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = l_bathyspace_type
                l_attribute_list [ BathyDbLib.IM_SDFILE_NAME_COL ]    = l_sdfile_out
                l_attribute_list [ BathyDbLib.IM_IM_FORMAT_COL ]      = l_im_format
                l_attribute_list [ BathyDbLib.IM_SEP_MODEL_COL ]      = self.ParameterList[ BathyToolsLib.PARAMETER_VERT_REF ]
                l_attribute_list [ BathyDbLib.IM_SURVEYTYPE_COL ]     = BathyDbLib.MODEL_SURVEYTYPE_ID
                if l_epsg_id_db :
                    l_attribute_list [ BathyDbLib.IM_COORD_SYS_SRC_COL ]  = l_epsg_id_db
                else :
                    l_attribute_list [ BathyDbLib.IM_COORD_SYS_SRC_COL ]  = self.ParameterList[ BathyToolsLib.PARAMETER_COORD_SYS ]
                    l_attribute_list [ BathyDbLib.IM_ETRSYEAR_COL ]       = self.ParameterList[ BathyToolsLib.PARAMETER_ETRSYEAR ]
                self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

                # Store BLOB of SD file
                self.logger.info("Store SD file BLOB in database")
                l_blob_file_name = "BLOB" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_SD
                self.DbConnection.set_blob ( BathyDbLib.IM_CLASS_ID, l_im_id, BathyDbLib.IM_SDBLOB_COL, l_sdfile_out, l_blob_file_name )

            # Process BAG Metadata
            if str(l_imp_meta_data) == "T" :
                # First commit connection because bag importer updates some individual model
                self.DbConnection.commit_close()
                BathyExecutablesLib.sens_bag_importer ( self.logger, self.ParameterList )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            os.sys.exit("Execution stopped")


class ImpImDONAR  ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Import file
            self.logger.info ( 'Importing file ' + self.ParameterList[ BathyToolsLib.PARAMETER_INPUT_FILE ] )

            # Start executable
            BathyExecutablesLib.sens_donar_importer ( self.DbConnection, self.logger, self.ParameterList )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            os.sys.exit("Execution stopped")


class ImpImGML ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Set bathyspace type
            l_bathyspace_type = BathyDbLib.BATHYSPACE_ASCII

            # Get parameters from list
            l_im_id                 = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]
            l_input_file            = self.ParameterList[ BathyToolsLib.PARAMETER_INPUT_FILE ]
            l_depth_attribute_name  = self.ParameterList[ BathyToolsLib.PARAMETER_DEPTH_ATTR ]

            # Import file
            self.logger.info ( 'Importing file ' + l_input_file )

            # Create bathyspace directory
            l_bathyspace_dir  = BathyToolsLib.create_bathyspace_dir ( self.logger, l_im_id )
            l_bathyspace_file = l_bathyspace_dir + "\\" + "survey_" + str(l_im_id) + BathyExecutablesLib.FILE_EXT_ASCII

            # Read lines from GML file and write to ascii bathyspace file
            fIn = open( l_input_file,'r' )
            fOut = open( l_bathyspace_file, 'w' )
            i = 0
            for l_line in fIn:
                l_output_line = BathyToolsLib.process_imp_gml_line ( self.logger, l_line, l_depth_attribute_name )
                if l_output_line :
                    fOut.write ( l_output_line )
                    i = i + 1
                    if i % BathyDbLib.NR_OF_ROWS_PER_INSERT == 0 :
                        self.logger.info( str(i) + " points processed" )

            # Log total number of points imported and close files
            self.logger.info ( str(i) + " points written to bathyspace " + l_bathyspace_file )
            fIn.close()
            fOut.close()

            # Add separator and extract dimensions
            self.logger.info ("Generate bathyspace files")
            l_coord_sys_class_id = BathyToolsLib.get_coord_sys_class ( self.DbConnection, self.logger, self.ParameterList[ BathyToolsLib.PARAMETER_COORD_SYS ] )
            self.logger.info ("Coordinate system class is " + str(l_coord_sys_class_id) )
            BathyToolsLib.gen_bathyspace_files ( self.logger, l_bathyspace_file, l_im_id, l_coord_sys_class_id )

            # Extract and store boundaries
            self.logger.info ("Store bathyspace dimensions")
            BathyToolsLib.store_bathyspace_dimensions ( self.logger, self.DbConnection, BathyDbLib.IM_CLASS_ID, l_bathyspace_dir, l_im_id, l_coord_sys_class_id )

            # Store Bathyspace attributes in database
            self.logger.info("Store bathyspace parameters in database")
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_BATHYSP_FILE_COL ]   = l_bathyspace_file
            l_attribute_list [ BathyDbLib.IM_BATHYSP_TYPE_COL ]   = l_bathyspace_type
            l_attribute_list [ BathyDbLib.IM_SURVEYTYPE_COL ]     = self.ParameterList [ BathyToolsLib.PARAMETER_SURVEYTYPE ]
            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

            # Store IM attributes from import wizard and update workflow step
            BathyToolsLib.store_im_attributes_from_import ( self.DbConnection, self.logger, self.ParameterList )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ImpImMetadataCsv ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Start importer
            BathyExecutablesLib.sens_csv_importer ( self.logger, self.ParameterList )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class ImpImMetadataIsoXml ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Run importer
            BathyExecutablesLib.sens_isoxml_importer ( self.logger, self.ParameterList )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise


class GenerateProducts ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )
            l_temp_dir = BathyToolsLib.get_working_dir( self.logger, self.ParameterList [ BathyToolsLib.TEMPDIR ] )
            BathyExecutablesLib.makegrid_export ( self.DbConnection, self.logger, self.ParameterList, l_temp_dir )

            # Zip all output
            l_output_file = self.ParameterList[ BathyToolsLib.OUTPUTFILE ] 
            BathyToolsLib.zip_files ( self.logger, l_output_file )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            raise

class PostprocessIm ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Get parameters from list
            l_im_id                 = self.ParameterList[ BathyToolsLib.PARAMETER_IM_ID ]

            # Get bathyspace type and file from database
            l_attributes = [ BathyDbLib.IM_BATHYSP_TYPE_COL, BathyDbLib.IM_BATHYSP_FILE_COL, BathyDbLib.IM_IM_FORMAT_COL, BathyDbLib.IM_LINK_DISTANCE_COL, BathyDbLib.IM_COORD_SYS_SRC_COL ]
            l_values = self.DbConnection.get_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attributes )
            l_bathyspace_type_id = l_values[0]
            l_bathyspace_file    = l_values[1]
            l_im_format          = l_values[2]
            l_link_distance      = l_values[3]
            l_coord_sys_id       = l_values[4]

            # Check if directory exists
            l_bathyspace_dir    = os.path.dirname(l_bathyspace_file)
            if not os.path.isdir( l_bathyspace_dir ) :
                self.logger.critical( "Bathyspace directory is NOT on this client")
                sys.exit("Execution stopped")

            # Unload Trackline bathyspace
            if int(l_bathyspace_type_id) == int(BathyDbLib.BATHYSPACE_TL) :
                # Create temp dir and write tracklines to file
                self.logger.info("Unload trackline bathyspace")
                l_temp_dir       = self.ParameterList[ BathyToolsLib.TEMPDIR ]
                l_input_file     = "UnloadedIM_" + str(l_im_id) + ".xyz"
                l_trackline_file = l_temp_dir + "\\" + l_input_file
                l_separator      = BathyToolsLib.BATHYSPACE_SEP
                BathyToolsLib.write_tracklines_to_file ( self.DbConnection, self.logger, l_im_id, l_trackline_file, l_separator )

            # Unload PFM bathyspace
            if int(l_bathyspace_type_id) == int(BathyDbLib.BATHYSPACE_PFM) :
                self.logger.info("Unload PFM bathyspace")
                self.logger.info("To be implemented")

            # Unload ASCII bathyspace
            if int(l_bathyspace_type_id) == int(BathyDbLib.BATHYSPACE_ASCII) :
                self.logger.info("Unload ASCII bathyspace")
                l_temp_dir     = os.path.dirname( l_bathyspace_file )
                l_input_file   = os.path.basename( l_bathyspace_file )

            # Unload SD bathyspace
            if int(l_bathyspace_type_id) == int(BathyDbLib.BATHYSPACE_SD) :
                self.logger.info("Unload SD bathyspace")
                l_temp_dir     = os.path.dirname( l_bathyspace_file )
                l_input_file   = os.path.basename( l_bathyspace_file )
                # BathyToolsLib.gen_bathyspace_files ( self.logger, l_bathyspace_file )
                #l_unload_file  = l_temp_dir + "\\" + l_input_file
                #BathyToolsLib.unload_sdfile ( self.DbConnection, self.logger, l_im_id, l_bathyspace_file, l_unload_file )

            # For BAG bathyspace xyzuncertainty file is already availbale from BAG file
            if int(l_bathyspace_type_id) == int(BathyDbLib.BATHYSPACE_BAG) :
                self.logger.info("Unload BAG bathyspace")
                l_temp_dir     = os.path.dirname( l_bathyspace_file )
                l_input_file   = os.path.basename( l_bathyspace_file )
                #BathyToolsLib.gen_bathyspace_files ( self.logger, l_bathyspace_file )

            # Convert gridsize (always in meters) to decimal degrees when coordinate system is geographic
            l_coord_sys_class_id = BathyToolsLib.get_coord_sys_class ( self.DbConnection, self.logger, l_coord_sys_id )
            l_gridsize_m         = self.ParameterList[ BathyToolsLib.PARAMETER_GRIDSIZE ]
            if int(l_coord_sys_class_id) == int( BathyDbLib.GEOGRAPHIC ) and str(self.ParameterList[ BathyToolsLib.PARAMETER_RESAMPLE ]) == "T" :
                l_y_avg       = BathyToolsLib.get_avg_y_source ( self.logger, l_bathyspace_dir, l_im_id )
                l_gridsize_dd = BathyToolsLib.convert_meters_to_decimal_degrees ( self.logger, l_gridsize_m, l_y_avg) 
                self.ParameterList[ BathyToolsLib.PARAMETER_GRIDSIZE ] = l_gridsize_dd
                self.logger.info ("Gridsize converted from " + str(l_gridsize_m) + " m to " + str(l_gridsize_dd) + " decimal degrees" )


            # Now start Makegrid for coordinate conversions and gridding and/or interpolation
            l_processed_datafile = BathyExecutablesLib.makegrid_postprocessing ( self.DbConnection, self.logger, self.ParameterList, l_temp_dir, l_input_file ) 

            # If resample (and interpolation) then regenerate the hull and store new SD file in database
            if self.ParameterList[ BathyToolsLib.PARAMETER_GRIDSIZE ] :
                l_gridsize = self.ParameterList[ BathyToolsLib.PARAMETER_GRIDSIZE ]
            else :
                l_gridsize = None

            #if str(self.ParameterList[ BathyToolsLib.PARAMETER_RESAMPLE ]) == "T" :
            # IF resample is T then also regenerate the hull since boundary of IM has changed
            BathyToolsLib.generate_postprocess_sdfile ( self.DbConnection, self.logger, l_im_id, l_processed_datafile, l_gridsize, str(self.ParameterList[ BathyToolsLib.PARAMETER_RESAMPLE ]) )
            l_ascii_file, l_bounds_file = BathyToolsLib.get_pp_bounds_file_names ( self.logger, l_bathyspace_dir, l_im_id )
            l_ascii_file                = l_ascii_file
            #else :
            #    l_bounds_file               = BathyToolsLib.get_bounds_file_name ( self.logger, l_bathyspace_dir, l_im_id )

            # Get number of points of model
            l_nr_of_points = BathyToolsLib.get_nr_of_points_model ( self.logger, l_bounds_file )

            # If user has selected postprocessing then update im_format if IM to SENS IM format
            # Makegrid generates file with .grd so replace .asc with .grd
            self.logger.info("Update IM attributes in database")
            self.logger.info("Store processed datafile " + str(l_processed_datafile) )
            l_attribute_list = {}
            l_attribute_list [ BathyDbLib.IM_PROC_DATA_FILE_COL ] = l_processed_datafile
            l_attribute_list [ BathyDbLib.IM_POINTS_IN_MOD_COL ]  = l_nr_of_points
            if str(self.ParameterList[ BathyToolsLib.PARAMETER_RESAMPLE ]) == "T" :
                l_attribute_list [ BathyDbLib.IM_IM_FORMAT_DB ]  = BathyDbLib.IM_FRMT_SENS
                l_attribute_list [ BathyDbLib.IM_RESAMPLE_COL ]  = self.ParameterList[ BathyToolsLib.PARAMETER_RESAMPLE ]
                l_attribute_list [ BathyDbLib.IM_GRIDSIZE_COL ]  = l_gridsize_m
                l_attribute_list [ BathyDbLib.IM_NEIGHBOUR_COL ] = self.ParameterList[ BathyToolsLib.PARAMETER_NEIGHBOUR ]
            else :
                l_attribute_list [ BathyDbLib.IM_IM_FORMAT_DB ]  = l_im_format
                l_attribute_list [ BathyDbLib.IM_RESAMPLE_COL ]  = "F"
                l_attribute_list [ BathyDbLib.IM_GRIDSIZE_COL ]  = ""
                l_attribute_list [ BathyDbLib.IM_NEIGHBOUR_COL ] = ""
            if str(self.ParameterList[ BathyToolsLib.PARAMETER_INTERPOL ]) == "T" :
                l_attribute_list [ BathyDbLib.IM_INTERPOL_COL ]    = self.ParameterList[ BathyToolsLib.PARAMETER_INTERPOL ]
                l_attribute_list [ BathyDbLib.IM_POINTS_USED_COL ] = self.ParameterList[ BathyToolsLib.PARAMETER_POINTS_USED ]
                l_attribute_list [ BathyDbLib.IM_WEIGHT_FAC_COL ]  = self.ParameterList[ BathyToolsLib.PARAMETER_WEIGHT_FAC ]
                l_attribute_list [ BathyDbLib.IM_SEARCH_DIS_COL ]  = self.ParameterList[ BathyToolsLib.PARAMETER_SEARCH_DIS ]
                l_attribute_list [ BathyDbLib.IM_SMOOTH_FAC_COL ]  = self.ParameterList[ BathyToolsLib.PARAMETER_SMOOTH ]
                l_attribute_list [ BathyDbLib.IM_PP_SAMPLE_COL ]   = self.ParameterList[ BathyToolsLib.PARAMETER_PP_SAMPLE ]
            else :
                l_attribute_list [ BathyDbLib.IM_INTERPOL_COL ]    = "F"
                l_attribute_list [ BathyDbLib.IM_POINTS_USED_COL ] = ""
                l_attribute_list [ BathyDbLib.IM_WEIGHT_FAC_COL ]  = ""
                l_attribute_list [ BathyDbLib.IM_SEARCH_DIS_COL ]  = ""
                l_attribute_list [ BathyDbLib.IM_SMOOTH_FAC_COL ]  = ""

            self.DbConnection.set_obj_attributes ( BathyDbLib.IM_CLASS_ID, l_im_id, l_attribute_list )

            # Update workflowstep
            self.DbConnection.update_workflow_step ( self.ParameterList[ BathyToolsLib.PARAMETER_PROCESS_ID ], BathyDbLib.IM_CLASS_ID, l_im_id )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            os.sys.exit("Execution stopped")


class ImpImSql ( BathyProcessObject ) :

    def __init__(self, ParameterList):

        # Initialize class
        BathyProcessObject.__init__( self, ParameterList )

    def run ( self ) :

        # Start execution
        try:
            self.logger.info ('Start ' + DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] )

            # Start the importer
            BathyExecutablesLib.sens_sql_importer ( self.logger, self.ParameterList )

        except Exception, err:
            self.logger.critical( DB_PROCESS_DESC [ int(self.ParameterList[ BathyToolsLib.PROCESSID ]) ] + " failed:ERROR: %s\n" % str(err))
            os.sys.exit("Execution stopped")

#! /usr/bin/python

# standard library imports 
import os
import sys
import logging

# related third party imports

# local application/library specific imports
import BathyProcessesLib
import BathyExecutablesLib
import BathyToolsLib

__author__="Terlien"
__date__ ="$28-mei-2010 11:48:28$"

# Module name
MODULE_NAME = "BathyTools"

if __name__ == "__main__":

    try:

        # Read input parameters from command line
        try :
            task_id, parameter_file_name = BathyToolsLib.read_input_from_command_line(sys.argv)
        except Exception, err:
            raise

        # Parse XML
        try :
            ParameterValueList = BathyToolsLib.generate_parameter_value_list_from_file(parameter_file_name, task_id)
        except Exception, err:
            os.sys.exit("Execution stopped: ERROR: %s\n" % str(err))

        # Initialize logging to screen
        try :
            level_name = ParameterValueList[ BathyToolsLib.LOGLEVEL ]
            level = BathyToolsLib.LOGLEVELS.get(level_name, logging.NOTSET)
            logger = logging.getLogger(MODULE_NAME)
            logger.setLevel(level=level)
            stream_hdlr = logging.StreamHandler()
            #formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            stream_hdlr.setFormatter(formatter)
            logger.addHandler(stream_hdlr)
        except Exception, err:
            os.sys.exit("Initialize logging failed: ERROR: %s\n" % str(err))
            raise

        # Start logging to file
        try :
            #logfile = ParameterValueList[ BathyToolsLib.OUTPUTDIRECTORY ] + "\\" + ParameterValueList[ BathyToolsLib.OUTPUTFILE ] + BathyExecutablesLib.FILE_EXT_LOG
            file_name = ParameterValueList[ BathyToolsLib.OUTPUTFILE ]
            # Remove extention
            file_name_parts = file_name.rstrip().split(".")
            logfile_name = file_name_parts[0]
            logfile = ParameterValueList[ BathyToolsLib.TEMPDIR ] + "/" + logfile_name + BathyExecutablesLib.FILE_EXT_LOG
            logger.info("Start logging to file: " + logfile )
            logfile_hdlr = logging.FileHandler(logfile)
            logfile_hdlr.setLevel(level=level)
            logfile_hdlr.setFormatter(formatter)
            logger.addHandler(logfile_hdlr)
            logger.info("Logging to file " + logfile)
        except Exception, err:
            logger.critical("Starting logging to file failed: ERROR: %s\n" % str(err))
            raise
        
        # For EMODNET: Add personal layer import process ID
        ParameterValueList[ BathyToolsLib.PROCESSID ] = BathyProcessesLib.UPDATE_PERSONAL_LAYER 

        # Start process
        try :
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.ARCHIVE_IM) :
                BathyProcess = BathyProcessesLib.ArchiveIm( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.ARCHIVE_TRACKLINE) :
                BathyProcess = BathyProcessesLib.ArchiveTrackline( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.CREATE_PFM) :
                BathyProcess = BathyProcessesLib.PfmCreator( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.EXPORT_EMODNET_GRID) :
                BathyProcess = BathyProcessesLib.ExportEMODNETGrid( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.EXPORT_EMODNET_GRID_CM) :
                BathyProcess = BathyProcessesLib.ExportEMODNETGridCm( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.EXPORT_GEOTIFF_IM) :
                BathyProcess = BathyProcessesLib.ExportGeotiffIm ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.GENERATE_HULL) :
                BathyProcess = BathyProcessesLib.GenerateHull ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPORT_ESRI_ASCII_GRID) :
                BathyProcess = BathyProcessesLib.CreateBathyspaceEsriAsciiGrid ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPORT_ASCII_NO_ATTR) :
                BathyProcess = BathyProcessesLib.CreateBathyspaceAsciiNoAttr ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPORT_BAG) :
                BathyProcess = BathyProcessesLib.CreateBathyspaceBag ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPORT_ASCII_UNC_ATTR) :
                BathyProcess = BathyProcessesLib.CreateBathyspaceAsciiUncAttr ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPORT_PFM) :
                BathyProcess = BathyProcessesLib.CreateBathyspacePfm ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPORT_GML) :
                BathyProcess = BathyProcessesLib.CreateBathyspaceGml ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPORT_EMODNET) :
                BathyProcess = BathyProcessesLib.CreateBathyspaceEmodnet ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.ADD_TRACKLINE_TO_IM) :
                BathyProcess = BathyProcessesLib.AddTracklineToIm ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.CM_PROCESSING) :
                BathyProcess = BathyProcessesLib.ProcessCm ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.ACTIVATE_IM_IN_CM) :
                BathyProcess = BathyProcessesLib.ActivateImInCm ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.DEACTIVATE_IM_IN_CM) :
                BathyProcess = BathyProcessesLib.DeactivateImInCm ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPIM_ESRIASCIIGRID) :
                BathyProcess = BathyProcessesLib.ImpImESRIASCIIGRID ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.POSTPROCESS_IM) :
                BathyProcess = BathyProcessesLib.PostprocessIm ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPIM_ASCII) :
                BathyProcess = BathyProcessesLib.ImpImASCII ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.ADD_TRACKLINES_TO_IM) :
                BathyProcess = BathyProcessesLib.AddTracklinesToIm ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPIM_BAG) :
                BathyProcess = BathyProcessesLib.ImpImBAG ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPIM_GML) :
                BathyProcess = BathyProcessesLib.ImpImGML ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.GENERATE_PRODUCTS) :
                BathyProcess = BathyProcessesLib.GenerateProducts ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.EXP_ASCII_IM) :
                BathyProcess = BathyProcessesLib.ExportAsciiIm ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.EXPORT_SDFILE_IM) :
                BathyProcess = BathyProcessesLib.ExportSdFileIm ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPIM_DONAR) :
                BathyProcess = BathyProcessesLib.ImpImDONAR ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPIM_METADATACSV) :
                BathyProcess = BathyProcessesLib.ImpImMetadataCsv ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPIM_METADATAISOXML) :
                BathyProcess = BathyProcessesLib.ImpImMetadataIsoXml ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPIM_SQL) :
                BathyProcess = BathyProcessesLib.ImpImSql ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.IMPIM_SD) :
                BathyProcess = BathyProcessesLib.ImpImSd ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.SURFACE_DIFF_PROD) :
                BathyProcess = BathyProcessesLib.SurfaceDiffModelProd ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.SEP_MODEL_FILE_IMP) :
                BathyProcess = BathyProcessesLib.SepModelFileImp ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.SURFACE_DIFF_MODEL) :
                BathyProcess = BathyProcessesLib.SurfaceDifferenceModel ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.EXPORT_EMODNET_CM) :
                BathyProcess = BathyProcessesLib.ExportEMODNETGridCm ( ParameterValueList )
            if int(ParameterValueList [ BathyToolsLib.PROCESSID ]) == int(BathyProcessesLib.UPDATE_PERSONAL_LAYER) :
                BathyProcess = BathyProcessesLib.updatePersonalLayer ( ParameterValueList )                
            # Add process id to paramater XML
            BathyProcess.run()
            BathyProcess.commit_close()
        except Exception, err:
            os.sys.exit("Execution stopped")

        # Remove log handlers
        try:
            logger.info("Remove logging handlers")
            logger.removeHandler(logfile_hdlr)
            logger.removeHandler(stream_hdlr)
        except Exception, err:
            print "Removing logging handlers failed: ERROR: %s\n" % str(err)

    except Exception, err:
        os.sys.exit(1)
    else:
        os._exit(0)


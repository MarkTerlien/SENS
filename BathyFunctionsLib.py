#! /usr/bin/python

# standard library imports
import sys
import os
import logging
import xml.dom.minidom

# related third party imports

# local application/library specific imports
import BathyToolsLib
import BathyDbLib
import BathyExecutablesLib


__author__="Terlien"
__date__ ="$28-mei-2010 11:52:24$"

# Executables CMDOP IVS3D:
CREATECOVERAGEVECTORS = "cmdopbeta createcoveragevectors"
GENERATESDFILE        = "cmdop gridder"
ESRIASCIICONVERTER    = "cmdop gasciitoscalar"
ESRIBINCONVERTER      = "cmdop arctoscalar"
RESAMPLER             = "cmdop resampler"
UNLOADSDFILE          = "cmdop exportsurface"
BAGTOASCIICONVERTER   = "cmdop bagtoascii"
BAGTOSDCONVERTER      = "cmdop bagtoscalar"
PROJECTCREATE         = "cmdop projectcreate"


def cmdop_projectcreate ( DbConnection, logger, project, icoordsys) :
    """Function run run cmdop executable projectcreate"""
    try :
        logger.info("Running cmdop_projectcreate")
        command = PROJECTCREATE + " -project " + "\"" + str(project) + "\"" + " -icoordsys " + str(icoordsys)
        BathyExecutablesLib.cmdop_createproject ( logger, command )
    except Exception, err:
        logger.critical( "Running cmdop_projectcreate failed:ERROR: %s\n" % str(err))
        raise


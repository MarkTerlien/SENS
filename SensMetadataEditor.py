#! /usr/bin/python

""" Template function """

# standard library imports
import sys
import logging
import xml.dom.minidom

# related third party imports
import cx_Oracle
from easygui import *


__author__="Terlien"
__date__ ="$9-okt-2009 11:50:05$"
__copyright__ = "Copyright 2009, ATLIS"

# Module name
MODULE_NAME = "SensMetadataEditor"

# DB connect Parameters
DB_USER_SOURCE       = "DB_USER_SOURCE"
DB_PASSWORD_SOURCE   = "DB_PASSWORD_SOURCE"
DB_TNS_SOURCE        = "DB_TNS_SOURCE"

# Database connection parameter values
PARAMETER_LIST_VALUE = {}
PARAMETER_LIST_VALUE [ DB_USER_SOURCE ]     = "sens_portal"
PARAMETER_LIST_VALUE [ DB_PASSWORD_SOURCE ] = "SENS_PORTAL"
PARAMETER_LIST_VALUE [ DB_TNS_SOURCE ]      = "10.20.0.49/sens11"

# Menu options
MNU_ADD_ATTRIBUTE         = "ADD_ATTRIBUTE"
MNU_ADD_DOMAIN            = "S57_ADD_DOMAIN"
MNU_ADD_DOMAIN_VALUE      = "S57_ADD_DOMAIN_VALUE"
MNU_EXIT                  = "EXIT"

# Menu options dictionary
MENU_OPTIONS = {}
MENU_OPTIONS [ MNU_ADD_ATTRIBUTE ]    = "Add attribute"
MENU_OPTIONS [ MNU_ADD_DOMAIN  ]      = "Add domain"
MENU_OPTIONS [ MNU_ADD_DOMAIN_VALUE ] = "Add domain value"
MENU_OPTIONS [ MNU_EXIT ]             = "Exit"

# Attribute types that need special treatment
ENUMERATION = 1
LIST        = 2

# Object class types
USER_DOMAIN_OBJECT_CLASS = 172993

#####################################
# Classes
#####################################

# Database connection class
class DbConnectionClass:
    """Connection class to Oracle database"""
    def __init__(self, DbUser, DbPass, DbConnect, parent_module):
        try :
            self.logger = logging.getLogger( parent_module + '.DbConnection')
            self.logger.info("Setup database connection")
            self.oracle_connection       = cx_Oracle.connect(DbUser, DbPass, DbConnect)
            self.oracle_cursor           = self.oracle_connection.cursor()
            self.oracle_cursor.arraysize = 100000
            self.oracle_cursor.execute("select 'established' from dual")
        except Exception, err:
            self.logger.critical("Setup database connection failed: ERROR: " + str(err))
            raise

    def execute_query ( self, stmt ) :
        """Function toexecute query"""
        try :
            self.oracle_cursor = self.oracle_connection.cursor()
            return self.oracle_cursor.execute( stmt )
        except Exception, err:
            self.logger.critical("Execute query failed: ERROR: " + str(err))
            raise

    def add_attribute ( self, business_object_id, attribute_label, attribute_desc, attribute_type_id, attribute_source_id, attribute_group_id, is_unique, not_null, show_in_portal, domain_id ) :
        try:
            logger.info("Add attribute")

            # Create attribute
            attribute_name = attribute_label
            attribute_name.replace(' ','')
            parameters = [ None, business_object_id, attribute_name, attribute_label, None, attribute_desc, None, attribute_type_id, domain_id, None, None, None, attribute_group_id, attribute_source_id, is_unique, 9999, show_in_portal, not_null  ]
            self.oracle_cursor = self.oracle_connection.cursor()
            attribute_id = self.oracle_cursor.callfunc( "sdb_interface_pck.setObjectAttrDef", int, parameters )
            logger.info("Attribute " + str(attribute_name) + " with ID " + str(attribute_id) + " added")

        except Exception, err:
            self.logger.critical("Add attribute failed: ERROR: " + str(err))
            raise

    def add_domain ( self, domain_name ) :
        try:
            logger.info("Create domain")

            # Create domain
            domain_label = domain_name
            domain_name.replace(' ','')
            parameters = [ domain_name, domain_label, domain_label, USER_DOMAIN_OBJECT_CLASS ]
            self.oracle_cursor = self.oracle_connection.cursor()
            domain_id = self.oracle_cursor.callfunc( "sdb_interface_pck.createObjectTable", int, parameters )
            logger.info("Domain " + str(domain_name) + " with ID " + str(domain_id) + " created")

        except Exception, err:
            self.logger.critical("Create domain failed: ERROR: " + str(err))
            raise

    def add_domain_value ( self, user_domain_id, domain_value ) :
        try :
            logger.info("Add domain value")

            # Build DOM
            doc = xml.dom.minidom.Document()
            rowset = doc.createElement("ROWSET")
            doc.appendChild(rowset)
            row = doc.createElement("ROW")
            rowset.appendChild(row)

            # Add NAME attribute
            attribute = doc.createElement("NAME")
            row.appendChild(attribute)
            value = doc.createTextNode(str(domain_value))
            attribute.appendChild(value)

            # Get XML as string
            mut_xml = doc.toxml()

            # Execute insert
            self.oracle_cursor = self.oracle_connection.cursor()
            l_obj_id = self.oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [user_domain_id, 'I', mut_xml ])
            logger.info("Domain value " + str(domain_value) + " inserted; ID is " + str(int(l_obj_id)) )

        except Exception, err:
            self.logger.critical("Add domain value failed: ERROR: " + str(err))
            raise

    def commit ( self ) :
        self.oracle_connection.commit()

    def commit_close( self ) :
        """Function to commit and close connection"""
        self.oracle_connection.commit()
        self.oracle_connection.close()

#####################################
# Gui functions
#####################################

def gui_select_from_domain ( table_name, where_clause ) :
    try :
        logger.info("Select item from domain list")
        choice_list = []
        resultset = OracleConnection.execute_query( "select name from " + str(table_name) + " where " + str(where_clause)  )
        for row in resultset :
            choice_list.append ( str(row[0]) )
        ttl = "Domain Selection"
        msg = "Select from domain"
        name = choicebox(msg, ttl, choice_list)
        resultset = OracleConnection.execute_query( "select id from " + str(table_name) + " where name = \'" + str(name) + "\'" )
        for row in resultset :
            id = int(row[0])
        logger.info ( "Select attribute " + str(name) + " with ID " + str(id) )
        return id
    except Exception, err:
        logger.critical ( "Wizard add attribute failed: ERROR: %s\n" % str(err) )
        raise

def gui_start ( OracleConnection ) :
    while True :
        msg   = "What do you want?"
        options = [ MENU_OPTIONS [ MNU_ADD_ATTRIBUTE ],  MENU_OPTIONS [ MNU_ADD_DOMAIN ], MENU_OPTIONS [ MNU_ADD_DOMAIN_VALUE ], MENU_OPTIONS [ MNU_EXIT ] ]
        reply=buttonbox(msg,None,options)
        if reply == MENU_OPTIONS [ MNU_ADD_ATTRIBUTE ] :
            gui_wizard_add_attribute ( OracleConnection )
        if reply == MENU_OPTIONS [ MNU_ADD_DOMAIN  ] :
            gui_wizard_add_domain ( OracleConnection )
        elif reply == MENU_OPTIONS [ MNU_ADD_DOMAIN_VALUE ] :
            gui_wizard_add_domain_value ( OracleConnection )
        elif reply == MENU_OPTIONS [ MNU_EXIT ] :
            OracleConnection.commit_close()
            break

def gui_db_parameters() :
    title = 'Database connection parameters'
    msg   = "Give database connection parameters"
    field_names   = [ DB_TNS_SOURCE, DB_USER_SOURCE , DB_PASSWORD_SOURCE ]
    return_values = [ PARAMETER_LIST_VALUE [DB_TNS_SOURCE], PARAMETER_LIST_VALUE [DB_USER_SOURCE], PARAMETER_LIST_VALUE [DB_PASSWORD_SOURCE] ]
    return_values = multpasswordbox(msg, title, field_names, return_values)
    if return_values :
        PARAMETER_LIST_VALUE [DB_TNS_SOURCE]      = return_values[0]
        PARAMETER_LIST_VALUE [DB_USER_SOURCE]     = return_values[1]
        PARAMETER_LIST_VALUE [DB_PASSWORD_SOURCE] = return_values[2]

def gui_wizard_add_attribute ( OracleConnection ) :
    try :
        logger.info ("Start add attribute wizard")

        # Select business object
        business_object_id = gui_select_from_domain ( "sdb_object_class", "object_class_type = 172997" )

        # Now ask for attribute label and description
        ttl = "Attribute name and description"
        msg = "Give attribute name and description"
        field_names  = ["Attribute label", "Attribute description"]
        field_values = []
        field_values = multenterbox(msg, ttl, field_names)
        attribute_label = str(field_values[0])
        attribute_desc  = str(field_values[1])
        logger.info ( "Label new attribute:  " + attribute_label )
        logger.info ( "Description new attribute:  " + attribute_desc )

        # Select attribute type
        attribute_type_id = gui_select_from_domain ( "sdb_attributetype", "to_be_added_by_user = \'T\'" )

        # For attribute type is 1 (enumeration) or 2 (list) ask for domain
        if attribute_type_id == ENUMERATION or attribute_type_id == LIST :
            domain_id = gui_select_from_domain ( "sdb_object_class", "object_class_type in ( 173039, 173001, 172999,  172995, 172993 )" )
        else :
            domain_id           = None

        # Default values
        attribute_source_id = 4      # ATLIS
        attribute_group_id  = 239367 # Defined by organization
        is_unique           = 'F'
        not_null            = 'F'
        show_in_portal      = 'F'

        # Add attribute
        OracleConnection.add_attribute ( business_object_id, attribute_label, attribute_desc, attribute_type_id, attribute_source_id, attribute_group_id, is_unique, not_null, show_in_portal, domain_id )
        
        # Commit
        OracleConnection.commit()

    except Exception, err:
        logger.critical ( "Wizard add attribute failed: ERROR: %s\n" % str(err) )
        raise

def gui_wizard_add_domain ( OracleConnection ) :
    try :
        logger.info ("Start add domain wizard")

        # Now ask for domain name
        ttl = "Domain name"
        msg = "Give domain name"
        field_names  = ["Domain name"]
        field_values = []
        field_values = multenterbox(msg, ttl, field_names)
        domain_name = str(field_values[0])
        logger.info ( "Name of new domain:  " + domain_name )

        # Create domain
        OracleConnection.add_domain ( domain_name )

        # Commit
        OracleConnection.commit()

    except Exception, err:
        logger.critical ( "Wizard add domai failed: ERROR: %s\n" % str(err) )
        raise

def gui_wizard_add_domain_value ( OracleConnection ) :
    try :
        logger.info ("Start add domain value wizard")

        # Get list of user domain
        user_domain_id = gui_select_from_domain ( "sdb_object_class", "object_class_type = " + str(USER_DOMAIN_OBJECT_CLASS) )
        logger.info ("Add enrty to user domain " + str(user_domain_id) )

        # Now ask for domain name
        ttl = "Domain value"
        msg = "Give domain value"
        field_names  = ["Domain value"]
        field_values = []
        field_values = multenterbox(msg, ttl, field_names)
        domain_value = str(field_values[0])
        logger.info ( "Name of new domain value:  " + domain_value )

        # Insert domain value
        OracleConnection.add_domain_value ( user_domain_id, domain_value )

        # Commit
        OracleConnection.commit()

    except Exception, err:
        logger.critical ( "Wizard add domain value failed: ERROR: %s\n" % str(err) )
        raise

#####################################
# Main
#####################################

if __name__ == "__main__":
    try:
        try :

            # Initialize logger
            logger = logging.getLogger(MODULE_NAME)
            logger.setLevel(logging.DEBUG)
            stream_hdlr = logging.StreamHandler()
            formatter   = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            stream_hdlr.setFormatter(formatter)
            logger.addHandler(stream_hdlr)

            # Get database parameters
            gui_db_parameters()

            # Open database connection
            OracleConnection = DbConnectionClass ( PARAMETER_LIST_VALUE[ DB_USER_SOURCE ], PARAMETER_LIST_VALUE[ DB_PASSWORD_SOURCE ], PARAMETER_LIST_VALUE[ DB_TNS_SOURCE ], MODULE_NAME )

            # Start GUI
            gui_start ( OracleConnection )

        except Exception, err:
            logger.critical ( "Application failed: ERROR: %s\n" % str(err) )
            raise
    except Exception, err:
        print "Starting logger failed: ERROR: %s\n" % str(err)
        sys.exit(1)
    else:
        sys.exit(0)

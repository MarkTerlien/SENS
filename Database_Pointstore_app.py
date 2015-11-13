#! /usr/bin/python

""" Function to import survey into database
"""

# Standard library imports
import os
import sys
import struct
import logging
import time
import xml.dom.minidom

# Related third party imports
import cx_Oracle
from easygui import *

# Module name
MODULE_NAME = "Database_Pointstore"

# Logging levels
LOG_LEVEL = 'info'
LOGLEVELS = {'debug'   : logging.DEBUG,
             'info'    : logging.INFO,
             'warning' : logging.WARNING,
             'error'   : logging.ERROR,
             'critical': logging.CRITICAL}

# DB connect Parameters
DB_USER_SOURCE       = "DB_USER_SOURCE"
DB_PASSWORD_SOURCE   = "DB_PASSWORD_SOURCE"
DB_TNS_SOURCE        = "DB_TNS_SOURCE"

# Other parameters
CHOICE        = "CHOICE"
GRID_FILE     = "GRID_FILE"
POINT_FILE    = "POINT_FILE"
DATA_FILE     = "DATA_FILE"
OUTPUT_CHOICE = "OUTPUT_CHOICE"
OUTPUT_DIR    = "OUTPUT_DIR"
OUTPUT_FILE   = "OUTPUT_FILE"
IM_ID         = "IM_ID"
START_ROW     = "Start row grid"
END_ROW       = "End row grid"
START_COL     = "Start column grid"
END_COL       = "End column grid"
NUMBER        = "Number of depths"

# Possible choices
CREATE   = "Create"
RETRIEVE = "Retrieve"
CONVERT  = "Convert"

# Possible output choices
GRIDCELLS_FROM_DB         = "GRIDCELLS_FROM_DB"
POINTS_FROM_DB_AS_RECORDS = "POINTS_FROM_DB_AS_RECORDS"
POINTS_FROM_DB_AS_STRINGS = "POINTS_FROM_DB_AS_STRINGS"
POINTS_FROM_CLIENT_BLOBS  = "POINTS_FROM_CLIENT_BLOBS"

# Database connection parameter values
PARAMETER_LIST_VALUE = {}
PARAMETER_LIST_VALUE [ DB_USER_SOURCE ]     = "sens"
PARAMETER_LIST_VALUE [ DB_PASSWORD_SOURCE ] = "senso"
PARAMETER_LIST_VALUE [ DB_TNS_SOURCE ]      = "10.20.0.49/sens11"
#PARAMETER_LIST_VALUE [ DB_USER_SOURCE ]     = "mtj"
#PARAMETER_LIST_VALUE [ DB_PASSWORD_SOURCE ] = "mtj"
#PARAMETER_LIST_VALUE [ DB_TNS_SOURCE ]      = "localhost/mtj"
PARAMETER_LIST_VALUE [ CHOICE ]              = CREATE
PARAMETER_LIST_VALUE [ GRID_FILE ]           = 'D:/Geodata/USA/Bathymetry/Portsmouth/SENS_GRID_small.xyz'
PARAMETER_LIST_VALUE [ POINT_FILE ]          = 'D:/Geodata/USA/Bathymetry/Portsmouth/H00741B.bin'
PARAMETER_LIST_VALUE [ DATA_FILE ]           = 'C:/Documents and Settings/terlien/Bureaublad/PS/H11014.xyz'
PARAMETER_LIST_VALUE [ IM_ID ]               = 2
PARAMETER_LIST_VALUE [ START_COL ]           = 0
PARAMETER_LIST_VALUE [ END_COL ]             = 77
PARAMETER_LIST_VALUE [ START_ROW ]           = 0
PARAMETER_LIST_VALUE [ END_ROW ]             = 113
PARAMETER_LIST_VALUE [ NUMBER ]              = 100000000
PARAMETER_LIST_VALUE [ OUTPUT_DIR ]          = 'D:/Geodata/USA/Bathymetry/Portsmouth'
PARAMETER_LIST_VALUE [ OUTPUT_CHOICE ]       = GRIDCELLS_FROM_DB
PARAMETER_LIST_VALUE [ OUTPUT_FILE ]         = 'DatabasePoinstore.xyz'

#########################################
# GUI functions
#########################################

def gui_start () :
    logger.info("Start GUI")
    while True :
        gui_choices()
        if PARAMETER_LIST_VALUE [ CHOICE ] == CREATE :
            gui_create()
        if PARAMETER_LIST_VALUE [ CHOICE ] == RETRIEVE :
            gui_retrieve()
        if PARAMETER_LIST_VALUE [ CHOICE ] == CONVERT :
            gui_convert()
        msg   = "Do you want to continue?"
        title = "Database Pointstore"
        if ccbox(msg, title):     # show a Continue/Cancel dialog
            gui_start ()  # user chose Continue
        else:  # user chose Cancel
            sys.exit(0)

def gui_open_db_connection () :
    logger.info("Open database connection GUI")
    title = 'Database connection parameters'
    msg   = "Enter database connection parameters "
    field_names   = [ DB_TNS_SOURCE, DB_USER_SOURCE , DB_PASSWORD_SOURCE ]
    return_values = [ PARAMETER_LIST_VALUE [DB_TNS_SOURCE], PARAMETER_LIST_VALUE [DB_USER_SOURCE], PARAMETER_LIST_VALUE[DB_PASSWORD_SOURCE] ]
    return_values = multpasswordbox( msg,title, field_names, return_values)
    if return_values :
        PARAMETER_LIST_VALUE [DB_TNS_SOURCE]      = return_values[0]
        PARAMETER_LIST_VALUE [DB_USER_SOURCE]     = return_values[1]
        PARAMETER_LIST_VALUE [DB_PASSWORD_SOURCE] = return_values[2]
    logger.info("Open database connection")
    oracle_connection = cx_Oracle.connect(PARAMETER_LIST_VALUE [DB_USER_SOURCE], PARAMETER_LIST_VALUE [DB_PASSWORD_SOURCE], PARAMETER_LIST_VALUE [DB_TNS_SOURCE])
    oracle_cursor     = oracle_connection.cursor()
    return oracle_connection, oracle_cursor

def gui_choices () :

    # Select what you want to do
    logger.info("Selection of point store action")
    msg     = "What do you want to do?"
    title   = "Database Pointstore selection"
    choices = [ CREATE, RETRIEVE, CONVERT ]
    choice  = buttonbox(msg, title,choices)
    if choice == CREATE :
        PARAMETER_LIST_VALUE [ CHOICE ] = CREATE
    if choice == RETRIEVE :
        PARAMETER_LIST_VALUE [ CHOICE ] = RETRIEVE
    if choice == CONVERT :
        PARAMETER_LIST_VALUE [ CHOICE ] = CONVERT


def gui_convert () :

    # Convert ascii file to binary file
    add_attributes = False
    #  Read ascii file and write binary file
    title        = 'Inputfile selection'
    msg          = 'Select inputfile'
    nr_lines     = 0
    input_file   = PARAMETER_LIST_VALUE [ DATA_FILE ]
    input_file   = fileopenbox(msg, title, input_file)
    output_dir   = os.path.dirname( input_file )
    output_file  = os.path.basename( input_file ).split(".")[0] + str("_double.bin")
    asc_file_out = os.path.basename( input_file ).split(".")[0] + str("_double.asc")
    logger.info("Output file : " + str(output_dir)  )
    logger.info("Output dir  : " + str(output_file) )
    os.chdir(output_dir)
    # Write binary file
    logger.info("Write binary file")
    fIn  = open( input_file , 'r')
    fOut = open( output_file, 'wb')
    for line in fIn :
        nr_lines = nr_lines + 1
        line_items = line.rstrip().split()
        for i in range (0,len(line_items)) :
            if nr_lines < 10 :
                logger.info("Position " + str(i) + " value " + str(line_items[i]))
            if i == 0 : 
                # x
                data = struct.pack('d', float(line_items[i]))
            if i == 1 :
                # y
                data = struct.pack('d', float(line_items[i]))
            if i == 2 :
                # z
                data = struct.pack('d', float(line_items[i]))
            fOut.write(data)
        if add_attributes :
            # ADD INTEGER
            integer_value = int(99)
            data = struct.pack('i', integer_value)
            fOut.write(data)
            # ADD STRING
            string_value = "test"
            data = struct.pack('4s', string_value)
            fOut.write(data)
    logger.info( str(nr_lines) + " lines written to file")
    fIn.close()
    fOut.close()

    # Write ascii file
    nr_lines     = 0
    fIn  = open( output_file , 'rb')
    fOut = open( asc_file_out, 'w')
    logger.info("Read binary file and write ascii file")
    while True:
        if add_attributes :
            bytes_read = fIn.read(struct.calcsize("<fffi4s"))
        else :
            bytes_read = fIn.read(struct.calcsize("<ddf"))
        #logger.info(str(bytes_read))
        if not bytes_read:
            break
        try :
            if add_attributes :
                data = struct.unpack("<fffi4s", bytes_read)
            else :
                data = struct.unpack("<ddf", bytes_read)
        except :
            logger.info("Error reading bytes")
        fOut.write( str(data) + "\n" )
        nr_lines = nr_lines + 1
    logger.info( str(nr_lines) + " read from file")
    fIn.close()
    fOut.close()


def gui_create () :

    # Parameters for creating a point store
    oracle_connection, oracle_cursor  = gui_open_db_connection ()
    logger.info("Parameters for creating a point store")
    title        = 'Inputfile selection'
    msg          = 'Select grid file'
    PARAMETER_LIST_VALUE [ GRID_FILE ]    = 'C:/Documents and Settings/terlien/Bureaublad/PS/SENS_GRID_even_smaller.xyz'
    PARAMETER_LIST_VALUE [ GRID_FILE ]    = fileopenbox(msg, title, PARAMETER_LIST_VALUE [ GRID_FILE ])
    # Workaround bug opening two file open boxes
    msg   = "Do you want to continue?"
    title = "Database Pointstore"
    if ccbox(msg, title):
        pass
    else :
        pass
    title        = 'Inputfile selection'
    msg          = 'Select point file'
    PARAMETER_LIST_VALUE [ POINT_FILE ]   = 'C:/Documents and Settings/terlien/Bureaublad/PS/H11014_double.bin'
    PARAMETER_LIST_VALUE [ POINT_FILE ] = fileopenbox(msg, title, PARAMETER_LIST_VALUE [ POINT_FILE ])

    # Get new IM_ID
    stmt  = "select max(instance_id) from sdb_pointstore"
    oracle_cursor.arraysize = 10
    oracle_cursor.execute(stmt)
    resultset = oracle_cursor.fetchmany()
    if resultset :
        for row in resultset :
            if row[0] :
                PARAMETER_LIST_VALUE [ IM_ID ] = int(row[0]) + 1
            else :
                PARAMETER_LIST_VALUE [ IM_ID ] = 2
    PARAMETER_LIST_VALUE [ IM_ID ] = 13

    # Delete entry
    stmt = 'delete from sdb_pointstore_info where instanceid = :1'
    oracle_cursor.execute(stmt, ( PARAMETER_LIST_VALUE [ IM_ID ], ) )

    # Now insert ps metadata
#    print "Insert metadataformat"
#    ps_im_format_id  = 70530
#    ps_info_class_id = 771
#    # Delete entry
#    stmt = 'delete from sdb_pointstore_info where instanceid = :1'
#    oracle_cursor.execute(stmt, ( PARAMETER_LIST_VALUE [ IM_ID ], ) )
#    # Add entry
#    doc = xml.dom.minidom.Document()
#    rowset = doc.createElement("ROWSET")
#    doc.appendChild(rowset)
#    row = doc.createElement("ROW")
#    rowset.appendChild(row)
#    attribute = doc.createElement("INSTANCEID")
#    row.appendChild(attribute)
#    value = doc.createTextNode(str(PARAMETER_LIST_VALUE [ IM_ID ]))
#    attribute.appendChild(value)
#    attribute = doc.createElement("POINTSTOREFORMAT")
#    row.appendChild(attribute)
#    value = doc.createTextNode(str(ps_im_format_id))
#    attribute.appendChild(value)
#    mut_xml = doc.toxml()
#    obj_id = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ps_info_class_id, 'I', mut_xml ])

    # Start import
    import_report = import_grid ( oracle_cursor, oracle_connection )

    # Print report
    textbox("Import report ", "Show import report", import_report)

    msg   = "Do you want to continue?"
    title = "Database Pointstore"
    if ccbox(msg, title):     # show a Continue/Cancel dialog
        gui_start ()  # user chose Continue
    else:  # user chose Cancel
        sys.exit(0)


def gui_retrieve () :

    # Parameters for retrieving data from a point store
    oracle_connection, oracle_cursor  = gui_open_db_connection ()
    logger.info("Parameters for retrieving data from a point store")

    # Popup IM select box
    im_list = []
    stmt  = "select distinct(instance_id) from sdb_pointstore"
    oracle_cursor.arraysize = 10000
    oracle_cursor.execute(stmt)
    resultset = oracle_cursor.fetchmany()
    if resultset :
        for row in resultset :
            im_list.append(str(row[0]))
    msg     = "Select individual model"
    title   = "Individual model"
    PARAMETER_LIST_VALUE [ IM_ID ] = choicebox(msg, title, im_list)

    # Select output directory
    title        = 'Output directory selection'
    msg          = 'Select output directory'
    PARAMETER_LIST_VALUE [ OUTPUT_DIR ] = diropenbox(msg, title, str(PARAMETER_LIST_VALUE [ OUTPUT_DIR ]) )
    output_file  = PARAMETER_LIST_VALUE [ OUTPUT_DIR ]  + "/" + PARAMETER_LIST_VALUE [ OUTPUT_FILE ]

    # Select what to retrieve
    msg     = "What do you want to retrieve?"
    title   = "Database Pointstore selection"
    choices = [ GRIDCELLS_FROM_DB, POINTS_FROM_DB_AS_RECORDS, POINTS_FROM_DB_AS_STRINGS, POINTS_FROM_CLIENT_BLOBS ]
    PARAMETER_LIST_VALUE [ OUTPUT_CHOICE ] = buttonbox(msg, title, choices)

    # Define spatial query
    msg     = "Define spatial query"
    title   = "Spatial query defintion"
    parameter_names  = [ START_COL, END_COL, START_ROW, END_ROW, NUMBER ]
    parameter_values = [ PARAMETER_LIST_VALUE[START_COL],PARAMETER_LIST_VALUE[END_COL], PARAMETER_LIST_VALUE[START_ROW], PARAMETER_LIST_VALUE[END_ROW] ,PARAMETER_LIST_VALUE [NUMBER] ]
    [ PARAMETER_LIST_VALUE[START_COL],PARAMETER_LIST_VALUE[END_COL], PARAMETER_LIST_VALUE[START_ROW], PARAMETER_LIST_VALUE[END_ROW], PARAMETER_LIST_VALUE [NUMBER] ] = multenterbox(msg, title, parameter_names, parameter_values)

    # Init
    nr_depths        = 0
    nr_output_lines  = 10
    output_lines     = ''
    nr_blob_lines    = 0
    #row_bytes_length = struct.calcsize("<fff")

    # Get list of IDs from database
    if PARAMETER_LIST_VALUE [ OUTPUT_CHOICE ] == POINTS_FROM_CLIENT_BLOBS :

        # Decide to write ascii file (to check) or not
        #write_ascii_file = True
        #parse_xyz        = False

        # First write to binary file and then read binary file and write to ascii file
        logger.info("Retrieve depths as BLOB and write to binary file")
        output_file_bin = os.path.dirname( output_file ) + "/" + os.path.basename( output_file ).split(".")[0] + str(".bin")
        stmt = 'select bucket from sdb_pointstore where instance_id = :1 and col_nr >= :2 and col_nr <= :3 and row_nr >= :4 and row_nr <= :5 and rownum <= :6'
        oracle_cursor.execute(stmt, ( PARAMETER_LIST_VALUE[IM_ID], PARAMETER_LIST_VALUE[START_COL],PARAMETER_LIST_VALUE[END_COL], PARAMETER_LIST_VALUE[START_ROW], PARAMETER_LIST_VALUE[END_ROW], PARAMETER_LIST_VALUE [NUMBER] ) )
        fOut   = open( output_file_bin, 'wb')
        start_retrieval = time.clock()

        # First read from DB and write to binary file
        start_retrieval = time.clock()
        fOut   = open( output_file_bin, 'wb')
        while True :
            resultset = oracle_cursor.fetchmany()
            if not resultset :
                break
            else :
                for row in resultset :
                    fOut.write( row[0].read() )
                    nr_blob_lines = nr_blob_lines + 1
        fOut.close()
        duration = str(round(time.clock() - start_retrieval,2))
        logger.info ( str(nr_blob_lines) + " BLOBs wrote to binary file in " + str(duration) + " seconds")

        # Now read from binary file and write to ascii file
        start_retrieval = time.clock()
        fIn  = open( output_file_bin, 'rb')
        fOut = open( output_file, 'w')
        while True :
            bytes_read = fIn.read(struct.calcsize("<fff"))
            if not bytes_read:
                break
            try :
                data = struct.unpack("<fff", bytes_read)
                line = str(data[0]) + " " + str(data[1]) + " " + str(data[2]) + "\n"
                fOut.write(line)
                nr_depths = nr_depths + 1
                if nr_depths % 100000 == 0 :
                    logger.info( str(nr_depths) + " read" )
            except :
                logger.info("Error reading bytes")
        logger.info( str(nr_depths) + " read" )
        fIn.close()
        fOut.close()
        duration = str(round(time.clock() - start_retrieval,2))
        logger.info ( str(nr_depths) + " parsed from binary file and written to ascii file in " + str(duration) + " seconds")

#                    depth_data = row[0].read()
#                    # Parse xyz
#                    offset     = 1
#                    while parse_xyz :
#                        # Following statement is very slow!!
#                        bytes_read = row[0].read(offset, row_bytes_length)
#                        if not bytes_read :
#                            break
#                        try :
#                            #data = struct.unpack("<fff", bytes_read)
#                            #x    = float(data[0])
#                            #y    = float(data[1])
#                            #z    = float(data[2])
#                            nr_depths  = nr_depths + 1
#                            if nr_depths % 1000 == 0 :
#                                logger.info( str(nr_depths) + " processed" )
#                            #if nr_depths <= nr_output_lines :
#                            #    output_lines = output_lines + str(x) + " " + str(y) + " " + str(z) + "\n"
#                        except :
#                            logger.info("Error reading bytes")
#                        offset     = offset + row_bytes_length
#                    fOut.write( depth_data )
#                    fOut.write( row[0].read() )
#                    nr_blob_lines = nr_blob_lines + 1
#        fOut.close()
#        duration = str(round(time.clock() - start_retrieval,2))
#        logger.info ( str(nr_blob_lines) + " BLOBs wrote to binary file in " + str(duration) + " seconds")
#
#
#        # New read from binary file and write to ascii file
#        if write_ascii_file :
#            logger.info("Count and parse depths")
#            fIn  = open( output_file_bin, 'rb')
#            #fOut = open( output_file, 'w')
#            while True :
#                bytes_read = fIn.read(struct.calcsize("<fff"))
#                if not bytes_read:
#                    break
#                try :
#                    data = struct.unpack("<fff", bytes_read)
#                    line = str(data[0]) + " " + str(data[1]) + " " + str(data[2]) + "\n"
#                    fOut.write(line)
#                    nr_depths = nr_depths + 1
#                    if nr_depths <= nr_output_lines :
#                        output_lines = output_lines + line
#                except :
#                    logger.info("Error reading bytes")
#            fIn.close()
#            duration = str(round(time.clock() - start_retrieval,2))
#            logger.info ( str(nr_depths) + " parsed from binary file in " + str(duration) + " seconds")
#            fOut.close()

    else :
        if PARAMETER_LIST_VALUE [ OUTPUT_CHOICE ] == GRIDCELLS_FROM_DB :
            logger.info("Retrieve gridcells")
            stmt = 'select row_nr, col_nr, z_avg from sdb_pointstore where instance_id = :1 and col_nr >= :2 and col_nr <= :3 and row_nr >= :4 and row_nr <= :5 and rownum <= :6 '
            # Random sample of 10%
            # stmt = 'select row_nr, col_nr, depth_avg from mtj_ps_gridcells sample block(10) where im_id = :1 and col_nr >= :4 and col_nr <= :5 and row_nr >= :2 and row_nr <= :3 and rownum <= :6 '
        if PARAMETER_LIST_VALUE [ OUTPUT_CHOICE ] == POINTS_FROM_DB_AS_RECORDS :
            logger.info("Retrieve depths as records")
            stmt = 'select x, y, z from table ( sdb_pointstore_pck.readDepthsAsRecord ( :1, :2, :3, :4, :5, :6 ) )'
        if PARAMETER_LIST_VALUE [ OUTPUT_CHOICE ] == POINTS_FROM_DB_AS_STRINGS :
            logger.info("Retrieve depths as strings")
            stmt = 'select depth_string, \'\', \'\' from table ( sdb_pointstore_pck.readDepthsAsString  ( :1, :2, :3, :4, :5, :6, \' \' ) )'

        oracle_cursor.arraysize = 100000
        oracle_cursor.execute( stmt, ( PARAMETER_LIST_VALUE[IM_ID], PARAMETER_LIST_VALUE[START_COL],PARAMETER_LIST_VALUE[END_COL], PARAMETER_LIST_VALUE[START_ROW], PARAMETER_LIST_VALUE[END_ROW], PARAMETER_LIST_VALUE [NUMBER] ) )
        fOut = open( output_file, 'w')
        start_retrieval = time.clock()
        while True :
            resultset = oracle_cursor.fetchmany()
            if not resultset :
                break
            else :
                for row in resultset :
                    nr_depths = nr_depths + 1
                    line = str(row[0]) + " " + str(row[1]) + " " + str(row[2]) + "\n"
                    fOut.write(line)
                    if nr_depths <= nr_output_lines :
                        output_lines = output_lines + line
                logger.info( str(nr_depths) + " retrieved")
        fOut.close()
        duration = str(round(time.clock() - start_retrieval,2))

    # Log output text and first rows of file
    output_text = "\n"
    output_text = output_text +  "Summary retrieval of " + str(PARAMETER_LIST_VALUE [ OUTPUT_CHOICE ]) + "\n"
    output_text = output_text +  "--------------------------------------------------------\n"
    output_text = output_text +  "\n"
    output_text = output_text + str(nr_depths) + " depths retrieved in  " + duration + " seconds" + "\n"
    output_text = output_text + "\n"
    output_text = output_text + "Preview output file " + str( output_file ) + "\n"
    output_text = output_text +  "--------------------------------------------------------\n"
    output_text = output_text + "\n"
    output_text = output_text + output_lines
    textbox("Retrieval report ", "Show retrieval report", output_text)

    msg   = "Do you want to continue?"
    title = "Database Pointstore"
    if ccbox(msg, title):     # show a Continue/Cancel dialog
        oracle_cursor.close()
        oracle_connection.commit()
        oracle_connection.close()
        gui_start ()  # user chose Continue
    else:  # user chose Cancel
        oracle_cursor.close()
        oracle_connection.commit()
        oracle_connection.close()
        sys.exit(0)


def import_grid ( oracle_cursor, oracle_connection ) :

    try :

        # Function to import grid and depths into database
        logger.info("Start import grid as IM " + str(PARAMETER_LIST_VALUE [ IM_ID ]) )

        grid_file  = PARAMETER_LIST_VALUE [ GRID_FILE ]
        point_file = PARAMETER_LIST_VALUE [ POINT_FILE ]

        # ID of IM to load grid for
        im_id = PARAMETER_LIST_VALUE [ IM_ID ]

        # Get tmp table names from database
        grid_table  = oracle_cursor.var(cx_Oracle.STRING)
        point_table = oracle_cursor.var(cx_Oracle.STRING)

        # Store significant points
        store_significant_points = 'T'

        # Create tmp tables in database
        ps_name   = "MTJ Pointstore"
        ps_format = 70530
        coord_sys = 105044
        ver_dat   = 86

        session_id = oracle_cursor.callfunc('sdb_pointstore_pck.startCreatePointstore', int, [im_id, ps_name, ps_format, coord_sys, ver_dat, 0, 0, 0, 0, 0, 0, store_significant_points, grid_table, point_table, "F"])
        logger.info("Insert in grid table  is " + str(grid_table.getvalue())  )

        # Now restart the oracle connect to get grants on table
        logger.info("Restart Oracle connection")
        oracle_cursor.close()
        oracle_connection.commit()
        oracle_connection.close()
        oracle_connection = cx_Oracle.connect(PARAMETER_LIST_VALUE [DB_USER_SOURCE], PARAMETER_LIST_VALUE [DB_PASSWORD_SOURCE], PARAMETER_LIST_VALUE [DB_TNS_SOURCE])
        oracle_cursor     = oracle_connection.cursor()

        # Count number of lines in gridfile
        logger.info("Count number of gridcells in file")
        fIn = open(grid_file,'r')
        nr_of_lines = 0
        for line in fIn :
            nr_of_lines = nr_of_lines + 1
        fIn.close()
        logger.info(str(nr_of_lines) + " gridcells in file")

        # Count number of points in binary file
        logger.info("Count number of points in file")
        fIn = open(point_file,'rb')
        nr_of_points = 0
        while True:
            bytes_read = fIn.read(struct.calcsize("<ddd"))
            nr_of_points = nr_of_points + 1
            if not bytes_read:
                break
        fIn.close()
        nr_of_points = int(nr_of_points) * int(nr_of_lines)
        logger.info(str(nr_of_points) + " points in file")

        # Store grids in database
        logger.info("Start storing depths in database")
        start_retrieval = time.clock()
        i           = 0
        nr_depths   = 1
        blobdata    = oracle_cursor.var(cx_Oracle.BLOB)
        stmt_b      = str(grid_table.getvalue())
        stmt_p      = str(point_table.getvalue())
        print stmt_b
        print stmt_p
        blobdata.setvalue(0, open(point_file, 'rb').read() )
        fIn         = open(grid_file, 'r')
        for line in fIn:
            i = i + 1
            oracle_cursor.execute( stmt_b, ( im_id, int(line.split()[0]), int(line.split()[1]), float(line.split()[2]), float(line.split()[2]), float(line.split()[2]), nr_depths,  blobdata ) )
            if i % 10000 == 0 or i == nr_of_lines:
                logger.info(str(i) + " gridcells written to database")
        fIn.close()
        grid_duration = str(round(time.clock() - start_retrieval,2))
        logger.info("Gridcells and points inserted in " + str(grid_duration) + " seconds")

        # Create indexes and add partitions to tables
        logger.info("Create indexes and add partitions to tables")
        start_retrieval = time.clock()
        oracle_cursor.callproc('sdb_pointstore_pck.commitCreatePointstore ',[im_id, session_id])
        index_duration = str(round(time.clock() - start_retrieval,0))
        logger.info("Indexes created in " + str(index_duration) + " seconds")

        # Log output text and first rows of file
        output_text = "\n"
        output_text = output_text +  "Summary import of gridfile " + str(PARAMETER_LIST_VALUE [ GRID_FILE ]) + "\n"
        output_text = output_text +  "Summary import of pointfile " + str(PARAMETER_LIST_VALUE [ POINT_FILE ]) + "\n"
        output_text = output_text +  "--------------------------------------------------------\n"
        output_text = output_text +  "\n"
        output_text = output_text + str(nr_of_lines)  + " gridcells imported in  " + grid_duration + " seconds" + "\n"
        output_text = output_text + str(nr_of_points) + " points imported in  "    + grid_duration + " seconds" + "\n"
        output_text = output_text +  "\n"
        output_text = output_text + " Indexes created in  " + index_duration + " seconds" + "\n"
        output_text = output_text + "\n"
        output_text = output_text +  "--------------------------------------------------------\n"
        output_text = output_text + "\n"
        output_text = output_text + "Instance ID = " + str(PARAMETER_LIST_VALUE [ IM_ID ])

        # Close Oracle connection
        oracle_cursor.close()
        oracle_connection.commit()
        oracle_connection.close()

        return output_text

    except Exception, err :
        sys.exit(err)

####################################
# Start main program
####################################

if __name__ == "__main__":

    # Initialize logger
    logger      = logging.getLogger(MODULE_NAME)
    level       = LOGLEVELS.get(LOG_LEVEL, logging.NOTSET)
    logger.setLevel( level )
    stream_hdlr = logging.StreamHandler()
    formatter   = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_hdlr.setFormatter(formatter)
    logger.addHandler(stream_hdlr)

    # Start gui
    gui_start ()
    

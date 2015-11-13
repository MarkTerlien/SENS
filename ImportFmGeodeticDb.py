#! /usr/bin/python

""" Template function """

# standard library imports
import cx_Oracle
import xml.dom.minidom
import string

__author__="Terlien"
__date__ ="$9-okt-2009 11:50:05$"
__copyright__ = "Copyright 2009, ATLIS"

ELLIPSOID_IN             = "D:\\SensSVN\\BathyToolsV2\\BatchFiles\\ellipsoide.txt"
HORIZONTAL_DATUM_IN      = "D:\\SensSVN\\BathyToolsV2\\BatchFiles\\fm_datums.txt"
HORIZONTAL_PARAMETERS_IN = "D:\\SensSVN\\BathyToolsV2\\BatchFiles\\fm_coords.txt"
#WKT_RECORDS_IN           = "D:\\SensSVN\\BathyToolsV2\\BatchFiles\\fm_coords_wkt.txt"
#FORMATTED_WKT_RECORDS_IN = "D:\\SensSVN\\BathyToolsV2\\BatchFiles\\fm_coords_formatted.txt"
#HORIZONTAL_PARAMETERS_IN = "D:\\SensSVN\\BathyToolsV2\\BatchFiles\\3994.txt"
WKT_RECORDS_IN           = "D:\\SensSVN\\BathyToolsV2\\BatchFiles\\3994_wkt.txt"
FORMATTED_WKT_RECORDS_IN = "D:\\SensSVN\\BathyToolsV2\\BatchFiles\\3994_formatted.txt"

MISSING_PARAMETERS_IN    = "D:\\SensSVN\\BathyToolsV2\\BatchFiles\\fm_coords_20101223.txt"

IMPORT_ELLIPSOID             = False
IMPORT_HORIZONTAL_DATUM      = False
IMPORT_HORIZONTAL_PARAMETERS = False
IMPORT_WKT_RECORDS           = False
IMPORT_FORMATTED_WKT_RECORDS = False
LINK_COUNTRIES               = False
IMPORT_PROJECTION_UNITS      = False
UPDATE_PROJECTION_UNITS      = False
UPDATE_MISSING_PARAMETERS    = False
UPDATE_GEOCS                 = False
INSERT_NEW_GEOCS             = False
IMPORT_EPSG_CODES            = True

COORD_SYS_CLASS_ID        = "587"
GEODETIC_PARAM_CLASS_ID   = "594"
PROJECTION_FROM_CLASS_ID  = "593"
CONTINENT_CLASS_ID        = "590"
COUNTY_CLASS_ID           = "591"
HEMISPHERE_CLASS_ID       = "595"
HORIZONTAL_DATUM_CLASS_ID = "589"
ELLIPSOID_CLASS_ID        = "588"
STATE_CLASS_ID            = "688"
PROJ_UNIT_CLASS_ID        = "697"
GEO_UNIT_CLASS_ID         = "701"
PRIME_MERIDIAN_CLASS_ID   = "702"

PROJECTION_FORMULA = { "ALBERS_CONIC_EQUAL_AREA" : 66605
                     ,"AZIMUTHAL_EQUIDISTANT" : 65347
                     ,"BEHRMANN" : 86405
                     ,"BONNE" : 65362
                     ,"CASSINI_SOLDNER" : 66602
                     ,"CYLINDRICAL_EQUAL_AREA" : 86407
                     ,"ECKERT_I" : 65358
                     ,"ECKERT_II" : 65361
                     ,"ECKERT_III" : 65334
                     ,"ECKERT_IV" : 65353
                     ,"ECKERT_V" : 65350
                     ,"ECKERT_VI" : 65359
                     ,"EQUIDISTANT_CONIC" : 65340
                     ,"EQUIRECTANGULAR" : 86409
                     ,"GALL_STEREOGRAPHIC" : 86411
                     ,"HOTINE_OBLIQUE_MERCATOR" : 66601
                     ,"HOTINE_OBLIQUE_MERCATOR_TWO_POINT_NATURAL_ORIGIN" : 86413
                     ,"KROVAK" : 66607
                     ,"LABORDE_OBLIQUE_MERCATOR" : 86415
                     ,"LAMBERT_AZIMUTHAL_EQUAL_AREA" : 65332
                     ,"LAMBERT_CONFORMAL_CONIC_1SP" : 66599
                     ,"LAMBERT_CONFORMAL_CONIC_2SP" : 66600
                     ,"LAMBERT_CONFORMAL_CONIC_2SP_BELGIUM" : 86417
                     ,"LOXIMUTHAL" : 86419
                     ,"MERCATOR_1SP" : 66604
                     ,"MILLER_CYLINDRICAL" : 65331
                     ,"MOLLWEIDE" : 65355
                     ,"NEW_ZEALAND_MAP_GRID" : 66606
                     ,"OBLIQUE_STEREOGRAPHIC" : 66603
                     ,"PLATE_CARREE" : 65333
                     ,"POLAR_STEREOGRAPHIC" : 86421
                     ,"POLYCONIC" : 65338
                     ,"QUARTIC_AUTHALIC" : 86423
                     ,"ROBINSON" : 65356
                     ,"SINUSOIDAL" : 65349
                     ,"STEREOGRAPHIC" : 65357
                     ,"TRANSVERSE_MERCATOR" : 65346
                     ,"TRANSVERSE_MERCATOR_SOUTH_ORIENTATED" : 86425
                     ,"TUNISIA_MINING_GRID" : 86427
                     ,"TWO_POINT_EQUIDISTANT" : 86429
                     ,"VANDERGRINTEN" : 65342
                     ,"WINKEL_I" : 86431
                     ,"WINKEL_II" : 86433
                     }

def get_domain_id ( object_class_id, domain_name ) :
    # Get ID of domain record
    query_xml  = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + str(domain_name) + "</Literal></PropertyIsEqualTo></And></Filter>"
    result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [object_class_id, query_xml ])
    if result_xml :
        result_dom = xml.dom.minidom.parseString(str(result_xml))
        result_set = result_dom.getElementsByTagName("ROW")
        for row in result_set :
            id_tag  = row.getElementsByTagName("ID")[0]
            id  = id_tag.childNodes[0].nodeValue
    else :
        id = None
    return id

def set_value ( object_class_id, object_instance_id, column_name, column_value) :
    mut_xml = "<ROWSET><ROW>"
    mut_xml = mut_xml + "<ID>" + str(object_instance_id) + "</ID>"
    mut_xml = mut_xml + "<" + str(column_name) + ">" + str(column_value) + "</" + str(column_name) + ">"
    mut_xml = mut_xml + "</ROW></ROWSET>"
    obj_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ object_class_id, 'U', mut_xml ])
    return obj_id


def get_new_domain_id ( object_class_id, domain_name ) :
    # Get ID of domain record
    query_xml  = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + str(domain_name) + "</Literal></PropertyIsEqualTo></And></Filter>"
    result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [object_class_id, query_xml ])
    if result_xml :
        result_dom = xml.dom.minidom.parseString(str(result_xml))
        result_set = result_dom.getElementsByTagName("ROW")
        for row in result_set :
            id_tag  = row.getElementsByTagName("ID")[0]
            dom_id  = id_tag.childNodes[0].nodeValue
    else :
        dom_id = None
    # Insert when ID is not found
    if not dom_id :
        mut_xml = "<ROWSET><ROW><NAME>" + str(domain_name) + "</NAME></ROW></ROWSET>"
        dom_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [object_class_id, 'I', mut_xml ])
        print str(domain_name) + " inserted as domain value in object class " + str(object_class_id)
    return dom_id

def get_country_id ( domain_name ) :
    # Get ID of country record
    query_xml  = "<Filter><And><PropertyIsLike><PropertyName>NAME</PropertyName><Literal>" + str(domain_name) + "</Literal></PropertyIsLike></And></Filter>"
    result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [COUNTY_CLASS_ID, query_xml ])
    if result_xml :
        result_dom = xml.dom.minidom.parseString(str(result_xml))
        result_set = result_dom.getElementsByTagName("ROW")
        for row in result_set :
            id_tag  = row.getElementsByTagName("ID")[0]
            id  = id_tag.childNodes[0].nodeValue
    else :
        id = None
    return id

if __name__ == "__main__":

    # Init Oracle connection
    DbUser = "sens"
    DbPass = "senso"
    DbConnect = "10.20.0.49/sens11"
    oracle_connection = cx_Oracle.connect(DbUser, DbPass, DbConnect)
    oracle_cursor     = oracle_connection.cursor()
    print "Connected to database"

    if IMPORT_ELLIPSOID :
        # Import ellipsoids
        print "Import ellipsoid"
        fIn  = open(ELLIPSOID_IN,'r')
        nr_of_lines = 0
        for line in fIn :
            print line
            line_split = line.rstrip().split(",")
            # 0 = name
            # 1 = code (SYS003)
            # 2 = semi major axis (SYS001)
            # 3 = flattening (SYS002)
            mut_xml = "<ROWSET><ROW><NAME>" + str(line_split[0]) + "</NAME>" + "<SYS001>" + str(line_split[2]) + "</SYS001>" + "<SYS002>" + str(line_split[3]) + "</SYS002>" + "<SYS003>" + str(line_split[1]) + "</SYS003>"  + "</ROW></ROWSET>"
            print mut_xml
            obj_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ELLIPSOID_CLASS_ID, 'I', mut_xml ])
            nr_of_lines = nr_of_lines + 1
        print "Number of ellipsoids imported " + str(nr_of_lines)
        fIn.close()

    if IMPORT_HORIZONTAL_DATUM :
        # Import horizontal datums
        print "Import horizontal datums"
        fIn  = open(HORIZONTAL_DATUM_IN,'r')
        nr_of_lines = 0
        for line in fIn :
            # FD_Abidjan_1987 0
            #,6143 epsg       1
            #,124.76 dx       2
            #,53     dy       3
            #,466.79 dz       4
            #,0      rx       5
            #,0      ry       6
            #,0      rz       7
            #,0      scale    8
            #,       stdx     9
            #,       stdy     10
            #,       stdz     11
            #,Clarke 1880 (RGS) ellipsoid 12
            line_split  = line.rstrip().split(",")
            if len(line_split) == 13 :
                NAME        = str(line_split[0])                     # NAME
                Dx          = str(line_split[2])                     # SYS002
                Rx          = str(line_split[5])                     # SYS003
                Dy          = str(line_split[3])                     # SYS004
                Ry          = str(line_split[6])                     # SYS005
                Dz          = str(line_split[4])                     # SYS006
                Rz          = str(line_split[7])                     # SYS007
                ScaleFactor = str(line_split[8])                     # SYS008
                Ellipsoid   = str(line_split[12])                    # SYS009
                StdDevDx    = str(line_split[9])                     # SYS010
                StdDevDy    = str(line_split[10])                    # SYS011
                StdDevDz    = str(line_split[11])                    # SYS012
                EpsgCode    = str(line_split[1])                     # SYS013
                # Get ellipsoid id
                ellipsoid_id = get_domain_id ( ELLIPSOID_CLASS_ID, Ellipsoid )
                # Build insert XML
                mut_xml = "<ROWSET><ROW>"
                mut_xml = mut_xml + "<NAME>" + str(NAME) + "</NAME>"
                mut_xml = mut_xml + "<SYS002>" + str(Dx) + "</SYS002>"
                mut_xml = mut_xml + "<SYS003>" + str(Rx) + "</SYS003>"
                mut_xml = mut_xml + "<SYS004>" + str(Dy) + "</SYS004>"
                mut_xml = mut_xml + "<SYS005>" + str(Ry) + "</SYS005>"
                mut_xml = mut_xml + "<SYS006>" + str(Dz) + "</SYS006>"
                mut_xml = mut_xml + "<SYS007>" + str(Rz) + "</SYS007>"
                mut_xml = mut_xml + "<SYS008>" + str(ScaleFactor) + "</SYS008>"
                mut_xml = mut_xml + "<SYS009>" + str(ellipsoid_id) + "</SYS009>"
                mut_xml = mut_xml + "<SYS010>" + str(StdDevDx) + "</SYS010>"
                mut_xml = mut_xml + "<SYS011>" + str(StdDevDy) + "</SYS011>"
                mut_xml = mut_xml + "<SYS012>" + str(StdDevDz) + "</SYS012>"
                mut_xml = mut_xml + "<SYS013>" + str(EpsgCode) + "</SYS013>"
                mut_xml = mut_xml + "</ROW></ROWSET>"
                print mut_xml
                obj_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [HORIZONTAL_DATUM_CLASS_ID, 'I', mut_xml ])
                nr_of_lines = nr_of_lines + 1
                print nr_of_lines
        print "Number of horizontal datums imported " + str(nr_of_lines)
        fIn.close()

    if IMPORT_HORIZONTAL_PARAMETERS :
        # Import horizontal parameters
        print "Import horizontal parameters"
        fIn  = open(HORIZONTAL_PARAMETERS_IN,'r')
        nr_of_lines = 0
        mut_xml = "<ROWSET><ROW>"
        for line in fIn :
            line_split = line.rstrip().split(":")
            if len(line_split) == 2 :
                # Parse parameter
                if str(line_split[0]) == str("classname") :
                    value = str(line_split[1]).strip()
                    if str(value) == "Common Coordinate Systems" :
                        print "Insert is F"
                        insert = False
                    else :
                        print "Insert is T"
                        insert = True
                if str(line_split[0]) == str("name") :
                    value = str(line_split[1]).strip()
                    coordinate_system_name  = value
                    print coordinate_system_name
                    mut_xml = mut_xml + "<NAME>" + str(value) + "</NAME>"
                if str(line_split[0]) == str("type"):
                    value = str(line_split[1])
                    if str(value) == "GEOGCS" :
                        value_id = 64167
                    else :
                        value_id = 64168
                    mut_xml = mut_xml + "<SYS001>" + str(value_id) + "</SYS001>"
                if str(line_split[0]) == str("epsg"):
                    value = str(line_split[1]).strip()
                    if int(value) == int(-1) :
                        mut_xml = mut_xml + "<SYS002></SYS002>"
                    else :
                        mut_xml = mut_xml + "<SYS002>" + str(value) + "</SYS002>"
                if str(line_split[0]) == str("proj zone") and ( "UTM" in coordinate_system_name ):
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        mut_xml = mut_xml + "<SYS007>" + str(value) + "</SYS007>"
                if str(line_split[0]) == str("proj hemisphere"):
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        if str(value) == "N" :
                            value_id = 64172
                        elif str(value) == "S" : 
                            value_id = 64173
                        elif str(value) == "E" :
                            value_id = 92313
                        elif str(value) == "W" :
                            value_id = 92315
                        mut_xml = mut_xml + "<SYS008>" + str(value_id) + "</SYS008>"
                if str(line_split[0]) == str("geo datum name") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        print "geo datum name: " + str(value)
                        value_id = get_domain_id ( HORIZONTAL_DATUM_CLASS_ID, value )
                        if value_id :
                            mut_xml = mut_xml + "<SYS009>" + str(value_id) + "</SYS009>"
                if str(line_split[0]) == str("proj name") :
                    if line_split[1] :
                        value_id = PROJECTION_FORMULA.get(string.upper(str(line_split[1]).strip()))
                        print "proj name: " + string.upper(str(line_split[1]).strip())
                        if value_id :
                            mut_xml = mut_xml + "<SYS010>" + str(value_id) + "</SYS010>"
                if str(line_split[0]) == str("country") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        print "country: " + str(value)
                        value_id = get_new_domain_id ( COUNTY_CLASS_ID, value )
                        if value_id :
                            mut_xml = mut_xml + "<SYS011>" + str(value_id) + "</SYS011>"
                if str(line_split[0]) == str("proj false east") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        mut_xml = mut_xml + "<SYS012>" + str(value) + "</SYS012>"
                if str(line_split[0]) == str("proj false north") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        mut_xml = mut_xml + "<SYS013>" + str(value) + "</SYS013>"
                if str(line_split[0]) == str("proj sf") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        mut_xml = mut_xml + "<SYS014>" + str(value) + "</SYS014>"
                if str(line_split[0]) == str("proj cm") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        mut_xml = mut_xml + "<SYS015>" + str(value) + "</SYS015>"
                if str(line_split[0]) == str("proj cp") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        mut_xml = mut_xml + "<SYS016>" + str(value) + "</SYS016>"
                if str(line_split[0]) == str("proj lat1") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        mut_xml = mut_xml + "<SYS017>" + str(value) + "</SYS017>"
                if str(line_split[0]) == str("proj lat2") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        mut_xml = mut_xml + "<SYS018>" + str(value) + "</SYS018>"
                if str(line_split[0]) == str("proj azimuth") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        mut_xml = mut_xml + "<SYS019>" + str(value) + "</SYS019>"
                if str(line_split[0]) == str("proj grid angle") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        mut_xml = mut_xml + "<SYS020>" + str(value) + "</SYS020>"
                if str(line_split[0]) == str("continent") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        print "continent: " + str(value)
                        value_id = get_new_domain_id ( CONTINENT_CLASS_ID, value )
                        if value_id :
                            mut_xml = mut_xml + "<SYS023>" + str(value_id) + "</SYS023>"
                if str(line_split[0]) == str("state") :
                    if line_split[1] :
                        value = str(line_split[1]).strip()
                        print "state: " + str(value)
                        value_id = get_new_domain_id ( STATE_CLASS_ID, value )
                        if value_id :
                            mut_xml = mut_xml + "<SYS024>" + str(value_id) + "</SYS024>"
            else :
                    # Execute update of record
                    if insert :
                        mut_xml = mut_xml + "<SYS005>F</SYS005>"
                        mut_xml = mut_xml + "<SYS006>F</SYS006>"
                        mut_xml = mut_xml + "</ROW></ROWSET>"
                        print mut_xml
                        obj_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [GEODETIC_PARAM_CLASS_ID, 'I', mut_xml ])
                        nr_of_lines = nr_of_lines + 1
                        print nr_of_lines
                    else :
                        print "Skip common systems"
                    # Reset mut_xml
                    mut_xml = "<ROWSET><ROW>"
        print "Number of wkt records imported " + str(nr_of_lines)
        fIn.close()

    if LINK_COUNTRIES :
        print "Link countries to continent"
        fIn  = open(HORIZONTAL_PARAMETERS_IN,'r')
        nr_of_lines = 0
        continent   = None
        country     = None
        for line in fIn :
            line_split = line.rstrip().split(":")
            if len(line_split) == 2 :
                if str(line_split[0]) == str("continent") :
                    if line_split[1] :
                        continent = str(line_split[1]).strip()
                        print "continent: " + str(continent)
                if str(line_split[0]) == str("country") :
                    if line_split[1] :
                        country = str(line_split[1]).strip()
                        print "country: " + str(country)
            elif continent and country :
                # Get continent for country
                query_xml  = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + str(country) + "</Literal></PropertyIsEqualTo></And></Filter>"
                result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [COUNTY_CLASS_ID, query_xml ])
                if result_xml :
                    result_dom = xml.dom.minidom.parseString(str(result_xml))
                    result_set = result_dom.getElementsByTagName("ROW")
                    for row in result_set :
                        id_tag        = row.getElementsByTagName("SYS001")[0]
                        try :
                            continent_id  = id_tag.childNodes[0].nodeValue
                        except :
                            print "No continent ID "
                            continent_id = None
                            id_tag        = row.getElementsByTagName("ID")[0]
                            country_id    = id_tag.childNodes[0].nodeValue
                else :
                    continent_id = None
                # If continent is None => Get ID of continent
                if not continent_id :
                    query_xml  = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + str(continent) + "</Literal></PropertyIsEqualTo></And></Filter>"
                    result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [CONTINENT_CLASS_ID, query_xml ])
                    if result_xml :
                        result_dom = xml.dom.minidom.parseString(str(result_xml))
                        result_set = result_dom.getElementsByTagName("ROW")
                        for row in result_set :
                            id_tag  = row.getElementsByTagName("ID")[0]
                            new_continent_id  = id_tag.childNodes[0].nodeValue
                    else :
                        new_continent_id = None
                    if new_continent_id :
                        # Update continent
                        print "Execute update"
                        mut_xml = "<ROWSET><ROW>"
                        mut_xml = mut_xml + "<ID>" + str(country_id) + "</ID>"
                        mut_xml = mut_xml + "<SYS001>" + str(new_continent_id) + "</SYS001>"
                        mut_xml = mut_xml + "</ROW></ROWSET>"
                        print mut_xml
                        obj_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [COUNTY_CLASS_ID, 'U', mut_xml ])
                        nr_of_lines = nr_of_lines + 1
                        print nr_of_lines
        print "Number of wkt records updated " + str(nr_of_lines)
        fIn.close()


    if IMPORT_WKT_RECORDS :
        # Update wkt unformatted record
        print "Update wkt unformatted record"
        fIn  = open(WKT_RECORDS_IN,'r')
        nr_of_lines = 0
        for line in fIn :
            # Split line at first <space>
            line_split = line.rstrip().split(' ',1)
            if len(line_split) == 2 :
                name = line_split[0]
                wkt  = line_split[1]
                # Get ID of record
                print "Get instance id for " + str(name)
                #query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + name + "</Literal></PropertyIsEqualTo></And></Filter>"
                query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>SYS002</PropertyName><Literal>3994</Literal></PropertyIsEqualTo></And></Filter>"
                result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [GEODETIC_PARAM_CLASS_ID, query_xml ])
                if result_xml :
                    result_dom = xml.dom.minidom.parseString(str(result_xml))
                    result_set = result_dom.getElementsByTagName("ROW")
                    for row in result_set :
                        id_tag  = row.getElementsByTagName("ID")[0]
                        upd_id  = id_tag.childNodes[0].nodeValue
                else :
                    upd_id = None
                print "Execute update for instance " + str(upd_id)
                if upd_id :
                    mut_xml = "<ROWSET><ROW>"
                    mut_xml = mut_xml + "<ID>" + str(upd_id) + "</ID>"
                    mut_xml = mut_xml + "<SYS022>" + str(wkt) + "</SYS022>"
                    mut_xml = mut_xml + "</ROW></ROWSET>"
                    obj_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ GEODETIC_PARAM_CLASS_ID, 'U', mut_xml ])
                    nr_of_lines = nr_of_lines + 1
        print "Number of wkt records updated " + str(nr_of_lines)
        fIn.close()

    if IMPORT_EPSG_CODES :
        print "Update epsg codes"
        fIn  = open(HORIZONTAL_PARAMETERS_IN,'r')
        nr_of_lines = 0
        for line in fIn :
            line_split = line.rstrip().split(":")
            if len(line_split) == 2 :
                nr_of_lines = nr_of_lines + 1
                # Parse parameter
                if str(line_split[0]) == str("name") :
                    value = str(line_split[1]).strip()
                    coordinate_system_name  = 'A' + value[1:]
                if str(line_split[0]) == str("epsg"):
                    value = str(line_split[1]).strip()
                    if int(value) == int(-1) :
                        epsg = ""
                    else :
                        epsg = str(value)
                        print str(nr_of_lines) + ": Update " + epsg + " for " + coordinate_system_name
                        l_stmt = "update sdb_geodetichorizparams set sys002 = " + epsg + " where name = \'" + str(coordinate_system_name) + "\'"
                        oracle_cursor.execute(l_stmt)

    if IMPORT_FORMATTED_WKT_RECORDS :
        # Update wkt unformatted record
        print "Update wkt formatted record"
        fIn  = open(FORMATTED_WKT_RECORDS_IN,'r')
        nr_of_lines = 0
        for line in fIn :
            if line[:1] == "#" :
                coordinate_system       = str(line[2:]).strip()
                coordinate_system_found = True
                start_record            = False
            elif line[:1] == "\n" and coordinate_system_found and not start_record :
                start_record            = True
            elif line[:6] == "GEOGCS" or line[:6] == "PROJCS" :
                formatted_wkt           = str(line)
                coordinate_system_wkt   = coordinate_system
            elif start_record and len(line) > 1  :
                formatted_wkt           = formatted_wkt + str(line)
            elif line[:1] == "\n" and coordinate_system_found and start_record :
                # Store record and reset
                # Get ID of record
                print str(formatted_wkt)
                print "Get instance id for " + str(coordinate_system_wkt)
                #query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + str(coordinate_system_wkt) + "</Literal></PropertyIsEqualTo></And></Filter>"
                query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>SYS002</PropertyName><Literal>3994</Literal></PropertyIsEqualTo></And></Filter>"
                result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [GEODETIC_PARAM_CLASS_ID, query_xml ])
                if result_xml :
                    result_dom = xml.dom.minidom.parseString(str(result_xml))
                    result_set = result_dom.getElementsByTagName("ROW")
                    for row in result_set :
                        id_tag  = row.getElementsByTagName("ID")[0]
                        upd_id  = id_tag.childNodes[0].nodeValue
                else :
                    upd_id = None
                # Execute update
                print "Execute update for instance " + str(upd_id)
                if upd_id :
                    mut_xml = "<ROWSET><ROW>"
                    mut_xml = mut_xml + "<ID>" + str(upd_id) + "</ID>"
                    mut_xml = mut_xml + "<SYS004>" + str(formatted_wkt) + "</SYS004>"
                    mut_xml = mut_xml + "</ROW></ROWSET>"
                    obj_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ GEODETIC_PARAM_CLASS_ID, 'U', mut_xml ])
                    nr_of_lines = nr_of_lines + 1
        print "Number of wkt records updated " + str(nr_of_lines)
        fIn.close()

    # Import projection units
    if IMPORT_PROJECTION_UNITS :
        # Import projection units
        print "Import projection units"
        fIn  = open(HORIZONTAL_PARAMETERS_IN,'r')
        nr_of_lines = 0
        nr_of_units_inserted = 0
        mut_xml = "<ROWSET><ROW>"
        for line in fIn :
            line_split = line.rstrip().split(":")
            if len(line_split) == 2 :
                # Parse parameter
                if str(line_split[0]) == str("name") :
                    name = str(line_split[1]).strip()
                if str(line_split[0]) == str("proj unit name") :
                    proj_unit_name = str(line_split[1]).strip()
                    print "Projection unit: " + proj_unit_name
                    # Get proj unit id, check if unit is already added to table, if not add
                    if proj_unit_name :
                        query_xml  = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + str(proj_unit_name) + "</Literal></PropertyIsEqualTo></And></Filter>"
                        result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [PROJ_UNIT_CLASS_ID, query_xml ])
                        if not result_xml :
                            # Add projection unit
                            mut_xml = "<ROWSET><ROW>"
                            mut_xml = mut_xml + "<NAME>" + str(proj_unit_name) + "</NAME>"
                            mut_xml = mut_xml + "</ROW></ROWSET>"
                            proj_unit_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ PROJ_UNIT_CLASS_ID, 'I', mut_xml ])
                            print "Projection unit inserted " + str(proj_unit_name)
                            nr_of_units_inserted = nr_of_units_inserted + 1
                        else :
                            result_dom = xml.dom.minidom.parseString(str(result_xml))
                            result_set = result_dom.getElementsByTagName("ROW")
                            for row in result_set :
                                id_tag  = row.getElementsByTagName("ID")[0]
                                proj_unit_id  = id_tag.childNodes[0].nodeValue
                        # Get ID of record
                        print "Get instance id for " + str(name)
                        query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + name + "</Literal></PropertyIsEqualTo></And></Filter>"
                        result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [GEODETIC_PARAM_CLASS_ID, query_xml ])
                        if result_xml :
                            result_dom = xml.dom.minidom.parseString(str(result_xml))
                            result_set = result_dom.getElementsByTagName("ROW")
                            for row in result_set :
                                id_tag  = row.getElementsByTagName("ID")[0]
                                upd_id  = id_tag.childNodes[0].nodeValue
                        else :
                            upd_id = None
                        # Execute the update
                        print "Execute update for instance: " + str(upd_id)
                        if upd_id :
                            mut_xml = "<ROWSET><ROW>"
                            mut_xml = mut_xml + "<ID>" + str(upd_id) + "</ID>"
                            mut_xml = mut_xml + "<SYS025>" + str(proj_unit_id) + "</SYS025>"
                            mut_xml = mut_xml + "</ROW></ROWSET>"
                            obj_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ GEODETIC_PARAM_CLASS_ID, 'U', mut_xml ])
                            nr_of_lines = nr_of_lines + 1
                            print "Number of updates: " + str(nr_of_lines)
        print "Number of wkt records updated " + str(nr_of_lines)
        print "Number of projection units inserted " + str(nr_of_units_inserted)
        fIn.close()

    # Update projection units with multiplication factor
    if UPDATE_PROJECTION_UNITS:
        #meter|1
        #Gold Coast foot|0.3047997101815088
        #German legal metre|1.0000135965
        #kilometre|1000
        #Clarke's foot|0.3047972654
        #Indian yard|0.9143985307444408
        #British chain (Sears 1922 truncated)|20.116756
        #British chain (Sears 1922)|20.11676512155263
        #British foot (Sears 1922)|0.3047994715386762
        #British yard (Sears 1922)|0.9143984146160287
        #Clarke's link|0.201166195164
        #US survey foot|0.3048006096012192
        #foot|0.3048
        #link|0.201168
        #US_Foot|0.30480060960121924
        #Foot_US|0.30480060960121924
        name  = 'meter'
        value = 1
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'Gold Coast foot'
        value = 0.3047997101815088
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'German legal metre'
        value = 1.0000135965
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'kilometre'
        value = 1000
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'Clarke\'s foot'
        value = 0.3047972654
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'Indian yard'
        value = 0.9143985307444408
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'British chain (Sears 1922 truncated)'
        value = 20.116756
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'British chain (Sears 1922)'
        value = 20.11676512155263
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'British foot (Sears 1922)'
        value = 0.3047994715386762
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'British yard (Sears 1922)'
        value = 0.9143984146160287
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'Clarke\'s link'
        value = 0.201166195164
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'US survey foot'
        value = 0.3048006096012192
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'foot'
        value = 0.3048
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'link'
        value = 0.201168
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'US_Foot'
        value = 0.30480060960121924
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"
        name  = 'Foot_US'
        value = 0.30480060960121924
        id = get_domain_id ( PROJ_UNIT_CLASS_ID, name )
        if id:
            set_value ( PROJ_UNIT_CLASS_ID, id, "SYS001", value)
        else :
            print str(name) + " skipped"

    # Add the missing parameters
    if UPDATE_MISSING_PARAMETERS:
        # Import projection units
        upd_id                      = None
        new_geo_unit_inserted       = False
        new_prime_meridian_inserted = False
        print "Import missing parameters"
        fIn  = open(MISSING_PARAMETERS_IN,'r')
        nr_of_lines = 0
        nr_of_units_inserted = 0
        mut_xml = "<ROWSET><ROW>"
        for line in fIn :
            line_split = line.rstrip().split(":")
            if len(line_split) == 2 :
                # Parse parameter
                if str(line_split[0]) == str("name") :
                    name = str(line_split[1]).strip()
                    # Get ID of record
                    print "Get instance id for " + str(name)
                    query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + name + "</Literal></PropertyIsEqualTo></And></Filter>"
                    result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [GEODETIC_PARAM_CLASS_ID, query_xml ])
                    if result_xml :
                        result_dom = xml.dom.minidom.parseString(str(result_xml))
                        result_set = result_dom.getElementsByTagName("ROW")
                        for row in result_set :
                            id_tag  = row.getElementsByTagName("ID")[0]
                            upd_id  = id_tag.childNodes[0].nodeValue
                    else :
                        upd_id = None
                    print "Instance to update " + str(upd_id)

                if str(line_split[0]) == str("geo unit name") :
                    parameter_name = str(line_split[1]).strip()
                    print "Geo unit: " + parameter_name
                    # Get geo unit id, check if unit is already added to table, if not add
                    if parameter_name :
                        query_xml  = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + str(parameter_name) + "</Literal></PropertyIsEqualTo></And></Filter>"
                        result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [GEO_UNIT_CLASS_ID, query_xml ])
                        if not result_xml :
                            # Add projection unit
                            mut_xml = "<ROWSET><ROW>"
                            mut_xml = mut_xml + "<NAME>" + str(parameter_name) + "</NAME>"
                            mut_xml = mut_xml + "</ROW></ROWSET>"
                            parameter_id_28  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ GEO_UNIT_CLASS_ID, 'I', mut_xml ])
                            print "Geo unit inserted: " + str(parameter_name)
                            nr_of_units_inserted = nr_of_units_inserted + 1
                            new_geo_unit_inserted = True
                        else :
                            result_dom = xml.dom.minidom.parseString(str(result_xml))
                            result_set = result_dom.getElementsByTagName("ROW")
                            for row in result_set :
                                id_tag  = row.getElementsByTagName("ID")[0]
                                parameter_id_28  = id_tag.childNodes[0].nodeValue

                # Insert value for new geo unit parameter
                if str(line_split[0]) == str("geo unit dim") and new_geo_unit_inserted :
                    parameter_value = str(line_split[1]).strip()
                    mut_xml = "<ROWSET><ROW>"
                    mut_xml = mut_xml + "<ID>" + str(parameter_id_28) + "</ID>"
                    mut_xml = mut_xml + "<SYS001>" + str(parameter_value) + "</SYS001>"
                    mut_xml = mut_xml + "</ROW></ROWSET>"
                    parameter_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ GEO_UNIT_CLASS_ID, 'U', mut_xml ])
                    print "Geo unit value " + str(parameter_value) + " inserted"
                    new_geo_unit_inserted = False

                if str(line_split[0]) == str("geo pm name") :
                    parameter_name = str(line_split[1]).strip()
                    print "Prime meridian: " + parameter_name
                    # Get prime meridian id, check if unit is already added to table, if not add
                    if parameter_name :
                        query_xml  = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + str(parameter_name) + "</Literal></PropertyIsEqualTo></And></Filter>"
                        result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [PRIME_MERIDIAN_CLASS_ID, query_xml ])
                        if not result_xml :
                            # Add projection unit
                            mut_xml = "<ROWSET><ROW>"
                            mut_xml = mut_xml + "<NAME>" + str(parameter_name) + "</NAME>"
                            mut_xml = mut_xml + "</ROW></ROWSET>"
                            parameter_id_27  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ PRIME_MERIDIAN_CLASS_ID, 'I', mut_xml ])
                            print "Prime meridian inserted: " + str(parameter_name)
                            nr_of_units_inserted = nr_of_units_inserted + 1
                            new_prime_meridian_inserted = True
                        else :
                            result_dom = xml.dom.minidom.parseString(str(result_xml))
                            result_set = result_dom.getElementsByTagName("ROW")
                            for row in result_set :
                                id_tag  = row.getElementsByTagName("ID")[0]
                                parameter_id_27  = id_tag.childNodes[0].nodeValue

                # Insert value for new prime meridian parameter
                if str(line_split[0]) == str("geo pm lon") and new_prime_meridian_inserted :
                    parameter_value = str(line_split[1]).strip()
                    mut_xml = "<ROWSET><ROW>"
                    mut_xml = mut_xml + "<ID>" + str(parameter_id_27) + "</ID>"
                    mut_xml = mut_xml + "<SYS001>" + str(parameter_value) + "</SYS001>"
                    mut_xml = mut_xml + "</ROW></ROWSET>"
                    parameter_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ PRIME_MERIDIAN_CLASS_ID, 'U', mut_xml ])
                    print "Prime meridian value " + str(parameter_value) + " inserted"
                    new_prime_meridian_inserted = False

                if str(line_split[0]) == str("proj lat_org") :
                    parameter_name_29 = str(line_split[1]).strip()
                    print "Latitue origin: " + str(parameter_name_29)

                if str(line_split[0]) == str("proj grid angle") :
                    parameter_name_30 = str(line_split[1]).strip()
                    print "Grid angle: " + str(parameter_name_30)
                    # Get prime meridian id, check if unit is already added to table, if not add

            if line[:2] == str("--") and upd_id :
                # Execute the update
                print "EXECUTE UPDATE FOR INSTANCE: " + str(upd_id)
                if upd_id :
                    mut_xml = "<ROWSET><ROW>"
                    mut_xml = mut_xml + "<ID>" + str(upd_id) + "</ID>"
                    if parameter_id_27 :
                        mut_xml = mut_xml + "<SYS027>" + str(parameter_id_27) + "</SYS027>"
                    if parameter_id_28 :
                        mut_xml = mut_xml + "<SYS028>" + str(parameter_id_28) + "</SYS028>"
                    if parameter_name_29 :
                        mut_xml = mut_xml + "<SYS029>" + str(parameter_name_29) + "</SYS029>"
                    if parameter_name_30 :
                        mut_xml = mut_xml + "<SYS030>" + str(parameter_name_30) + "</SYS030>"
                    mut_xml = mut_xml + "</ROW></ROWSET>"
                    obj_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ GEODETIC_PARAM_CLASS_ID, 'U', mut_xml ])
                    nr_of_lines = nr_of_lines + 1
                    print "Number of updates: " + str(nr_of_lines)

        print "Number of wkt records updated " + str(nr_of_lines)
        print "Number of projection units inserted " + str(nr_of_units_inserted)
        fIn.close()


    if UPDATE_GEOCS :
        print "Link Geo Cs to Proj Cs"
        fIn  = open(MISSING_PARAMETERS_IN,'r')
        nr_of_lines_updated     = 0
        nr_of_lines_not_updated = 0
        for line in fIn :
            # Get required parameters
            line_split = line.rstrip().split(":")
            if len(line_split) == 2 :
                if str(line_split[0]) == str("type") :
                    type = str(line_split[1]).strip()
                if str(line_split[0]) == str("name") :
                    name = str(line_split[1]).strip()
                if str(line_split[0]) == str("geo name") :
                    geocs = str(line_split[1]).strip()
            # Execute update
            if line[:2] == str("--") :
                if str(type) == "PROJCS" :
                    # Get ID of GEOCS
                    print "Find geocs ID for " + str(geocs)
                    query_xml  = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + str(geocs) + "</Literal></PropertyIsEqualTo></And></Filter>"
                    result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [GEODETIC_PARAM_CLASS_ID, query_xml ])
                    if result_xml :
                        result_dom = xml.dom.minidom.parseString(str(result_xml))
                        result_set = result_dom.getElementsByTagName("ROW")
                        for row in result_set :
                            id_tag  = row.getElementsByTagName("ID")[0]
                            geocs_id  = id_tag.childNodes[0].nodeValue
                    else :
                        geocs_id = None
                    # Get ID of PROJCS record
                    print "Find projcs ID for " + str(name)
                    query_xml  = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + str(name) + "</Literal></PropertyIsEqualTo></And></Filter>"
                    result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [GEODETIC_PARAM_CLASS_ID, query_xml ])
                    if result_xml :
                        result_dom = xml.dom.minidom.parseString(str(result_xml))
                        result_set = result_dom.getElementsByTagName("ROW")
                        for row in result_set :
                            id_tag  = row.getElementsByTagName("ID")[0]
                            projcs_id  = id_tag.childNodes[0].nodeValue
                    else :
                        projcs_id = None
                    # Update record with ID of GEOCS
                    if geocs_id and projcs_id :
                        print "EXECUTE UPDATE"
                        print "Projcs ID: " + str(projcs_id)
                        print "Geocs ID: " + str(geocs_id)
                        mut_xml = "<ROWSET><ROW>"
                        mut_xml = mut_xml + "<ID>" + str(projcs_id) + "</ID>"
                        mut_xml = mut_xml + "<SYS031>" + str(geocs_id) + "</SYS031>"
                        mut_xml = mut_xml + "</ROW></ROWSET>"
                        obj_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ GEODETIC_PARAM_CLASS_ID, 'U', mut_xml ])
                        nr_of_lines_updated = nr_of_lines_updated + 1
                        print "Number of projcs updated: " + str(nr_of_lines_updated)
                else:
                    print "Not a projected system"
                    nr_of_lines_not_updated = nr_of_lines_not_updated + 1
                    print "Number of geocs not updated: " + str(nr_of_lines_not_updated)


    if INSERT_NEW_GEOCS :
        print "Add missing geocs"
        fIn  = open(MISSING_PARAMETERS_IN,'r')
        nr_of_lines_updated     = 0
        nr_of_geocs_inserted    = 0
        # Select FP with missing FG
        oracle_cursor.execute( 'select name, id from sdb_geodetichorizparams where sys031 is null and name like \'FP%\'' )
        projcs_list_cursor = oracle_cursor.fetchall()
        projcs_list = []
        projcs_dict = {}
        for proj_cs in projcs_list_cursor :
            print "Projcs " + str(proj_cs[0]) + " misses geocs"
            projcs_list.append( str(proj_cs[0]) )
            projcs_dict[ str(proj_cs[0]) ] =  str(proj_cs[1])
        for line in fIn :
            # Get required parameters
            line_split = line.rstrip().split(":")
            if len(line_split) == 2 :
                if str(line_split[0]) == str("name") :
                    name = str(line_split[1]).strip()
                if str(line_split[0]) == str("geo name") :
                    geocs = str(line_split[1]).strip()
                if str(line_split[0]) == str("geo epsg") :
                    geo_epsg = str(line_split[1]).strip()
                if str(line_split[0]) == str("geo datum name") :
                    geo_datum_name = str(line_split[1]).strip()
                if str(line_split[0]) == str("geo pm name") :
                    geo_pm_name = str(line_split[1]).strip()
                if str(line_split[0]) == str("geo unit name") :
                    geo_unit_name = str(line_split[1]).strip()
            # Execute update
            if line[:2] == str("--") and name[:2] == str("FP") :
                #print "Check " + str(name)
                projcs = name
                if projcs in projcs_list :
                    # Check if geocs is not yet added to table
                    statement = 'select count(1) from sdb_geodetichorizparams where name = \'' + str(geocs) + '\''
                    oracle_cursor.execute( statement )
                    count_list = oracle_cursor.fetchall()
                    for count_item in count_list :
                        count = count_item[0]
                    if int(count) == int(0) :
                        print "INSERT GEOCS " + str(geocs) + " extracted from projcs " + str(projcs)
                        # Get horizontal datum
                        hor_dat_id = get_domain_id ( HORIZONTAL_DATUM_CLASS_ID, geo_datum_name )
                        # Get prime meridian
                        pri_mer_id = get_domain_id ( PRIME_MERIDIAN_CLASS_ID, geo_pm_name )
                        # Get prime meridian
                        geo_uni_id = get_domain_id ( GEO_UNIT_CLASS_ID, geo_unit_name )
                        mut_xml = "<ROWSET><ROW>"
                        mut_xml = mut_xml + "<NAME>" + str(geocs) + "</NAME>"
                        mut_xml = mut_xml + "<SYS001>64167</SYS001>"
                        mut_xml = mut_xml + "<SYS002>" + str(geo_epsg) + "</SYS002>"
                        mut_xml = mut_xml + "<SYS009>" + str(hor_dat_id) + "</SYS009>"
                        mut_xml = mut_xml + "<SYS026>142432</SYS026>"
                        mut_xml = mut_xml + "<SYS027>" + str(pri_mer_id) + "</SYS027>"
                        mut_xml = mut_xml + "<SYS028>" + str(geo_uni_id) + "</SYS028>"
                        mut_xml = mut_xml + "</ROW></ROWSET>"
                        geocs_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ GEODETIC_PARAM_CLASS_ID, 'I', mut_xml ])
                        nr_of_geocs_inserted = nr_of_geocs_inserted + 1
                        print "Number of geocs inserted: " + str(nr_of_geocs_inserted)
                    else:
                        # Get obj_id from table
                        print "Get geocs ID for " + str(geocs) + " from table"
                        oracle_cursor.execute( 'select id from sdb_geodetichorizparams where name = \'' + str(geocs) + '\'' )
                        count_list = oracle_cursor.fetchall()
                        for count_item in count_list :
                            geocs_id = count_item[0]
                    if geocs_id :
                        print "EXECUTE UPDATE"
                        projcs_id = projcs_dict[ projcs ]
                        print "Projcs ID: " + str(projcs_id)
                        print "Geocs ID: " + str(geocs_id)
                        mut_xml = "<ROWSET><ROW>"
                        mut_xml = mut_xml + "<ID>" + str(projcs_id) + "</ID>"
                        mut_xml = mut_xml + "<SYS031>" + str(geocs_id) + "</SYS031>"
                        mut_xml = mut_xml + "</ROW></ROWSET>"
                        obj_id  = oracle_cursor.callfunc("sdb_interface_pck.setObject", cx_Oracle.NUMBER, [ GEODETIC_PARAM_CLASS_ID, 'U', mut_xml ])
                        nr_of_lines_updated = nr_of_lines_updated + 1
                        print "Number of projcs updated: " + str(nr_of_lines_updated)

        print "Total number of projcs updated: " + str(nr_of_lines_updated)
        print "Total number of geocs inserted: " + str(nr_of_geocs_inserted)

    # Close file and commit
    print "Commit transaction"
    oracle_connection.commit()
    oracle_connection.close()

        #CoordSysClass                    SYS001
        #EPSGCode                         SYS002
        #WKTDescription                   SYS004 skip
        #FrequentlyUsedValue              SYS005
        #UserDefined                      SYS006
        #UtmZone                          SYS007
        #Hemisphere                       SYS008
        #HorizontalDatum                  SYS009
        #ProjectionFormula                SYS010
        #Country                          SYS011
        #FalseEasting                     SYS012
        #FalseNorthing                    SYS013
        #ScaleFactor                      SYS014
        #CentralMeridian                  SYS015
        #CentralParallel                  SYS016
        #FirstParallel                    SYS017
        #SecondParallel                   SYS018
        #AzimuthYAxis                     SYS019
        #TiltProjectionPlane              SYS020
        #CentralLine                      SYS021
        #WktUnformatted                   SYS022
        #Continent                        SYS023
        #State                            SYS024

   








        # Get ID of record
#        query_xml = "<Filter><And><PropertyIsEqualTo><PropertyName>NAME</PropertyName><Literal>" + name[3:] + "</Literal></PropertyIsEqualTo></And></Filter>"
#        result_xml = oracle_cursor.callfunc("sdb_interface_pck.getObject", cx_Oracle.CLOB, [GEODETIC_CLASS_ID, query_xml ])
#        if result_xml :
#            result_dom = xml.dom.minidom.parseString(str(result_xml))
#            result_set = result_dom.getElementsByTagName("ROW")
#            for row in result_set :
#                id_tag  = row.getElementsByTagName("ID")[0]
#                upd_id  = id_tag.childNodes[0].nodeValue

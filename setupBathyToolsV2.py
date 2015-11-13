from cx_Freeze import setup, Executable

import datetime

VERSION = "0.6.6.0"

#l_date = datetime.datetime.now()
#file_handle = open ("D:\\SensSVN\\BathyTools\\src\\etc\\version.txt", "r+")
#line_list = file_handle.readlines()
#last_line = line_list[-1]
#line_items = last_line.split(";")
#l_build_items = line_items[1]
#l_build_item = l_build_items.split(":")
#l_build_nr = int(l_build_item[1])
## Increase build number
#l_build_nr = l_build_nr + 1
#file_handle.close()
#file_handle = open ("D:\\SensSVN\\BathyTools\\src\\etc\\version.txt", "w")
#file_handle.writelines(line_list)
#file_handle.write("Version: " + str(VERSION) + " ; Build: " + str(l_build_nr) + " ; Date: " + str(l_date) + " ;" + "\n" )
#file_handle.close()

includeFiles = [
("C:\EMODNET\8_python\BathyTools\src\etc\Microsoft.VC90.CRT.manifest", "Microsoft.VC90.CRT.manifest"),
("C:\EMODNET\8_python\BathyTools\src\etc\proj.dll","proj.dll"),
("C:\EMODNET\8_python\BathyTools\src\etc\coordinate_axis.csv", "coordinate_axis.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\ellipsoid.csv", "ellipsoid.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\gcs.csv", "gcs.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\gcs.override.csv", "gcs.override.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\gdal_datum.csv", "gdal_datum.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\gt_datum.csv", "gt_datum.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\gt_ellips.csv", "gt_ellips.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\pcs.csv", "pcs.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\pcs.override.csv", "pcs.override.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\prime_meridian.csv", "prime_meridian.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\projop_wparm.csv", "projop_wparm.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\projop_wparm.csv", "projop_wparm.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\projop_wparm.csv", "projop_wparm.csv"),
("C:\EMODNET\8_python\BathyTools\src\etc\\version.txt", "version.txt"),
("C:\EMODNET\8_python\BathyTools\src\etc\\license_cx_Freeze.txt", "license_cx_Freeze.txt"),
("C:\EMODNET\8_python\BathyTools\src\etc\\license_cx_Oracle.txt", "license_cx_Oracle.txt"),
("C:\EMODNET\8_python\BathyTools\src\etc\\license_gdal_ogr.txt", "license_gdal_ogr.txt"),
("C:\EMODNET\8_python\BathyTools\src\etc\\license_Python24.txt", "license_Python24.txt"),
("C:\EMODNET\8_python\BathyTools\src\etc\\geoconv\\GeoConv.exe", "GeoConv.exe"),
("C:\EMODNET\8_python\BathyTools\src\etc\\geoconv\\lat_etrs.grd", "lat_etrs.grd"),
("C:\EMODNET\8_python\BathyTools\src\etc\\geoconv\\Y2c.dat", "Y2c.dat"),
("C:\EMODNET\8_python\BathyTools\src\etc\\geoconv\\X2c.dat", "X2c.dat"),
("C:\EMODNET\8_python\BathyTools\src\etc\\geoconv\\nlGeo04.dat", "nlGeo04.dat"),
("C:\EMODNET\8_python\BathyTools\src\etc\\geoconv\\RD_ETRS_DLL.dll", "RD_ETRS_DLL.dll"),
("C:\EMODNET\8_python\BathyTools\src\etc\\geoconv\\SENSMakeGrid.exe", "SENSMakeGrid.exe"),
("C:\EMODNET\8_python\BathyTools\src\etc\\geoconv\\Readme.txt", "Readme.txt"),
("C:\EMODNET\8_python\BathyTools\src\etc\\geoconv\\digipol.exe", "digipol.exe")
]

options = dict(
include_files = includeFiles)

setup(
        name = "BathyToolsV2",
        version = "0.6",
        description = "Executables to run third party executables",
        options = dict(build_exe = options),
        executables = [ Executable("..\src\BathyTools.py") ] )
        


 


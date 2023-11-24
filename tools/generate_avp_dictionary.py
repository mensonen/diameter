#!/usr/bin/env python3
#
# A crude helper script that reads the dictionary.xml file, and all of its
# included external entities, and produces two python files
# `message/constants.py` and `message/avp/dictionary.py` that contain
# constant values mapping AVPs, vendors and ENUMs to their integer values, and
# a large dictionary that maps each AVP to a definition of how they can be
# built (python type, mandatory flags etc).
import pathlib
import re

from lxml import etree as ElementTree

# point this to a directory containing wireshark dictionaries
WIRESHARK_DICTIONARY = "/usr/share/wireshark/diameter/dictionary.xml"

const_outfile = pathlib.Path("../src/diameter/message/constants.py")
dict_outfile = pathlib.Path("../src/diameter/message/avp/dictionary.py")

tree = ElementTree.parse(WIRESHARK_DICTIONARY)
clean_name = re.compile(r"\W+")

# these are useless to us, as they do not produce even remotely unique AVP
# variable names
skip = ("Not defined", "Unassigned", "Reserved", "Experimental",
        "Implementation", "Unallocated")

type_map = {
    "IPAddress": "AvpAddress", "Enumerated": "AvpEnumerated",
    "Float32": "AvpFloat32", "Float64": "AvpFloat64", "Grouped": "AvpGrouped",
    "Integer32": "AvpInteger32", "Integer64": "AvpInteger64",
    "Unsigned32": "AvpUnsigned32", "Unsigned64": "AvpUnsigned64",
    "OctetString": "AvpOctetString", "Time": "AvpTime",
    "UTF8String": "AvpUtf8String",
    "DiameterIdentity": "AvpOctetString", "IPFilterRule": "AvpOctetString",
    "QOSFilterRule": "AvpOctetString", "MIPRegistrationRequest": "AvpOctetString",
    "DiameterURI": "AvpUtf8String", "VendorId": "AvpUnsigned32",
    "AppId": "AvpInteger32", "OctetStringOrUTF8": "AvpOctetString"}

avp_constants = {}
avp_codes = []
avp_vendor_codes = {}
avp_dictionary = []
avp_vendor_dictionaries = {}

enum_constants = {}
application_constants = {}

vendors = {}

# pre-populate vendor name to vendor code mapping
for vendor in tree.iterfind("vendor"):
    vendors[vendor.attrib["vendor-id"]] = int(vendor.attrib["code"])
    avp_vendor_codes[int(vendor.attrib["code"])] = []
    avp_vendor_dictionaries[int(vendor.attrib["code"])] = []


def iter_tree(base: ElementTree._Element):
    """Go through an XML node and parse all 'avp' tags that it contains."""
    for avp in base.iterfind("avp"):
        avp_name = avp.attrib["name"]
        if avp_name.startswith(skip):
            continue

        avp_code = int(avp.attrib["code"])

        is_grouped = avp.find("grouped")
        if is_grouped is None:
            find_type = avp.find("type")
            if find_type is None:
                continue

            avp_type = find_type.attrib["type-name"]
        else:
            avp_type = "Grouped"

        if avp_type not in type_map:
            continue

        vendor_id = None

        orig_avp_constant = re.sub(clean_name, "_", avp_name).upper()

        if avp.attrib.get("vendor-id") and avp.attrib["vendor-id"] in vendors:
            vendor_id = vendors[avp.attrib["vendor-id"]]
            vendor_name = avp.attrib["vendor-id"]
            vendor_constant = re.sub(clean_name, "_", vendor_name).upper()
            avp_constant = f"AVP_{vendor_constant}_{orig_avp_constant}"
        else:
            avp_constant = f"AVP_{orig_avp_constant}"

        if avp_constant in avp_constants:
            continue
        if vendor_id is None and avp_code in avp_codes:
            continue
        elif vendor_id is not None and avp_code in avp_vendor_codes[vendor_id]:
            continue

        avp_constants[avp_constant] = avp_code
        if vendor_id is None:
            avp_codes.append(avp_code)
        else:
            avp_vendor_codes[vendor_id].append(avp_code)

        if avp_type == "Enumerated":
            enums = {
                int(e.attrib["code"]): re.sub(clean_name, "_", e.attrib["name"]).upper()
                for e in avp.iterfind("enum")}
            for enum_code, enum_name in enums.items():
                avp_constants[
                    f"E_{orig_avp_constant}_{enum_name}"] = enum_code

        dict_attrib = [f'"name": "{avp_name}"',
                       f'"type": {type_map[avp_type]}']
        if avp.attrib.get("mandatory"):
            dict_attrib.append('"mandatory": True')
        if vendor_id:
            dict_attrib.append(f'"vendor": {vendor_id}')
            avp_vendor_dictionaries[vendor_id].append(
                f"""{avp_constant}: {{{", ".join(dict_attrib)}}}""")
        else:
            avp_dictionary.append(
                f"""{avp_constant}: {{{", ".join(dict_attrib)}}}""")


# dictionary.xml
iter_tree(tree.find("base"))
# application entity files
for base in tree.iterfind("application"):
    iter_tree(base)

    app_id = base.attrib["id"]
    app_name = base.attrib["name"]

    application_constants[int(app_id)] = re.sub(clean_name, "_", app_name).upper()

# vendor entity files
for base in tree.iterfind("vendor"):
    iter_tree(base)

with const_outfile.open("w") as f:
    f.write("# Automatically generated from a dictionary.xml file\n\n")

    f.write("\n# All known Application IDs\n")
    for app_id, app_constant in application_constants.items():
        f.write(f"APP_{app_constant} = {app_id}\n")

    f.write("\n# All known Vendor IDs\n")
    for vendor_id, vendor_code in vendors.items():
        vendor_constant = re.sub(clean_name, "_", vendor_id).upper()
        f.write(f"VENDOR_{vendor_constant} = {vendor_code}\n")

    f.write("\n# Vendor ID-to-name mapping\n")
    f.write("VENDORS = {\n    ")
    f.write(",\n    ".join(f'{c}: "{n}"' for n, c in vendors.items()))
    f.write("}\n")

    f.write("\n# All known AVPs\n")
    for avp_constant, avp_code in avp_constants.items():
        f.write(f"{avp_constant} = {avp_code}\n")

with dict_outfile.open("w") as f:
    f.write("# Automatically generated from a dictionary.xml file\n\n")
    f.write("from . import (AvpAddress, AvpEnumerated, AvpFloat32, AvpFloat64, AvpGrouped,\n"
            "               AvpInteger32, AvpInteger64, AvpUnsigned32, AvpUnsigned64,\n"
            "               AvpOctetString, AvpTime, AvpUtf8String)\n")
    f.write("from ..constants import *\n\n")
    f.write("# base avp dictionary with no vendors\n")
    f.write("AVP_DICTIONARY = {\n    ")
    f.write(",\n    ".join(avp_dictionary))
    f.write("}\n\n")
    f.write("# vendor specific\n")
    f.write("AVP_VENDOR_DICTIONARY = {}\n")
    for vendor_id, avp_dictionary in avp_vendor_dictionaries.items():
        f.write(f"AVP_VENDOR_DICTIONARY[{vendor_id}] = {{\n    ")
        f.write(",\n    ".join(avp_dictionary))
        f.write("}\n")

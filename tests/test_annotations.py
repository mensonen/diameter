"""
Run from package root:
~# python3 -m pytest -vv
"""

import datetime
import typing
import warnings

import pytest

import diameter.message.avp.avp as avp
import diameter.message.avp.grouped as grouped_lib
from diameter.message import DefinedMessage
from diameter.message.avp.avp import *
from diameter.message.avp.dictionary import AVP_DICTIONARY, AVP_VENDOR_DICTIONARY
from diameter.message.avp.generator import AvpGenDef, AvpGenerator

# Doesn't include AvpGrouped
AVP_TYPES_TO_PYTHON_TYPES = {
    AvpAddress: str,
    AvpFloat32: float,
    AvpFloat64: float,
    AvpInteger32: int,
    AvpInteger64: int,
    AvpOctetString: bytes,
    AvpUnsigned32: int,
    AvpUnsigned64: int,
    AvpUtf8String: str,
    AvpTime: datetime.datetime,
}


class AvpInfo(typing.TypedDict):
    name: str
    type: type[avp.Avp]
    mandatory: bool
    vendor: typing.NotRequired[int]


def get_avp_dictionary_entry(avp_code: int, vendor_id: int) -> AvpInfo | None:
    if avp_code in AVP_DICTIONARY and vendor_id == 0:
        return AVP_DICTIONARY[avp_code]

    elif (
        vendor_id != 0
        and vendor_id in AVP_VENDOR_DICTIONARY
        and avp_code in AVP_VENDOR_DICTIONARY[vendor_id]
    ):
        return AVP_VENDOR_DICTIONARY[vendor_id][avp_code]

    else:
        return None


def validate_avp_generator_annotations(avp_generator: type[AvpGenerator]):
    parent_hints = typing.get_type_hints(avp_generator.__base__)
    # this test doesn't need to check annotations inherited from DefinedMessage
    # like "code: int", also avp_def and additional_avps
    avps_to_skip = {*parent_hints, "avp_def", "additional_avps"}

    hints = typing.get_type_hints(avp_generator)
    avp_defs = {avp.attr_name: avp for avp in avp_generator.avp_def}

    for avp_name, annotated_type in hints.items():
        if avp_name in avps_to_skip:
            continue

        field_name = f"{avp_generator.__name__}.{avp_name}"  # for logs
        assert avp_name in avp_defs, f"{field_name} doesn't have AVP definition"

        validate_avp_annotation(
            field_name, avp_name, avp_defs[avp_name], annotated_type
        )


def validate_avp_annotation(
    field_name: str,
    avp_name: str,
    avp_def: AvpGenDef,
    annotated_type: type,
):
    origin = typing.get_origin(annotated_type)
    if origin is not None and issubclass(origin, list):
        single_avp_type = typing.get_args(annotated_type)[0]
    else:
        single_avp_type = annotated_type

    if avp_def.type_class:
        assert issubclass(single_avp_type, avp_def.type_class), (
            f"{field_name} annotation ({annotated_type}) doesn't match "
            f"type_class in AvpGenDef: {avp_def.type_class.__name__}"
        )

    entry = get_avp_dictionary_entry(avp_def.avp_code, avp_def.vendor_id)
    assert entry is not None, (
        "No entry in AVP dictionaries with AVP code "
        f"{avp_def.avp_code} and vendor {avp_def.vendor_id}"
    )
    assert entry.get("vendor", 0) == avp_def.vendor_id

    converted_name = entry["name"].lower().replace("-", "_")
    name_options = [
        converted_name.replace("3gpp", "tgpp"),
        converted_name.replace("3gpp_", ""),
    ]
    if avp_name not in name_options:
        warnings.warn(
            f"{field_name} name doesn't exactly match its "
            f"AVP name: {entry['name']!r} ({name_options})"
        )

    if entry["type"] in AVP_TYPES_TO_PYTHON_TYPES:
        python_type = AVP_TYPES_TO_PYTHON_TYPES[entry["type"]]
        assert issubclass(single_avp_type, (python_type, Avp)), (
            f"{field_name} has {annotated_type} annotation, which cannot be "
            f"converted to {entry['type'].__name__}"
        )
    elif issubclass(entry["type"], AvpGrouped):
        assert avp_def.type_class is not None, (
            f"{field_name} AVP is grouped but doesn't have type_class"
        )
        assert hasattr(single_avp_type, "avp_def"), (
            f"{field_name} AVP is grouped but annotation ({annotated_type}) "
            f"doesn't have AVP definitions in it"
        )
    else:
        raise ValueError(f"{field_name} has unknown AVP type: {entry['type']}")


def test_defined_messages_annotations_correctness():
    for message_class in DefinedMessage.__subclasses__():
        validate_avp_generator_annotations(message_class)


def test_grouped_avps_annotations_correctness():
    for grouped_avp_classname in grouped_lib.__all__:
        grouped_avp_class = getattr(grouped_lib, grouped_avp_classname)

        if grouped_avp_class == grouped_lib.GenericSpec:
            continue  # GenericSpec doesn't have avp_def
        validate_avp_generator_annotations(grouped_avp_class)

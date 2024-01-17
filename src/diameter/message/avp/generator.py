"""
Definitions for classes and methods that are used to convert AVPs to python
class attributes and from class attributes back to AVPs.
"""
from __future__ import annotations

import logging

from typing import NamedTuple, Protocol

from .avp import Avp
from .errors import AvpEncodeError

logger = logging.getLogger("diameter.avp")


class AvpGenDef(NamedTuple):
    attr_name: str
    """The class attribute name that holds the value for the AVP."""
    avp_code: int
    """An AVP code that the actual AVP will be generated from."""
    vendor_id: int = 0
    """A vendor ID to pass on to AVP generation. Should be zero if no vendor 
    is to be set."""
    is_required: bool = False
    """Indicates that the class attribute must be set. A ValueError is raised 
    if the attribute is missing."""
    is_mandatory: bool | None = None
    """Overwrite the default mandatory flag provided by AVP dictionary."""
    type_class: type | None = None
    """For grouped AVPs, indicates the type of another class that holds the 
    attributes needed for the grouped sub-AVPs."""


# class attribute, required, avp code, vendor id, mandatory flag, typedef, is list
AvpGenType = tuple[AvpGenDef, ...]


def generate_avps_from_defs(obj: AvpGenerator, strict: bool = False) -> list[Avp]:
    """Go through a tree of AVP attribute definitions and produce AVPs.

    Traverses recursively through an `avp_def` attribute in an object instance
    and returns a complete list of AVPs, with grouped AVPs populated as well.
    """
    avp_list = []
    if not hasattr(obj, "avp_def"):
        return avp_list

    for gen_def in obj.avp_def:
        if not hasattr(obj, gen_def.attr_name) and gen_def.is_required:
            msg = f"mandatory AVP attribute `{gen_def.attr_name}` is not set"
            if strict:
                raise ValueError(msg)
            else:
                logger.debug(msg)
            continue
        elif not hasattr(obj, gen_def.attr_name):
            continue
        if getattr(obj, gen_def.attr_name) is None:
            continue
        attr_value = getattr(obj, gen_def.attr_name)

        try:
            if gen_def.type_class and isinstance(attr_value, list):
                for value in attr_value:
                    if value is None:
                        continue
                    grouped_avp = Avp.new(gen_def.avp_code, gen_def.vendor_id,
                                          is_mandatory=gen_def.is_mandatory)
                    sub_avps = generate_avps_from_defs(value)
                    grouped_avp.value = sub_avps
                    avp_list.append(grouped_avp)

            elif gen_def.type_class:
                grouped_avp = Avp.new(gen_def.avp_code, gen_def.vendor_id,
                                      is_mandatory=gen_def.is_mandatory)
                sub_avps = generate_avps_from_defs(attr_value)
                grouped_avp.value = sub_avps
                avp_list.append(grouped_avp)

            elif isinstance(attr_value, list):
                for value in attr_value:
                    if value is None:
                        continue
                    single_avp = Avp.new(gen_def.avp_code, gen_def.vendor_id,
                                         value=value,
                                         is_mandatory=gen_def.is_mandatory)
                    avp_list.append(single_avp)

            else:
                single_avp = Avp.new(gen_def.avp_code, gen_def.vendor_id,
                                     value=attr_value,
                                     is_mandatory=gen_def.is_mandatory)
                avp_list.append(single_avp)
        except AvpEncodeError as e:
            raise AvpEncodeError(
                f"Failed to parse value for attribute `{gen_def.attr_name}`: "
                f"{e}") from None

    if hasattr(obj, "additional_avps"):
        return avp_list + getattr(obj, "additional_avps")
    return avp_list


class AvpGenerator(Protocol):
    """A generic type structure that describes a single AVP generator.

    AVP generators are just dataclasses that hold attribute names, each
    attribute representing a value for an AVP. In addition, they hold a special
    attribute called `avp_def`, which is a tuple of `AvpGenDef` named tuple
    instances, describing how each class attribute converts into an actual
    AVP. The conversion is done by `__traverse_avp_defs` function, which is
    called when a `Message` subclass wants to return its AVP list.
    """
    avp_def: AvpGenType
    """A tuple containing AVP generation definitions."""

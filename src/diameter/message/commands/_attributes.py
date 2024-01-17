"""
Helper classes and data holders to generate and maintain class attributes for
Diameter Application Message subclasses.
"""
from __future__ import annotations

import logging

from ..avp import Avp, AvpDecodeError
from ..avp.generator import AvpGenDef, AvpGenerator

logger = logging.getLogger("diameter.message.avp")


def assign_attr_from_defs(obj: AvpGenerator, avp_list: list[Avp]):
    """Go through a tree of AVP attribute definitions and populate attributes.

    Traverses recursively through an `avp_def` attribute in an object instance
    and assigns values to the object attributes, based on AVPs discovered in a
    list of AVPs.

    The purpose of this is to convert a "dumb" AVP list tree in a `Message`
    instance into easily accessible attributes.
    """
    needed: dict[str, AvpGenDef] = {
        f"{a.avp_code}-{a.vendor_id}": a for a in obj.avp_def}

    for avp in avp_list:
        avp_key = f"{avp.code}-{avp.vendor_id}"

        if avp_key in needed:
            attr_name = needed[avp_key].attr_name
            has_attr = hasattr(obj, attr_name)
            current_value = None
            if has_attr:
                current_value = getattr(obj, attr_name)

            if needed[avp_key].type_class is not None:
                attr_value = needed[avp_key].type_class()
                assign_attr_from_defs(attr_value, avp.value)
                if has_attr and isinstance(current_value, list):
                    current_value.append(attr_value)
                else:
                    setattr(obj, attr_name, attr_value)

            elif has_attr and isinstance(current_value, list):
                avp_value = None
                try:
                    avp_value = avp.value
                except AvpDecodeError as e:
                    logger.warning(str(e))
                current_value.append(avp_value)
            else:
                avp_value = None
                try:
                    avp_value = avp.value
                except AvpDecodeError as e:
                    logger.warning(str(e))
                setattr(obj, attr_name, avp_value)

        elif hasattr(obj, "additional_avps"):
            getattr(obj, "additional_avps").append(avp)

        elif hasattr(obj, "_additional_avps"):
            getattr(obj, "_additional_avps").append(avp)

"""
Run from package root:
~# python3 -m pytest -vv
"""
import datetime
import pytest

from diameter.message import constants
from diameter.message.commands import CreditControlRequest

from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import MmtelInformation
from diameter.message.commands.credit_control import SupplementaryService
from diameter.message.commands.credit_control import AocInformation
from diameter.message.commands.credit_control import AocCostInformation
from diameter.message.commands.credit_control import TariffInformation
from diameter.message.commands.credit_control import AocSubscriptionInformation
from diameter.message.commands.credit_control import AccumulatedCost
from diameter.message.commands.credit_control import IncrementalCost
from diameter.message.commands.credit_control import CurrentTariff
from diameter.message.commands.credit_control import NextTariff
from diameter.message.commands.credit_control import ScaleFactor
from diameter.message.commands.credit_control import RateElement
from diameter.message.commands.credit_control import UnitValue
from diameter.message.commands.credit_control import UnitCost
from diameter.message.commands.credit_control import AocService


def test_ccr_3gpp_mms_information():
    # Test 3GPP extension AVPs added directly under Service-Information
    ccr = CreditControlRequest()
    ccr.session_id = "sctp-saegwc-poz01.lte.orange.pl;221424325;287370797;65574b0c-2d02"
    ccr.origin_host = b"dra2.gy.mno.net"
    ccr.origin_realm = b"mno.net"
    ccr.destination_realm = b"mvno.net"
    ccr.service_context_id = constants.SERVICE_CONTEXT_PS_CHARGING
    ccr.cc_request_type = constants.E_CC_REQUEST_TYPE_UPDATE_REQUEST
    ccr.cc_request_number = 952

    # Populate every single field even if it makes no sense
    ccr.service_information = ServiceInformation(
        mmtel_information=MmtelInformation(
            supplementary_service=[SupplementaryService(
                mmtel_service_type=constants.E_MMTEL_SERVICE_TYPE_CONFERENCE_CONF,
                service_mode=11,
                number_of_diversions=1,
                associated_party_address="sip:user@host",
                service_id="id",
                change_time=datetime.datetime.now(),
                number_of_participants=3,
                participant_action_type=constants.E_PARTICIPANT_ACTION_TYPE_JOIN_CONF,
                cug_information=b"\xff\x01\x02\x03\x04\x05\x06\x07",
                aoc_information=AocInformation(
                    aoc_cost_information=AocCostInformation(
                        accumulated_cost=AccumulatedCost(
                            value_digits=10,
                            exponent=2
                        ),
                        incremental_cost=[IncrementalCost(
                            value_digits=10,
                            exponent=2
                        )],
                        currency_code=10
                    ),
                    tariff_information=TariffInformation(
                        current_tariff=CurrentTariff(
                            currency_code=10,
                            scale_factor=ScaleFactor(
                                value_digits=10,
                                exponent=2
                            ),
                            rate_element=[RateElement(
                                cc_unit_type=constants.E_CC_UNIT_TYPE_MONEY,
                                charge_reason_code=constants.E_CHARGE_REASON_CODE_USAGE,
                                unit_value=UnitValue(
                                    value_digits=12,
                                    exponent=2
                                ),
                                unit_cost=UnitCost(
                                    value_digits=12,
                                    exponent=2
                                ),
                                unit_quota_threshold=900
                            )]
                        ),
                        tariff_time_change=datetime.datetime.now(),
                        next_tariff=NextTariff(
                            currency_code=10,
                            scale_factor=ScaleFactor(
                                value_digits=10,
                                exponent=2
                            ),
                            rate_element=[RateElement(
                                cc_unit_type=constants.E_CC_UNIT_TYPE_MONEY,
                                charge_reason_code=constants.E_CHARGE_REASON_CODE_USAGE,
                                unit_value=UnitValue(
                                    value_digits=12,
                                    exponent=2
                                ),
                                unit_cost=UnitCost(
                                    value_digits=12,
                                    exponent=2
                                ),
                                unit_quota_threshold=900
                            )]
                        )
                    ),
                    aoc_subscription_information=AocSubscriptionInformation(
                        aoc_service=[AocService(
                            aoc_service_obligatory_type=constants.E_AOC_SERVICE_TYPE_NONE,
                            aoc_service_type=constants.E_AOC_REQUEST_TYPE_AOC_TARIFF_ONLY
                        )],
                        aoc_format=constants.E_AOC_FORMAT_MONETARY,
                        preferred_aoc_currency=99
                    )
                )
            )]
        )
    )

    # Everything OK as long as it builds
    msg = ccr.as_bytes()

    assert ccr.header.length == len(msg)

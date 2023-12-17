"""
Run from package root:
~# python3 -m pytest -vv
"""
import pytest

from diameter.message import constants
from diameter.message.avp import Avp
from diameter.message.commands import DiameterEapAnswer, DiameterEapRequest
from diameter.message.commands.re_auth import FailedAvp
from diameter.message.commands.re_auth import ProxyInfo
from diameter.message.commands.re_auth import Tunneling


def test_der_create_new():
    # build a diameter-eap-request with every attribute populated and
    # attempt to parse it
    der = DiameterEapRequest()
    der.session_id = "labdra.gy.mno.net;02472683"
    der.auth_application_id = constants.APP_EAP_APPLICATION
    der.origin_host = b"dra2.gy.mno.net"
    der.origin_realm = b"mno.net"
    der.destination_realm = b"mno.net"
    der.auth_request_type = constants.E_AUTH_REQUEST_TYPE_AUTHENTICATE_ONLY
    der.destination_host =  b"dra3.mvno.net"
    der.nas_identifier = "dra2.gy.mno.net"
    der.nas_ip_address = b"10.0.0.2"
    der.nas_ipv6_address = b"0000:0000:0000:0000:0000:ffff:0a00:0002"
    der.nas_port = 8090
    der.nas_port_id = "1"
    der.nas_port_type = constants.E_NAS_PORT_TYPE_ETHERNET
    der.origin_state_id = 187623
    der.port_limit = 30
    der.user_name = "diameter"
    der.eap_payload = b"1"
    der.eap_key_name = b""  # rfc says should be empty
    der.service_type = constants.E_SERVICE_TYPE_FRAMED
    der.state = b"abcdef"
    der.authorization_lifetime = 1800
    der.auth_grace_period = 600
    der.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    der.callback_number = "1992"
    der.called_station_id = "78"
    der.calling_station_id = "79"
    der.originating_line_info = b"01cb"
    der.connect_info = "28800 V42BIS/LAPM"
    der.framed_compression = [10]
    der.framed_interface_id = 1
    der.framed_ip_address = b"10.0.0.1"
    der.framed_ipv6_prefix = [b"efefbada"]
    der.framed_ip_netmask = b"255.255.255.0"
    der.framed_mtu = 1500
    der.framed_protocol = constants.E_FRAMED_PROTOCOL_GANDALF
    der.tunneling = [Tunneling(
        tunnel_type=constants.E_TUNNEL_TYPE_L2TP,
        tunnel_medium_type=constants.E_TUNNEL_MEDIUM_TYPE_DECNET4,
        tunnel_client_endpoint="172.16.0.12",
        tunnel_server_endpoint="88.15.67.190"
    )]
    der.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]
    der.route_record = [b"ix1csdme221.epc.mnc003.mcc228.3gppnetwork.org"]

    msg = der.as_bytes()

    assert der.header.length == len(msg)
    assert der.header.is_request is True


def test_dea_create_new():
    # build a diameter-eap-answer with every attribute populated and
    # attempt to parse it
    dea = DiameterEapAnswer()
    dea.session_id = "labdra.gy.mno.net;02472683"
    dea.auth_application_id = constants.APP_EAP_APPLICATION
    dea.auth_request_type = constants.E_AUTH_REQUEST_TYPE_AUTHENTICATE_ONLY
    dea.result_code = constants.E_RESULT_CODE_DIAMETER_SUCCESS
    dea.origin_host = b"dra3.mvno.net"
    dea.origin_realm = b"mvno.net"
    dea.user_name = "diameter"
    dea.eap_payload = b"1"
    dea.eap_reissued_payload = b"2"
    dea.eap_master_session_key = b"ffff"
    dea.eap_key_name = b""  # rfc says should be empty
    dea.multi_round_time_out = 60
    dea.accounting_eap_auth_method = constants.E_ACCOUNTING_AUTH_METHOD_UNDEFINED
    dea.service_type = constants.E_SERVICE_TYPE_FRAMED
    dea.state_class = [b"ff"]
    dea.configuration_token = [b"ab"]
    dea.acct_interim_interval = 30
    dea.error_message = "failure"
    dea.error_reporting_host = b"dra1.mvno.net"
    dea.failed_avp = FailedAvp(additional_avps=[
        Avp.new(constants.AVP_ORIGIN_HOST, value=b"dra2.gy.mno.net")
    ])
    dea.idle_timeout = 30
    dea.authorization_lifetime = 3600
    dea.auth_grace_period = 120
    dea.auth_session_state = constants.E_AUTH_SESSION_STATE_NO_STATE_MAINTAINED
    dea.re_auth_request_type = constants.E_RE_AUTH_REQUEST_TYPE_AUTHORIZE_ONLY
    dea.session_timeout = 7200
    dea.state = b"abcdef"
    dea.reply_message = ["hell0"]
    dea.origin_state_id = 187623
    dea.filter_id = ["1"]
    dea.port_limit = 30
    dea.callback_id = "123"
    dea.callback_number = "41876"
    dea.framed_appletalk_link = 87
    dea.framed_appletalk_network = [876]
    dea.framed_appletalk_zone = b"faba"
    dea.framed_compression = [10]
    dea.framed_interface_id = 1
    dea.framed_ip_address = b"10.0.0.1"
    dea.framed_ipv6_prefix = [b"efefbada"]
    dea.framed_ipv6_pool = b"ffffff"
    dea.framed_ipv6_route = ["2001:db8::/32"]
    dea.framed_ip_netmask = b"255.255.255.0"
    dea.framed_route = ["192.0.2.0/24"]
    dea.framed_pool = b"1"
    dea.framed_ipx_network = 0x02
    dea.framed_mtu = 1500
    dea.framed_protocol = constants.E_FRAMED_PROTOCOL_GANDALF
    dea.framed_routing = constants.E_FRAMED_ROUTING_SEND_AND_LISTEN
    dea.nas_filter_rule = [b"permit in ip from 10.0.0.1 to 10.0.0.99"]
    dea.qos_filter_rule = [b"meter in ip from 10.0.0.1 to 10.0.0.99"]
    dea.tunneling = [Tunneling(
        tunnel_type=constants.E_TUNNEL_TYPE_L2TP,
        tunnel_medium_type=constants.E_TUNNEL_MEDIUM_TYPE_DECNET4,
        tunnel_client_endpoint="172.16.0.12",
        tunnel_server_endpoint="88.15.67.190"
    )]
    dea.redirect_host = ["aaa://diameterproxy.mvno.net"]
    dea.redirect_host_usage = constants.E_REDIRECT_HOST_USAGE_ALL_HOST
    dea.redirect_max_cache_time = 1800
    dea.proxy_info = [ProxyInfo(
        proxy_host=b"swlab.roam.server.net",
        proxy_state=b"\x00\x00"
    )]

    msg = dea.as_bytes()

    assert dea.header.length == len(msg)
    assert dea.header.is_request is False


def test_der_to_dea():
    req = DiameterEapRequest()
    ans = req.to_answer()

    assert isinstance(ans, DiameterEapAnswer)
    assert ans.header.is_request is False

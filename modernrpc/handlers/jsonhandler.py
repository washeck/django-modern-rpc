# coding: utf-8
import json
import logging

from django.utils.module_loading import import_string

from modernrpc.conf import settings
from modernrpc.core import JSONRPC_PROTOCOL, RPCRequest
from modernrpc.exceptions import (RPCParseError, RPCInvalidRequest)
from modernrpc.handlers.base import RPCHandler

try:
    # Python 3
    from json.decoder import JSONDecodeError
except ImportError:
    # Python 2: json.loads will raise a ValueError when loading json
    JSONDecodeError = ValueError

logger = logging.getLogger(__name__)


class JSONRPCBatchResult(object):
    def __init__(self):
        self.results = []


class JSONRPCHandler(RPCHandler):
    protocol = JSONRPC_PROTOCOL

    def __init__(self, entry_point):
        super(JSONRPCHandler, self).__init__(entry_point)

        self.decoder = import_string(settings.MODERNRPC_JSON_DECODER)
        self.encoder = import_string(settings.MODERNRPC_JSON_ENCODER)

    @staticmethod
    def valid_content_types():
        return [
            'application/json',
            'application/json-rpc',
            'application/jsonrequest',
        ]

    def parse_request(self, request_body):
        try:
            payload = json.loads(request_body, cls=self.decoder)
        except JSONDecodeError as err:
            raise RPCParseError(str(err))

        if not isinstance(payload, dict):
            raise RPCInvalidRequest("Bad JSON-RPC payload")

        return RPCRequest(
            payload.get("method"),
            payload.get("params"),
            jsonrpc=payload.get("jsonrpc"),
            request_id=payload.get("id")
        )

    def validate_request(self, rpc_request):
        if not rpc_request.method_name:
            raise RPCInvalidRequest('Missing parameter "method"')
        elif not rpc_request.jsonrpc:
            raise RPCInvalidRequest('Missing parameter "jsonrpc"')
        elif rpc_request.jsonrpc != "2.0":
            raise RPCInvalidRequest('jsonrpc version must be set to 2.0')

    def format_success_data(self, data, **kwargs):
        return {'result': data}

    def format_error_data(self, code, message, **kwargs):
        result = {
            'error': {
                'code': code,
                'message': message,
            }
        }
        if "error_data" in kwargs:
            result["error"]["data"] = kwargs["error_data"]
        return result

    def build_full_result(self, rpc_request, response_content, **kwargs):
        if rpc_request is None:
            rpc_request = RPCRequest(None, None, request_id=None, jsonrpc="2.0")
        elif not getattr(rpc_request, "request_id"):
            return ""

        result_payload = {
            'id': rpc_request.request_id,
            'jsonrpc': rpc_request.jsonrpc,
        }
        result_payload.update(response_content)
        return json.dumps(result_payload, cls=self.encoder)

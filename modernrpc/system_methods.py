# coding: utf-8
from modernrpc.core import ENTRY_POINT_KEY, PROTOCOL_KEY, registry, rpc_method, HANDLER_KEY, XMLRPC_PROTOCOL, \
    REQUEST_KEY, RpcRequest
from modernrpc.exceptions import RPCInvalidParams


@rpc_method(name='system.listMethods')
def __system_list_methods(**kwargs):
    """Returns a list of all methods available in the current entry point"""
    entry_point = kwargs.get(ENTRY_POINT_KEY)
    protocol = kwargs.get(PROTOCOL_KEY)

    return registry.get_all_method_names(entry_point, protocol, sort_methods=True)


@rpc_method(name='system.methodSignature')
def __system_method_signature(method_name, **kwargs):
    """
    Returns an array describing the signature of the given method name.

    The result is an array with:
     - Return type as first elements
     - Types of method arguments from element 1 to N
    :param method_name: Name of a method available for current entry point (and protocol)
    :param kwargs:
    :return: An array describing types of return values and method arguments
    """
    entry_point = kwargs.get(ENTRY_POINT_KEY)
    protocol = kwargs.get(PROTOCOL_KEY)

    method = registry.get_method(method_name, entry_point, protocol)
    if method is None:
        raise RPCInvalidParams('Unknown method {}. Unable to retrieve signature.'.format(method_name))
    return method.signature


@rpc_method(name='system.methodHelp')
def __system_method_help(method_name, **kwargs):
    """
    Returns the documentation of the given method name.

    :param method_name: Name of a method available for current entry point (and protocol)
    :param kwargs:
    :return: Documentation text for the RPC method
    """
    entry_point = kwargs.get(ENTRY_POINT_KEY)
    protocol = kwargs.get(PROTOCOL_KEY)

    method = registry.get_method(method_name, entry_point, protocol)
    if method is None:
        raise RPCInvalidParams('Unknown method {}. Unable to retrieve its documentation.'.format(method_name))
    return method.html_doc


@rpc_method(name='system.multicall', protocol=XMLRPC_PROTOCOL)
def __system_multi_call(calls, **kwargs):
    """
    Call multiple RPC methods at once.

    :param calls: An array of struct like {"methodName": string, "params": array }
    :param kwargs: Internal data
    :type calls: list
    :type kwargs: dict
    :return:
    """
    if not isinstance(calls, list):
        raise RPCInvalidParams('system.multicall first argument should be a list, {} given.'.format(type(calls)))

    handler = kwargs.get(HANDLER_KEY)
    request = kwargs.get(REQUEST_KEY)
    results = []

    for call in calls:

        rpc_request = RpcRequest(call['methodName'], call.get('params'))
        rpc_result = handler.process_request(request, rpc_request)

        if rpc_result.is_error():
            results.append({
                'faultCode': rpc_result.error_code,
                'faultString': rpc_result.error_message,
            })
        else:
            # From https://mirrors.talideon.com/articles/multicall.html:
            # "Notice that regular return values are always nested inside a one-element array. This allows you to
            # return structs from functions without confusing them with faults."
            results.append([rpc_result.success_data])

    return results

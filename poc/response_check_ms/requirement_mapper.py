# Remove abstraction of requirements and check specific elements
# TODO add check response code, content-type and encoding set? with the __check_headers_contains_elem method
__requirement_func_mapping = {
    "ASVS_3.0.1_10.10": lambda headers: __check_headers_contains_elem(
        headers, "Public-Key-Pins"
    ),
    "ASVS_3.0.1_10.11": lambda headers: __check_headers_contains_elem(
        headers, "Strict-Transport-Security"
    ),
    "ASVS_3.0.1_10.12": lambda headers: __check_headers_contains_elem(
        headers, "Strict-Transport-Security", "preload"
    ),
}


def __get_eval_result(status, message, confidence):
    """Builds a evaluation response object from given information

    Parameters:
    status (String): Result of evalution PASSED/FAILED/ERROR
    message (String): Message of evaluation, error on ERROR
    confidence (Number): Confidence level of result (0-100)
    
    Returns:
    dict: Containing the status, message, and confidence level
    """

    return {
        "status": status,
        "message": message,
        "confidenceLevel": confidence,
    }


def __check_headers_contains_elem(headers, element, nested_elem=None):
    """Checks the headers of a response against a given element. 
    Allows checking for a nested element in the given header element.
    E.g. HSTS, HPKP, preloading

    Parameters:
    headers (dict): dictionary of headers from a requests response object
    element (String): Header name to be checked for
    nested_elem (Number): Text to be checked for presence in the given header element
    
    Returns:
    dict: Containing the status, message, and confidence level of the __get_eval_result method
    """

    if element in headers:
        if nested_elem is not None and nested_elem not in headers[element]:
            return __get_eval_result(
                "FAILED", f"No {element} header with {nested_elem} found", 90
            )

        return __get_eval_result(
            "PASSED", f"Detected Header with the value of: {headers[element]}", 90
        )

    else:
        return __get_eval_result("FAILED", f"No {element} header found", 90)


def __check_encodings():
    # TODO add check for not using Base64 etc.
    pass


def __check_session_information():
    # TODO add check for guessable session id/token?
    pass


def evaluate(http_response, requirement):
    """Starts the evaluation of the given response object against the provided requirement
    
    Parameters:
    http_response (requests.Response object): HTTP response object
    requirement (String # TODO change to dict): The to be tested requirement object
    
    Returns:
    dict: Containing the status, message, and confidence level of the __get_eval_result method
    """

    # get the according method for the given requirement and pass it the headers of the response
    eval_result = __requirement_func_mapping[requirement](http_response.headers)
    return eval_result

"""
Lookup for HTTPS queries
"""

from http.client import HTTPSConnection, socket  # type: ignore
from typing import Any, Optional
from urllib.parse import urlencode

from ..utils.constants import CONNECTION_TIMEOUT, EMAIL, USER_AGENT
from ..utils.logger import logger
from .abstract_base import AbstractDataLookup


class HTTPSLookup(AbstractDataLookup):
    """Abstract class to wrap https queries:
    Initialized with the entry to query info about

    Defines:
    - lookup : Self -> Optional[bytes] - performs the queries and returns raw data
    - query : Self -> Optional[BibtexEntry] - performs single query, calls lookup and handle_output

    - domain: str = "localhost" - the domain name e.g. api.crossref.org
    - host : Optional[str] = None - host when different from domain
    - path : str = "/" - the path component of the URL
    - params : dict[str, str] = {} - parameters to add to the URL

    - request : str = "GET" - https request type
    - default_headers : dict[str, str] = ... default http header
    - headers : dict[str, str] = {} - headers to add, overrite default_headers

    all of these have associated methods get_XX : Self -> Type[XX] that can be overridden
    for finer behavior control

    Virtual methods and attributes:
    - handle_output : Self, bytes -> Optional[Result] - parses output into useful result
    """

    domain: str = "localhost"
    host: Optional[str] = None
    path: str = "/"
    params: dict[str, str] = {}

    request: str = "GET"
    default_headers: dict[str, str] = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Email": EMAIL,
    }
    headers: dict[str, str] = {}

    connection_timeout: float = CONNECTION_TIMEOUT

    def get_headers(self) -> dict[str, str]:
        """Return the headers used in an HTTPS request"""
        headers = self.default_headers.copy()
        headers.update(self.headers)
        headers["Host"] = self.get_host()
        return headers

    def get_request(self) -> str:
        """Return the request method to use
        override this if not using self.request (default GET)"""
        return self.request

    def get_domain(self) -> str:
        """Return the path to connect to
        override this if not using self.domain"""
        return self.domain

    def get_host(self) -> str:
        """Return the host header
        override this if not using self.host or self.domain"""
        if self.host is not None:
            return self.host
        return self.get_domain()

    def get_path(self) -> str:
        """Return the path to connect to
        override this if not using self.path"""
        params = self.get_params()
        if params:
            return self.path + "?" + urlencode(params)
        return self.path

    def get_params(self) -> dict[str, str]:
        """Url parameters, can use self.entry to set them
        override this if not using self.path"""
        return self.params

    def get_body(self) -> Optional[Any]:
        """Query body, can use self.entry to set them"""
        return None

    def get_data(self) -> Optional[bytes]:
        """main lookup function
        returns true if the lookup succeeded in finding all info
        false otherwise"""
        domain = self.get_domain()
        request = self.get_request()
        path = self.get_path()
        headers = self.get_headers()
        logger.info(f"{request} https://{domain}{path}")
        # logger.debug(f"{headers}")
        try:
            connection = HTTPSConnection(domain, timeout=self.connection_timeout)
            connection.request(
                request,
                path,
                self.get_body(),
                headers,
            )
            response = connection.getresponse()
            logger.info(f"response: {response.status} {response.reason}")
            if response.status != 200:
                connection.close()
                return None
            data = response.read()
            connection.close()
        except socket.timeout:
            logger.warn("connection timeout")
            return None
        except socket.gaierror as err:
            logger.warn(f"connection error: {err}")
            return None
        return data

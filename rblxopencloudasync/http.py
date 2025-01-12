# MIT License

# Copyright (c) 2022-2025 treeben77

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import time
from typing import Callable, Generic, Optional, TypeVar, Union

import aiohttp

from . import VERSION_INFO, http_session, user_agent
from .exceptions import (
    Conflict,
    Forbidden,
    HttpException,
    NotFound,
    RateLimited,
)

__all__ = ("send_request", "iterate_request", "Operation")

T = TypeVar("T")


async def send_request(
    method: str,
    path: str,
    authorization: Optional[str] = None,
    expected_status: Optional[list[int]] = None,
    retry_max_attempts: int = 2,
    retry_interval_seconds: float = 1,
    retry_interval_exponent: float = 2,
    **kwargs,
) -> tuple[int, Union[str, int, float, dict, list, None], dict]:
    """
    Sends a HTTP request to `https://apis.roblox.com` and returns the result. \
    It is used internally by the library but can also be used by users for \
    unimplemented apis.

    Example:
        This is an example to send a message with the messaging service API:
        ```py
        status, data, headers = await await send_request(
            "POST", f"messaging-service/v1/universes/00000000/topics/{topic}",
            authorization="insert-api-key", json={
                "message": "Hello World!"
            }
        )
        ```

    Args:
        method: The HTTP method to use in uppercase such as `GET` or `POST`.
        path: The HTTP path of the request, excluding the starting `/`, for \
        example `assets/v1/assets`.
        authorization: The value for the `x-api-key` header. Automatically \
        uses `Authorization` header instead if the value begins with \
        `Bearer `.
        expected_status: A list of status codes the function should not \
        handle (such as raise an exception). It is used internally by the \
        library, but can also be used by users to raise errors. *Will not \
        raise any errors when `None`.*
        retry_max_attempts: The number of retries to complete on an 5xx \
        error. Set to 0 for no retries, defaults to 2.
        retry_interval_seconds: The number of seconds between each retry on a \
        5xx error. Set to 0 for no delay interval.
        retry_interval_exponent: The second interval exponenet to apply to \
        `retry_interval_seconds` between each attempt.

    Other parameters:
        params (dict[str, Union[str, int, float, bool]]): A dictionary of \
        query params to send in the request.
        headers (dict[str, str]): A dictionary of headers to include in the \
        request. `user-agent` and `authorization`/`x-api-key` are overwritten.
        json (Union[dict, list, str, int, float, bool]): Any json compatible \
        python object to be sent in the request.
        data (Union[bytes], dict): The data to send with the request. *Can \
        not be used with `json` parameter.*
        timeout (float): The number of seconds until the request times out. \
        Defaults to 15 seconds. Set to `None` for no timeout (not recommended).
    
    Returns:
        A tuple with the first value being the status code, the second value \
        being the response body pre-json decoded if possible, and the last \
        value being the response headers.
    
    Raises:
        HttpException: HTTP status `400`, `401` 5xx`, or another unepexted \
        status returned which is not in `expected_status` and is not `None`.
        Forbidden: HTTP status `403` returned when `expected_status` \
        is not `None` and `403` is not in the list.
        NotFound: HTTP status `401` returned when `expected_status` is not \
        `None` and `401` is not in the list.
        RateLimited: HTTP status `429` returned when `expected_status` is not \
        `None` and `429` is not in the list.
    
    Note:
        The `send_request` function may function slightly differently between \
        the `rblxopencloud` and `rblxopencloudasync` modules.
    """

    global http_session
    if not http_session:
        http_session = aiohttp.ClientSession()

    headers = {"user-agent": user_agent, **kwargs.get("headers", {})}

    if kwargs.get("headers"):
        del kwargs["headers"]

    if authorization:
        headers[
            (
                "authorization"
                if authorization.startswith("Bearer ")
                else "x-api-key"
            )
        ] = authorization

    if path.startswith("/"):
        path = f"cloud/v2{path}"

    if kwargs.get("params"):
        for k, v in kwargs["params"].copy().items():
            if v is None:
                del kwargs["params"][k]
            if type(v) == bool:
                kwargs["params"][k] = str(v).lower()

    if not kwargs.get("timeout"):
        kwargs["timeout"] = 15

    response = await http_session.request(
        method,
        f"https://apis.roblox.com/{path}",
        headers=headers,
        **kwargs,
    )

    if "application/json" in response.headers.get("Content-Type", ""):
        body = await response.json()
    else:
        body = await response.text()

    if VERSION_INFO == "alpha":
        print(f"[DEBUG] {method} /{path} - {response.status}\n{body}")

    if expected_status and response.status not in expected_status:
        if response.status in [400, 401]:
            raise HttpException(response.status, body)
        elif response.status == 403:
            raise Forbidden(response.status, body)
        elif response.status == 404:
            raise NotFound(response.status, body)
        elif response.status == 429:
            raise RateLimited(response.status, body)
        elif response.status >= 500:
            if retry_max_attempts > 0:
                time.sleep(retry_interval_seconds)

                return await send_request(
                    method,
                    path,
                    authorization,
                    expected_status,
                    retry_max_attempts - 1,
                    retry_interval_seconds * retry_interval_exponent,
                    retry_interval_exponent,
                    **kwargs,
                )

            raise HttpException(response.status, body)
        elif response.status_code == 409:
            raise Conflict(response.status, body)
        elif response.status not in expected_status:
            raise HttpException(response.status, body)

    return response.status, body, response.headers


async def iterate_request(
    *args,
    data_key: str,
    cursor_key: str,
    max_yields: int = None,
    post_request_hook: Callable = None,
    **kwargs,
):

    next_cursor, yields = "", 0

    while max_yields is None or yields < max_yields:

        if not kwargs.get("params"):
            kwargs["params"] = {}
        kwargs["params"][cursor_key] = next_cursor if next_cursor else None

        status, data, headers = await send_request(*args, **kwargs)
        if post_request_hook:
            post_request_hook(status, data, headers)

        if not data.get(data_key) or len(data[data_key]) == 0:
            break

        for entry in data[data_key]:
            yield entry

            yields += 1
            if max_yields is not None and yields >= max_yields:
                break

        data_cursor = data.get("nextPageCursor", data.get("nextPageToken"))
        if next_cursor == data_cursor or not data_cursor:
            break

        next_cursor = data_cursor


class Operation(Generic[T]):
    """
    Represents a request to the Roblox API which takes time to complete such \
    as uploading an asset or flushing an experience's memory store.

    Attributes:
        is_done (bool): Wether the operations is known to be complete and \
        [`wait()`][rblxopencloud.Operation.wait] can provide an immedite \
        response.
    """

    def __init__(
        self,
        path: str,
        self_api_key: str,
        return_type: T,
        cached_response: dict = None,
        **return_meta,
    ) -> None:
        self.__path: str = path
        self.__api_key: str = self_api_key
        self.__return_type: T = return_type
        self.__return_meta: dict = return_meta
        self.__cached_response: dict = cached_response
        self.is_done: bool = cached_response is not None

    def __repr__(self) -> str:
        return "<rblxopencloud.Operation>"

    async def fetch_status(self) -> Optional[T]:
        """
        Fetches the current status of the operation. If it is complete, it \
        returns the expected value, otherwise returns `None`.

        Returns:
            The return type as defined by `T`, or `None` if not completed yet.

        Raises:
            HttpException: The request was not successful.
        """

        _, body, _ = await send_request(
            "GET", self.__path, self.__api_key, expected_status=[200]
        )
        if not body.get("done"):
            return None

        self.is_done = True

        if callable(self.__return_type):
            self.__cached_response = body["response"]
            return self.__return_type(body["response"], **self.__return_meta)
        else:
            return self.__return_type

    async def wait(
        self,
        timeout_seconds: Optional[float] = 60,
        interval_seconds: float = 0,
        interval_exponent: float = 1.3,
    ) -> T:
        """
        Continuously checks the status of the operation every \
        `interval_seconds` until complete or after `timeout_seconds` has \
        passed.

        Args:
            timeout_seconds: The number of seconds until the request stops \
            waiting for completion. Can be `None` to wait forever but not \
            recommended.
            interval_seconds: The number of seconds (excluding network time) \
            between every status check.
            interval_exponent: The number multiplier for exponental backoff. \
            Set to 1 for linear intervals.

        Returns:
            The return type as defined by `T`.

        Raises:
            HttpException: The request was not successful.
            TimeoutError: `timeout_seconds` was exceeded.
        """

        if self.__cached_response:
            if callable(self.__return_type):
                return self.__return_type(
                    self.__cached_response, **self.__return_meta
                )
            else:
                return self.__return_type

        import time

        start_time = time.time()
        while True:
            result = await self.fetch_status()
            if result:
                return result

            if timeout_seconds and time.time() - start_time > timeout_seconds:
                raise TimeoutError("Timeout exceeded")

            if interval_seconds > 0:
                time.sleep(interval_seconds)
            interval_seconds *= interval_exponent

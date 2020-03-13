import asyncio
import logging
import urllib
from typing import Any, Dict, Optional

import aiohttp

from .item import Item

USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0"
COOKIE_KEY = "kl-SDL"
COOKIE_VALUE = "199fff2f-4995-f234-4ee7-4d6e140a32c3"


class ColesItem(Item):
    def __init__(self, url: str):
        self._url = url
        self._item_data: Optional[Dict[Any, Any]] = None

    def __eq__(self, other: Any) -> Any:
        return self.url == other.url

    def __hash__(self) -> int:
        return hash(self.url)

    @property
    def url(self) -> str:
        return self._url

    @property
    def name(self) -> Any:
        if self._item_data is None:
            raise ValueError("Item data not present, need to call get_data() first")

        item_name_full = None

        item_entry_view = self._item_data.get("catalogEntryView", [])
        if len(item_entry_view) == 1:
            item_brand = item_entry_view[0].get("m", "Unknown Brand")
            item_name = item_entry_view[0].get("n")
            item_size = item_entry_view[0].get("a", {}).get("O3", [""])[0]

            if item_name is not None:
                item_name_full = "{} {} {}".format(item_brand, item_name, item_size)

        return item_name_full

    @property
    def price(self) -> float:
        if self._item_data is None:
            raise ValueError("Item data not present, need to call get_data() first")

        item_price = 0.0

        item_entry_view = self._item_data.get("catalogEntryView", [])
        if len(item_entry_view) == 1:
            try:
                item_price_str = item_entry_view[0].get("p1", {}).get("l4", 0.0)
                if item_price_str == 0.0:
                    item_price_str = item_entry_view[0].get("p1", {}).get("o", 0.0)

                item_price = float(item_price_str)
            except (TypeError, ValueError):
                pass

        return item_price

    @property
    def discounted_price(self) -> float:
        if self._item_data is None:
            raise ValueError("Item data not present, need to call get_data() first")

        item_price = 0.0

        item_entry_view = self._item_data.get("catalogEntryView", [])
        if len(item_entry_view) == 1:

            try:
                item_price = float(item_entry_view[0].get("p1", {}).get("o", "0.0"))
            except (TypeError, ValueError):
                pass

        return item_price

    async def get_data(self) -> None:
        logger = logging.getLogger("discount_checker")

        if self._item_data is not None:
            return

        url_path_split = urllib.parse.urlparse(self.url).path.split("/")
        if len(url_path_split) < 5:
            self._item_data = {}
            return

        item_name_url = url_path_split[4]
        item_url = "https://shop.coles.com.au/search/resources/store/20601/"\
                   "productview/bySeoUrlKeyword/{}".format(item_name_url)

        headers = {
            "Cookie": "{}={}".format(COOKIE_KEY, COOKIE_VALUE),
            "User-Agent": USER_AGENT
        }

        async with aiohttp.ClientSession(trust_env=True) as session:
            try:
                async with session.get(item_url, headers=headers) as response:
                    response.raise_for_status()
                    self._item_data = await response.json()
            except ValueError as e:
                logger.error("Could not parse JSON from response %s", e)
            except asyncio.TimeoutError as e:
                logger.error("Timed out when querying server %s", e)
            except aiohttp.client_exceptions.ClientResponseError as e:
                logger.error("HTTP Response received not 200 OK %s", e)
            except aiohttp.client_exceptions.ClientPayloadError as e:
                logger.error("Error when reading payload from HTTP response %s", e)
            except aiohttp.client_exceptions.ClientError as e:
                logger.error("Unable to make API request to server %s", e)
            finally:
                if self._item_data is None:
                    self._item_data = {}

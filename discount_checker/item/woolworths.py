import asyncio
import logging
import urllib
from typing import Any, Dict, Optional

import aiohttp

from .item import Item


class WoolworthsItem(Item):
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

        product_data = self._item_data.get("Product")
        if product_data is None:
            product_data = {}

        product_name = product_data.get("Name", None)
        product_size = product_data.get("PackageSize", "")

        if product_name is None:
            return product_name

        return "{} {}".format(product_name, product_size)

    @property
    def price(self) -> float:
        if self._item_data is None:
            raise ValueError("Item data not present, need to call get_data() first")

        item_price = 0.0
        try:
            product_data = self._item_data.get("Product")
            if product_data is None:
                product_data = {}

            item_price = float(product_data.get("WasPrice", 0.0))
        except (TypeError, ValueError):
            pass
        return item_price

    @property
    def discounted_price(self) -> float:
        if self._item_data is None:
            raise ValueError("Item data not present, need to call get_data() first")

        item_price = 0.0
        try:
            product_data = self._item_data.get("Product")
            if product_data is None:
                product_data = {}

            item_price = float(product_data.get("Price", 0.0))
        except (TypeError, ValueError):
            pass
        return item_price

    async def get_data(self) -> None:
        logger = logging.getLogger("discount_checker")

        if self._item_data is not None:
            return

        url_path_split = urllib.parse.urlparse(self.url).path.split("/")

        if len(url_path_split) < 4:
            self._item_data = {}
            return

        item_name_id = url_path_split[3]
        item_url = "https://www.woolworths.com.au/apis/ui/product/detail/{}"\
                   .format(item_name_id)

        async with aiohttp.ClientSession(trust_env=True) as session:
            try:
                async with session.get(item_url) as response:
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

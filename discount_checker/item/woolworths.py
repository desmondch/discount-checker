import asyncio
import logging
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

        product_name = self._item_data.get("Product", {}).get("Name", None)
        return product_name

    @property
    def price(self) -> float:
        if self._item_data is None:
            raise ValueError("Item data not present, need to call get_data() first")

        item_price = 0.0
        try:
            item_price = float(self._item_data.get("Product", {}).get("WasPrice", 0.0))
        except (TypeError, ValueError):
            pass
        return item_price

    @property
    def discounted_price(self) -> float:
        if self._item_data is None:
            raise ValueError("Item data not present, need to call get_data() first")

        item_price = 0.0
        try:
            item_price = float(self._item_data.get("Product", {}).get("Price", 0.0))
        except (TypeError, ValueError):
            pass
        return item_price

    async def get_data(self) -> None:
        logger = logging.getLogger("discount_checker")

        if self._item_data is not None:
            return

        item_name_split = self.url.rsplit("/", 2)
        if len(item_name_split) == 3:
            item_name_id = item_name_split[1]

        item_url = "https://woolworths.com.au/apis/ui/product/detail/{}"\
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

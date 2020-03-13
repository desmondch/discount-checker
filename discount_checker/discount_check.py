import argparse
import asyncio
import logging
import urllib
from typing import Dict, List, Set

from .config import DiscountCheckerConfig, SendTarget
from .item.coles import ColesItem
from .item.item import Item
from .item.woolworths import WoolworthsItem


def get_discounts(args: argparse.Namespace, config: DiscountCheckerConfig) -> None:
    # Setup logging for debugging and error messages
    logger = logging.getLogger("discount_checker")

    console_handler = logging.StreamHandler()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))
    else:
        logger.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    logger.addHandler(console_handler)

    item_set = set()
    base_urls = ["shop.coles.com.au", "www.woolworths.com.au"]

    for target in config.send_targets:
        logger.debug("Processing items for %s (%s)", target.name, target.email)
        for item_url in target.items:
            parsed_url = urllib.parse.urlparse(item_url)

            if parsed_url.netloc not in base_urls:
                print("URL {} was not recognised as a valid link to check.".format(item_url))
            else:
                item: Item
                if parsed_url.netloc == "shop.coles.com.au":
                    item = ColesItem(item_url)
                    logger.debug("Creating Coles item for URL: %s", item_url)
                elif parsed_url.netloc == "www.woolworths.com.au":
                    item = WoolworthsItem(item_url)
                    logger.debug("Creating Woolworths item for URL: %s", item_url)

                item_set.add(item)

    # Asynchronously make all the HTTP requests to get the price data for each item
    # from all store webpages
    logger.debug("Starting async loop to obtain data for all items.")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_data_all_items(item_set))
    loop.close()
    logger.debug("Ended async loop to obtain data for all items.")

    for target in config.send_targets:
        if args.debug:
            display_target_items(item_set, target)
        else:
            print("")


async def get_data_all_items(items: Set[Item]) -> None:
    get_data_functions = []

    for item in items:
        get_data_functions.append(item.get_data())

    await asyncio.gather(*get_data_functions)


def display_target_items(item_set: Set[Item], target: SendTarget) -> None:
    # Inefficient O(n^2) implementation to find appropriate items
    items_by_store_type: Dict[str, List[Item]] = {}

    for item_url in target.items:
        for item in item_set:
            if item_url == item.url:
                if isinstance(item, ColesItem):
                    items_by_store_type.setdefault("Coles", []).append(item)
                elif isinstance(item, WoolworthsItem):
                    items_by_store_type.setdefault("Woolworths", []).append(item)

    for store_type in items_by_store_type:
        print(">>>>>>>>STORE: {}<<<<<<<<".format(store_type))
        for item in items_by_store_type[store_type]:
            if item.name:
                # Ensure price and discounted price are not None / 0.0
                if item.price and item.discounted_price:
                    print("Item: {}".format(item.name))
                    print("Was: ${:.2f}".format(item.price))
                    print("Now: ${:.2f}".format(item.discounted_price))
                else:
                    print("Error getting price for item {}, URL: {}".format(item.name, item.url))
            else:
                print("Error getting name for item at URL: {}".format(item.url))

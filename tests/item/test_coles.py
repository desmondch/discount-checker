# pylint: disable=line-too-long
import pytest
import vcr
from discount_checker.item.coles import ColesItem


@pytest.mark.asyncio
@pytest.mark.parametrize("url,item_data", [
    (
        "https://shop.coles.com.au/a/national/product/arnotts-biscuits-assorted-creams",
        {"name": "Arnott's Assorted Creams Biscuits 500g", "price": 5.5, "discounted_price": 4.0}
    ),
    (
        "https://shop.coles.com.au/a/national/product/sunburst-zooper-dooper-water-ice",
        {"name": "Zooper Dooper 8 Cosmic Flavours Water Ice 70mL Tubes 24 pack", "price": 5.8, "discounted_price": 4.6}
    ),
    (
        "https://shop.coles.com.au/a/national/product/coca-cola-soft-drink-coke-375ml-cans-7365777p",
        {"name": "Coca-Cola Classic Coke Multipack Cans 375mL 24 pack", "price": 31.80, "discounted_price": 18.40}
    ),
    (
        "https://shop.coles.com.au/a/national/product/cadbury-caramilk-egg-bag",
        {"name": "Cadbury Caramilk Egg Bag 230g", "price": 8.0, "discounted_price": 6.0}
    ),
    (
        "https://shop.coles.com.au/a/national/product/coles-milk-full-cream-439693p",
        {"name": "Coles Full Cream Milk 2L", "price": 2.39, "discounted_price": 2.39}
    ),
    (
        "https://shop.coles.com.au/a/national/product/coles-pasta-fettuccini",
        {"name": "Coles Fettuccine Pasta 500g", "price": 1.2, "discounted_price": 1.2}
    ),
    (
        "https://shop.coles.com.au/a/national/product/sirena-tuna-in-springwater-9442937p",
        {"name": "Sirena Tuna In Springwater 425g", "price": 7.0, "discounted_price": 7.0}
    ),
    (
        "https://shop.coles.com.au/a/national/product/coles-bakery-bread-white-toast-baked-in-store",
        {"name": "Coles Bakery White Toast Bread Loaf 680g", "price": 2.0, "discounted_price": 2.0}
    )
])
@vcr.use_cassette("vcr/coles_get_data_valid_item.yml", record_mode="all")
async def test_coles_get_data_valid_item(url, item_data):
    item = ColesItem(url)
    await item.get_data()

    assert item.name == item_data["name"]
    assert item.price == item_data["price"]
    assert item.discounted_price == item_data["discounted_price"]


@pytest.mark.parametrize("url1,url2,expected_result", [
    ("https://shop.coles.com.au/a/national/product/coles-milk-full-cream-439693p",
     "https://shop.coles.com.au/a/national/product/coles-milk-full-cream-439693p",
     True),
    ("https://shop.coles.com.au/a/national/product/coles-milk-full-cream-439693p",
     "https://shop.coles.com.au/a/national/product/coles-bakery-bread-white-toast-baked-in-store",
     False),
    ("https://shop.coles.com.au/a/national/product/coca-cola-soft-drink-coke-375ml-cans-7365777p",
     "https://shop.coles.com.au/a/national/product/coles-pasta-fettuccini",
     False)]
)
def test_coles_eq(url1, url2, expected_result):
    item1 = ColesItem(url1)
    item2 = ColesItem(url2)

    assert (item1 == item2) == expected_result


def test_coles_hashable():
    item = ColesItem("https://shop.coles.com.au/a/national/product/coles-pasta-fettuccini")
    assert hash(item)

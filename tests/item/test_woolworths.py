# pylint: disable=line-too-long
import pytest
import vcr
from discount_checker.item.woolworths import WoolworthsItem


@pytest.mark.asyncio
@pytest.mark.parametrize("url,item_data", [
    (
        "https://www.woolworths.com.au/shop/productdetails/32731/coca-cola-bottle",
        {"name": "Coca Cola Bottle  1.25l", "price": 3.0, "discounted_price": 1.8}
    ),
    (
        "https://www.woolworths.com.au/shop/productdetails/922933/decor-microsafe-container-noodle-bowl",
        {"name": "Decor Microsafe Container Noodle Bowl each", "price": 8.0, "discounted_price": 4.0}
    ),
    (
        "https://www.woolworths.com.au/shop/productdetails/729421/steggles-frozen-chicken-kiev",
        {"name": "Steggles Frozen Chicken Kiev  350g", "price": 8.0, "discounted_price": 4.0}
    ),
    (
        "https://www.woolworths.com.au/shop/productdetails/807383/woolworths-drought-relief-full-cream-milk",
        {"name": "Woolworths Drought Relief Full Cream Milk 2l", "price": 2.39, "discounted_price": 2.39}
    ),
    (
        "https://www.woolworths.com.au/shop/productdetails/53815/papa-giuseppi-s-our-big-pizza-cheese-bacon-melt",
        {"name": "Papa Giuseppi's Our Big Pizza Cheese & Bacon Melt 630g", "price": 10.0, "discounted_price": 10.0}
    ),
    (
        "https://www.woolworths.com.au/shop/productdetails/829281/twinings-extra-strong-english-breakfast-tea-bags",
        {"name": "Twinings Extra Strong English Breakfast Tea Bags 80 pack", "price": 11.00, "discounted_price": 11.00}
    ),
    (
        "https://www.woolworths.com.au/shop/productdetails/38018/harris-ground-coffee-espresso",
        {"name": "Harris Ground Coffee Espresso 1kg", "price": 17.0, "discounted_price": 15.0}
    )
])
@vcr.use_cassette("vcr/woolworths_get_data_valid_item.yml", record_mode="none")
async def test_woolworths_get_data_valid_item(url, item_data):
    item = WoolworthsItem(url)
    await item.get_data()

    assert item.name == item_data["name"]
    assert item.price == item_data["price"]
    assert item.discounted_price == item_data["discounted_price"]


@pytest.mark.asyncio
@pytest.mark.parametrize("url,item_data", [
    (
        "https://www.woolworths.com.au/shop/productdetails/111111/invalid-item",
        {"name": None, "price": 0.0, "discounted_price": 0.0}
    ),
    (
        "https://www.woolworths.com.au/shop/productdetails/222222/invalid-item",
        {"name": None, "price": 0.0, "discounted_price": 0.0}
    )
])
@vcr.use_cassette("vcr/woolworths_get_data_invalid_item.yml", record_mode="none")
async def test_woolworths_get_data_invalid_item(url, item_data):
    item = WoolworthsItem(url)
    await item.get_data()

    assert item.name == item_data["name"]
    assert item.price == item_data["price"]
    assert item.discounted_price == item_data["discounted_price"]


@pytest.mark.asyncio
@pytest.mark.parametrize("url,item_data", [
    (
        "https://www.woolworths.com.au/shop/productdetails/38153/annalisa-tomatoes-diced",
        {"name": "Annalisa Tomatoes Diced 400g", "price": 0.0, "discounted_price": 0.0}
    ),
    (
        "https://www.woolworths.com.au/shop/productdetails/223995/sunrice-jasmine-rice-thai",
        {"name": "Sunrice Jasmine Rice Thai 5kg", "price": 0.0, "discounted_price": 0.0}
    ),
    (
        "https://www.woolworths.com.au/shop/productdetails/761072/nudie-nothing-but-coconut-water-straight-up",
        {"name": "Nudie Nothing But Coconut Water Straight Up 1l", "price": 0.0, "discounted_price": 0.0}
    )
])
@vcr.use_cassette("vcr/woolworths_get_data_item_no_longer_exists.yml", record_mode="none")
async def test_woolworths_get_data_item_no_longer_exists(url, item_data):
    item = WoolworthsItem(url)
    await item.get_data()

    assert item.name == item_data["name"]
    assert item.price == item_data["price"]
    assert item.discounted_price == item_data["discounted_price"]


@pytest.mark.parametrize("url1,url2,expected_result", [
    ("https://www.woolworths.com.au/shop/productdetails/807383/woolworths-drought-relief-full-cream-milk",
     "https://www.woolworths.com.au/shop/productdetails/807383/woolworths-drought-relief-full-cream-milk",
     True),
    ("https://www.woolworths.com.au/shop/productdetails/807383/woolworths-drought-relief-full-cream-milk",
     "https://www.woolworths.com.au/shop/productdetails/223995/sunrice-jasmine-rice-thai",
     False),
    ("https://www.woolworths.com.au/shop/productdetails/32731/coca-cola-bottle",
     "https://www.woolworths.com.au/shop/productdetails/829281/twinings-extra-strong-english-breakfast-tea-bags",
     False)]
)
def test_woolworths_eq(url1, url2, expected_result):
    item1 = WoolworthsItem(url1)
    item2 = WoolworthsItem(url2)

    assert (item1 == item2) == expected_result


def test_woolworths_hashable():
    item = WoolworthsItem("https://www.woolworths.com.au/shop/productdetails/248348/annalisa-beans-red-kidney")
    assert hash(item)

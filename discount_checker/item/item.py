import abc


class Item(abc.ABC):
    @property
    def url(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_data(self) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def price(self) -> float:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def discounted_price(self) -> float:
        raise NotImplementedError

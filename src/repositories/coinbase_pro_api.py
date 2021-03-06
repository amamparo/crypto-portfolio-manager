from abc import ABC, abstractmethod
from math import floor
from typing import List, Union

from cbpro import AuthenticatedClient


class AbstractCoinbaseProApi(ABC):
    @abstractmethod
    def get_tradeable_crypto_symbols(self) -> List[str]:
        pass

    @abstractmethod
    def get_cash_balance(self) -> float:
        pass

    @abstractmethod
    def get_non_empty_crypto_wallets(self) -> List[dict]:
        pass

    @abstractmethod
    def buy(self, symbol: str, fiat_amount: Union[float, str]) -> None:
        pass

    @abstractmethod
    def sell(self, symbol: str, quantity: Union[float, str]) -> None:
        pass


class CoinbaseProApi(AbstractCoinbaseProApi):
    def __init__(self, key: str, secret: str, passphrase: str):
        self.__cbp_client = AuthenticatedClient(key, secret, passphrase)

    def get_tradeable_crypto_symbols(self) -> List[str]:
        return [
            x['base_currency'] for x in self.__cbp_client.get_products()
            if x['quote_currency'] == 'USD'
               and not (x['limit_only'] or x['post_only'] or x['cancel_only'] or x['trading_disabled'])
        ]

    def get_cash_balance(self) -> float:
        return float(next(x for x in self.__cbp_client.get_accounts() if x['currency'] == 'USD')['balance'])

    def get_non_empty_crypto_wallets(self) -> List[dict]:
        return [
            x for x in self.__cbp_client.get_accounts()
            if x['currency'] != 'USD' and float(x['available']) > 0
        ]

    def buy(self, symbol: str, fiat_amount: Union[float, str]) -> None:
        self.__cbp_client.place_market_order(
            product_id='%s-USD' % symbol,
            side='buy',
            funds=str(floor(float(fiat_amount) * 100) / 100)
        )

    def sell(self, symbol: str, quantity: Union[float, str]) -> None:
        self.__cbp_client.place_market_order(
            product_id='%s-USD' % symbol,
            side='sell',
            size=str(quantity)
        )

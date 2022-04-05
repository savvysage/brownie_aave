from brownie import interface, network, config
from scripts.common import get_account


def get_weth():
    """
    Mints WETH by depositing ETH.
    """
    account = get_account()
    weth = interface.IWeth(
        config["networks"][network.show_active()]["contracts"]["weth"]
    )
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    tx.wait(1)
    print("Received 0.1 WETH")


def main():
    get_weth()

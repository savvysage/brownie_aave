from scripts.aave_borrow import (
    get_account,
    get_asset_price,
    get_lending_pool,
    approve_erc20,
)
from brownie import network, config


def test_get_asset_price():
    # Arrange / Act
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["contracts"]["dai_eth_price_feed"]
    )
    # Assert
    assert dai_eth_price > 0


def test_get_lending_pool():
    # Arrange / Act
    lending_pool = get_lending_pool()
    # Assert
    assert lending_pool is not None


def test_approve_erc20():
    # Arrange
    account = get_account()
    lending_pool = get_lending_pool()
    amount = 100000000000000000  # 0.1
    weth_address = config["networks"][network.show_active()]["contracts"]["weth"]
    # Act
    tx = approve_erc20(weth_address, lending_pool.address, amount, account)
    # Assert
    assert tx is not True

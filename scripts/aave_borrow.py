from brownie import interface, network, config
from scripts.common import get_account
from scripts.get_weth import get_weth
from web3 import Web3


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["contracts"][
            "lending_pool_addresses_provider"
        ]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(address, spender, amount, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrows_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrows_eth = Web3.fromWei(available_borrows_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow {available_borrows_eth} worth of ETH.")
    return (float(available_borrows_eth), float(total_debt_eth))


def get_asset_price(price_feed_address):
    price_feed = interface.IAggregatorV3(price_feed_address)
    latest_price = price_feed.latestRoundData()[1]
    return float(Web3.fromWei(latest_price, "ether"))


def repay(asset_address, amount, lending_pool, account):
    approve_erc20(asset_address, lending_pool.address, amount, account)
    repay_tx = lending_pool.repay(
        asset_address, amount, 1, account.address, {"from": account}
    )
    repay_tx.wait(1)


def main():
    account = get_account()
    weth_address = config["networks"][network.show_active()]["contracts"]["weth"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    amount = Web3.toWei(0.1, "ether")
    approve_erc20(weth_address, lending_pool.address, amount, account)
    print("Depositing WETH...")
    deposit_tx = lending_pool.deposit(
        weth_address, amount, account.address, 0, {"from": account}
    )
    deposit_tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["contracts"]["dai_eth_price_feed"]
    )
    print(f"The DAI/ETH price is {dai_eth_price}")
    dai_address = config["networks"][network.show_active()]["contracts"]["dai"]
    dai_amount_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    print(f"Borrowing {dai_amount_to_borrow} DAI...")
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(dai_amount_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("Borrowed!")
    get_borrowable_data(lending_pool, account)
    print("Repaying borrowed DAI...")
    repay(dai_address, Web3.toWei(dai_amount_to_borrow, "ether"), lending_pool, account)
    print("Repaid!")
    get_borrowable_data(lending_pool, account)
    print("You just deposited, borrowed, and repayed on Aave!")

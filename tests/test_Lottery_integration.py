from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
import pytest, time
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS, 
    fund_with_link, 
    get_account, 
    get_contract
)

def test_can_pick_winner_integration():
    #arrange
    lottery = deploy_lottery()
    account = get_account()
    if network.show_active()  in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #act
    lottery.startLottery({"from": account}), 
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance == 0
from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery, end_lottery
from web3 import Web3
import pytest
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS, 
    fund_with_link, 
    get_account, 
    get_contract
)

def test_get_entrance_fee():
    #arrange
    lottery = deploy_lottery()
    #act
    expected_entrance_fee = Web3.toWei(50/2000, "ether")
    entrance_fee = lottery.getEntranceFee()
    #assert
    print(f"expected_entrance_fee is: {expected_entrance_fee}")
    print(f"entrance_fee is {entrance_fee}")
    assert entrance_fee == expected_entrance_fee

def test_cant_enter_unless_started():
    #arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    #act/assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})
        
def test_can_end_lottery():
    #arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account}), 
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    assert end_lottery()
    
    
def test_can_pick_winner():
    #arrange
    lottery = deploy_lottery()
    account = get_account()
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #act
    lottery.startLottery({"from": account}), 
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestRandomness"]["requestId"]
    STATIC_RNG = 675
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )
    start_balance_account = account.balance()
    balance_of_lottery = lottery.balance()
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == start_balance_account + balance_of_lottery
    
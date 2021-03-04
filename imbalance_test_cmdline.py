import os
import time
import random
import argparse
from User import *
from Advertiser import *
from Contract import *
from collections import defaultdict

def send_money(sender, receiver, send_amount):
    def wait_for_confirmation(algodclient, txid):
        last_round = algodclient.status().get('last-round')
        txinfo = algodclient.pending_transaction_info(txid)
        while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
            last_round += 1
            algodclient.status_after_block(last_round)
            txinfo = algodclient.pending_transaction_info(txid)
        with open(os.path.join(os.path.dirname(__file__), "debug.log"), "a+") as fp:
            fp.write("Money transferring transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')) + "\n")
        return True

    params = sender.algod_client.suggested_params()
    received = False
    while (not received):
        try:
            txn = transaction.PaymentTxn(sender.account_public_key, params, receiver.account_public_key, send_amount)
            signed_txn = txn.sign(sender.account_private_key)
            sender.algod_client.send_transactions([signed_txn])
            received = wait_for_confirmation(sender.algod_client, txid = signed_txn.transaction.get_txid())
        except:
            pass
    wait_for_confirmation(sender.algod_client, txid = signed_txn.transaction.get_txid())

def test_main(init, set_num, cate_num, adv_nums, repeat_times):
    if int(key) == 1:
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC"
    elif int(key) == 2:
        API_key = "7iNfo9pqXu4TbDwzzR6oB6yqcnxcpLwm36HdRHTu"
    elif int(key) == 3:
        API_key = "CdYVr07ErYa3VNessIks1aPcmlRYPjfZ34KYF7TF"
        
    algod_address = "https://testnet-algorand.api.purestake.io/ps2"
    index_address = "https://testnet-algorand.api.purestake.io/idx2"

    if os.path.exists(os.path.join(os.path.dirname(__file__), "debug.log")):
        os.remove(os.path.join(os.path.dirname(__file__), "debug.log"))
    if os.path.exists(os.path.join(os.path.dirname(__file__), "account.txt")):
        os.remove(os.path.join(os.path.dirname(__file__), "account.txt"))

    if os.path.exists(os.path.join(os.path.dirname(__file__), "verify.log")):
        os.remove(os.path.join(os.path.dirname(__file__), "verify.log"))
    if os.path.exists(os.path.join(os.path.dirname(__file__), "search.log")):
        os.remove(os.path.join(os.path.dirname(__file__), "search.log"))

    temp_info = account.generate_account()
    user = User(API_key, algod_address, index_address, mnemonic.from_private_key(temp_info[0]))
    user.login()

    banker = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        algod_address = algod_address,
        index_address = index_address,
        passphrase = "code thrive mouse code badge example pride stereo sell viable adjust planet text close erupt embrace nature upon february weekend humble surprise shrug absorb faint")
    banker.login()

    if init == True:
        print("Building contract app...\n")
        content_info = mnemonic.from_private_key(account.generate_account()[0])
        temp = Advertiser(API_key, algod_address, index_address, content_info)
        temp.login()
        send_money(banker, temp, 15000000)
        contract = Contract(API_key, algod_address, index_address, content_info)
        contract.create_code()
        contract.compile_code()
        contract.init_contract(cate_num)
        # distinguish the testing results of different params
        contract.log_file = "debug_adv_set_" + str(set_num) + "_cate_" + str(cate_num) + ".log"
        with open(os.path.join(os.path.dirname(__file__), "account_cate_" + str(cate_num) + "_set_" + str(set_num) + ".txt"), "w") as fp:
            fp.write(content_info)
        print("Contract application building complete\n")

        print("Adding advertisers...\n")
        adv_list = defaultdict(list)
        
        for idx in range(cate_num):
            for _ in range(adv_nums[idx]):
                info = account.generate_account()
                adv = Advertiser(API_key, algod_address, index_address, mnemonic.from_private_key(info[0]))
                adv.login()
                input_categories = ["Category" + str(idx + 1)]
                adv_list["Category" + str(idx + 1)].append(adv)
                adv.assign_category(input_categories)
                send_money(banker, adv, 11000000)
                time.sleep(3)
                contract.opt_in_app(adv) 
                time.sleep(3)
        print("Advertiser opting-in complete\n")
        time.sleep(5)

    elif init == False:
        print("Building contract app...\n")
        with open(os.path.join(os.path.dirname(__file__), "account_cate_" + str(cate_num) + "_set_" + str(set_num) + ".txt"), "r") as fp:
            content_info = fp.readline()
        contract = Contract(API_key, algod_address, index_address, content_info)
        contract.log_file = "debug_adv_set_" + str(set_num) + "_cate_" + str(cate_num) + ".log"
        contract.create_code()
        contract.compile_code()
        print("Contract application checking complete\n")

        for _ in range(repeat_times):
            for idx in range(cate_num): 
                input_categories = ["Category" + str(idx + 1)]
            info = account.generate_account()
            adv = Advertiser(API_key, algod_address, index_address, mnemonic.from_private_key(info[0]))
            adv.login()
            adv.assign_category(input_categories)
            send_money(banker, adv, 11000000)
            contract.opt_in_app(adv) 
            
            # search & online hash testing
            print("Testing searching capability of smart contract...\n")
            search_category = "Category1"
            start = time.time()
            contract.full_search(user, search_category)
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of search " + search_category + " is: " + str(time.time() - start) + "\n")

            time.sleep(3)
            start = time.time()
            contract.create_hash_local_file(user)
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of hash local file creation is: " + str(time.time() - start) + "\n")

            start = time.time()
            local_hexdigest = contract.compute_local_hash(user, "Category1")
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of local hash computation " + search_category + " is: " + str(time.time() - start) + "\n")

            start = time.time()
            online_hexdigest = contract.search_hash(user, "Category1")
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of on-chain hash searching " + search_category + " is: " + str(time.time() - start) + "\n")   
            assert(local_hexdigest == online_hexdigest)

            # update testing
            print("Testing updating capability of smart contract...\n")
            start = time.time()
            contract.update_app(adv)
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of updating one advertiser in " + search_category + " is: " + str(time.time() - start) + "\n")

            time.sleep(5)
            start = time.time()
            contract.create_hash_local_file(user)
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of hash local file creation is: " + str(time.time() - start) + "\n")

            start = time.time()
            local_hexdigest = contract.compute_local_hash(user, "Category1")
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of local hash computation " + search_category + " is: " + str(time.time() - start) + "\n")

            start = time.time()
            online_hexdigest = contract.search_hash(user, "Category1")
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of on-chain hash searching " + search_category + " is: " + str(time.time() - start) + "\n")           
            assert(local_hexdigest == online_hexdigest)

            # close out testing
            print("Testing closing out capability of smart contract...\n")
            start = time.time()
            contract.close_out_app(adv)
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of closing out one advertiser in " + search_category + " is: " + str(time.time() - start) + "\n")

            time.sleep(5)
            start = time.time()
            contract.create_hash_local_file(user)
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of hash local file creation is: " + str(time.time() - start) + "\n")

            start = time.time()
            local_hexdigest = contract.compute_local_hash(user, "Category1")
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of local hash computation " + search_category + " is: " + str(time.time() - start) + "\n")

            start = time.time()
            online_hexdigest = contract.search_hash(user, "Category1")
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of on-chain hash searching " + search_category + " is: " + str(time.time() - start) + "\n")         
            assert(local_hexdigest == online_hexdigest)


if __name__ == "__main__":
    """
    CHANGE PARAMS HERE TO LAUNCH DIFFERENT MODE
    """
    def str2bool(input_cmd):
        if isinstance(input_cmd, bool):
            return input_cmd
        if input_cmd.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif input_cmd.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    parser = argparse.ArgumentParser(description='Running the imbalanced testing of blockchain in cmd mode.')
    parser.add_argument('-i', '--init', type=str2bool,
        help='The initial mode of round test')
    parser.add_argument('-k', '--key', type=int,
        help='The index of key selected')
    parser.add_argument('-s', '--set-num', type=int,
        help='The index of advertiser set to generate')
    parser.add_argument('-r', '--repeat-times', type=int,
        help='The repeating times of the testing (init == False)')

    args = parser.parse_args(sys.argv[1:])
    init = args.init
    key = args.key
    set_num = args.set_num
    repeat_times = args.repeat_times

    cate_num = 6
    adv_nums_set = [
        [50,100,100,100,125,125],
        [50,50,100,100,100,200],
        [25,25,50,50,50,400],
        [10,10,10,20,50,500]
    ]

    assert(type(init) is bool)
    assert(type(cate_num) is int)
    assert(type(set_num) is int)
    assert(set_num < len(adv_nums_set))
    assert(type(adv_nums_set) is list)
    assert(type(repeat_times) is int)

    adv_nums = adv_nums_set[set_num]
    assert(type(adv_nums) is list)
    assert(cate_num == len(adv_nums))
    test_main(init, set_num, cate_num, adv_nums, repeat_times)
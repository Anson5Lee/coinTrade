#!/usr/bin/python
import datetime
from setup import *
import okex.spot_obj as spot_obj
from common import db_api
from policy import run_policy, send_report

if __name__ == "__main__":
    pair = 'dpy_eth'
    target_coin = 'dpy'
    base_coin = 'eth'
    ok_spot = spot_obj.SpotClass(pair, '1day', 7, debug=True)

    # cancel all unfinished orders
    print('Cancel all orders')
    ok_spot.cancel_orders()

    # update pending orders in database
    print('Update pending orders')
    orders = db_api.get_pending_orders()
    for item in orders:
        order = ok_spot.get_order(item['order_id'])
        if order is not None:
            db_api.update_order(order)

    # re-order
    print('Send new orders')
    run_policy(ok_spot, float_digits=8, target_coin=target_coin, base_coin=base_coin)

    # update account in database
    print('Update account')
    for i in ok_spot.get_available_coins():
        db_api.insert_account(i)

    # send report
    print('Send report')
    end_time = datetime.datetime.now()
    begin_time = end_time - datetime.timedelta(days=3)
    orders = db_api.get_orders_by_time(begin_time.timestamp(), end_time.timestamp())
    accounts = db_api.get_accounts_by_time(begin_time.timestamp(), end_time.timestamp())
    send_report(orders, accounts, email_receiver)

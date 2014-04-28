#!/usr/bin/env python3

import pickle

dump_file_name = "result.txt"


if __name__ == "__main__":
    dump_file = open(dump_file_name, "rb")
    shops = pickle.load(dump_file)
    dump_file.close()
    print("shop_id/member_id/rank/taste/environment/service")
    for shop in shops:
        shop_id = shop[0]
        for i in range(2, len(shop)):
            review = shop[i]
            print("%(shop_id)d/%(member_id)d/%(rank)d/%(taste)d/%(environment)d/%(service)d" % {
                "shop_id": shop_id,
                "member_id": review[0],
                "rank": review[1],
                "taste": review[2],
                "environment": review[3],
                "service": review[4]
                })

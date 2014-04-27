#!/usr/bin/env python3

import os
import pickle


if __name__ == "__main__":
    reviews = []
    for i in range(300):
        dump_file = open("data/%d.txt" % (i + 1), "rb")
        review = pickle.load(dump_file)
        dump_file.close()
        reviews += review
    shop = []
    shop_name = []
    for review in reviews:
        if review[0] not in shop_name:
            shop_name.append(review[0])
            shop.append([review[0], 0])
        shop_index = shop_name.index(review[0])
        shop[shop_index][1] += 1
        shop[shop_index].append(review[1:])
    shop.sort(key=lambda s: s[1], reverse=True)
    dump_file = open("result.txt", "wb")
    pickle.dump(shop, dump_file)
    dump_file.close()

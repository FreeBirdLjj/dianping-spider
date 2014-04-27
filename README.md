# dianping-spider

Get some reviews of some members of dianping and sort by the mentioned times of the shop.

## Requirement

* `python3`, which should be found by `/usr/bin/env`.
* bs4, the html-parser of python3.
* urllib, to get something via the net.

## Notes

* Now the version can only work on a UNIX/UNIX-like OS, because it requires a '/' spiliter in path (maybe solved in the future).
* It seems like that [dianping](http://www.dianping.com/) is against spider, so the `dump.py` may block sometime. But it doesn't matter, just kill and restart it (after rest for a while), it will continue to work.

## Usage

Simply use:

```sh
./dump.py
./sort.py
./conv.py > res_table.txt
```

And it will download some reviews of 300 members in Shanghai of [dianping](http://www.dianping.com), 300 reviews per member at most and 90,000 in total by default.

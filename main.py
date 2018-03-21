#!/usr/bin/python
# main.py
import argparse
from nian import Nian

exports = ["markdown", "json", "html", "csv", "mongodb", "mysql"]

if __name__ == '__main__':
    print('main start')
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--export", type=str,
                        help="increase output verbosity")
    parser.add_argument("-u", "--uid", type=int,
                        help="increase output verbosity")
    parser.add_argument("-s", "--shell", type=str,
                        help="increase output verbosity")
    args = parser.parse_args()
    if args.export not in exports:
        print('args error')
        exit(0)
    page = 1
    nian = Nian('http://api.nian.so/')
    nian.init_user(args.uid, args.shell)
    nian.init_export_dir(args.uid)
    result = nian.get_dreams(page)
    nian.export_dreams(args.export, result)
    for i in result:
        dream = nian.get_dream_steps(i['id'])
        print(dream)
        nian.get_comment_steps(dream)
        nian.export_dream_steps()
    print(result)

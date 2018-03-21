#!/usr/bin/python
# main.py
import argparse
from nian import Nian

exports = ["markdown", "json", "html", "csv", "mongodb", "mysql"]

if __name__ == '__main__':
    print('main start')
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--export", type=str,
                        help="export method")
    parser.add_argument("-u", "--uid", type=int,
                        help="uid")
    parser.add_argument("-s", "--shell", type=str,
                        help="shell")
    parser.add_argument("--email", type=str,
                        help="email")
    parser.add_argument("-p", "--password", type=str,
                        help="password")
    args = parser.parse_args()
    if args.export not in exports:
        print('args error')
        exit(0)
    nian = Nian('http://api.nian.so/')
    if args.email and args.password:
        nian.login(args.email, args.password)
    elif args.shell and args.uid:
        nian.init_user(args.uid, args.shell)
    else:
        print('args error')
        exit(0)
    nian.init_export_dir(args.uid)
    result = nian.get_dreams()
    nian.export_dreams_images(result)
    for i in result:
        dream = nian.get_dream_steps(i['id'], method=args.export)
        step = nian.get_comment_steps(dream)
        nian.export_dream_steps(step, args.export, i['id'])
    nian.export_dreams(args.export)

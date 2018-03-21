#!/usr/bin/env python
# coding: utf-8
import csv
import hashlib
import json
import os

import requests
import time

import config
from jinja2 import Environment, FileSystemLoader


class Nian():
    def __init__(self, base_url):
        self.base_url = base_url
        self.dreams = []

    def init_user(self, uid, shell):
        self.uid = uid
        self.shell = shell

    def init_export_dir(self, uid):
        self.export_dir = 'exports/' + str(self.uid) + '/'
        self.image_dir = 'exports/images/' + str(self.uid) + '/steps/'
        self.image_dream_dir = 'exports/images/' + str(self.uid) + '/dreams/'
        self.make_dir(self.export_dir)
        self.make_dir(self.image_dir)
        self.make_dir(self.image_dream_dir)

    def make_dir(self, dirname):
        is_exists = os.path.exists(dirname)
        if not is_exists:
            os.makedirs(dirname)

    def get_dreams(self, page=1):
        is_next = True
        result = []
        while is_next:
            response = self._get(config.api_url['user'] + str(self.uid) + config.api_url['get_dreams'], {
                'shell': self.shell,
                'uid': self.uid,
                'page': page
            })
            dreams = response['data']['dreams']
            if len(dreams) <= int(response['data']['perPage']):
                is_next = False
            page = page + 1
            result.extend(dreams)
        return result

    def export_dreams_images(self, result):
        images = []
        for i in result:
            images.append(i['image'])
        self.download_img(images, 'http://img.nian.so/dream/', self.image_dream_dir)

    def export_dreams(self, method):
        self.export(method, self.dreams, 'dreams', template='dreams',
                    csv_header=['id', 'uid', 'user', 'title', 'content', 'lastdate', 'image', 'like', 'step',
                                'like_stepal_users', 'joined', 'total_users', 'like_step', 'editors', 'tags', 'joined',
                                'followed', 'private', 'percent', 'isliked', 'followers', 'cover', 'permission',
                                'is_friend'])

    def get_dream_steps(self, dream_id, page=1, method=None):
        is_next = True
        result = []
        while is_next:
            response = self._get(config.api_url['get_dream_steps'] + str(dream_id), {
                'shell': self.shell,
                'uid': self.uid,
                'sort': 'desc',
                'page': page
            })
            steps = response['data']['steps']
            if 'dream' in response['data']:
                self.dreams.append(response['data']['dream'])

                print(response['data']['dream'])
            if len(steps) <= 0:
                is_next = False
            page = page + 1
            result.extend(steps)
        return result

    def export(self, method, data, filename, template=None, csv_header=None):
        if method == 'csv':
            self.make_dir(self.export_dir + 'csv/')
            self.export_csv(data, self.export_dir + 'csv/' + filename + '.csv', csv_header)
        elif method == 'markdown':
            self.make_dir(self.export_dir + 'md/')
            self.export_jinja2(data, self.export_dir + 'md/' + filename + '.md', template=template + '.md')
        elif method == 'json':
            self.make_dir(self.export_dir + 'json/')
            self.export_json(data, self.export_dir + 'json/' + filename + '.json')
        elif method == 'html':
            self.make_dir(self.export_dir + 'html/')
            self.export_jinja2(data, self.export_dir + 'html/' + filename + '.html', template=template + '.html')
        else:
            pass

    def export_csv(self, data, filename, csv_header):
        with open(filename, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_header)
            writer.writeheader()
            writer.writerows(data)

    def export_json(self, data, filename):
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    def download_img(self, images, img_base_url, dirname):
        self.make_dir(dirname)
        for image in images:
            url = img_base_url + image
            if os.path.exists(dirname + image):
                continue
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(dirname + image, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
            else:
                print(url + 'error:' + str(r.status_code))

    def export_jinja2(self, data, filename, template):
        env = Environment(loader=FileSystemLoader('templates', 'utf-8'))
        env.get_template(template).stream(data=data, uid=self.uid).dump(filename)

    def export_dream_steps(self, steps, method, dream_id):
        for i in steps:
            if len(i['images']) != 0:
                images = []
                for item in i['images']:
                    images.append(item['path'])
                self.download_img(images, 'http://img.nian.so/step/',
                                  self.image_dir + str(i['dream']) + '/' + str(i['sid']) + '/')
        self.export(method, steps, 'steps_' + dream_id, template='steps',
                    csv_header=['sid', 'content', 'uid', 'image', 'width', 'height', 'lastdate', 'likes', 'liked',
                                'dream', 'member', 'type', 'step_comments', 'user', 'comments', 'publish_date',
                                'images'])

    def get_comment_steps(self, steps):
        for i in steps:
            i['step_comments'] = self.get_comments(i['sid'])
            i['publish_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(i['lastdate'])))
        return steps

    def get_comments(self, step_id, page=1):
        is_next = True
        result = []
        while is_next:
            response = self._get(config.api_url['steps'] + str(step_id) + config.api_url['get_comments'], {
                'shell': self.shell,
                'uid': self.uid,
                'sort': 'asc',
                'page': page
            })
            comments = response['data']['comments']
            if len(comments) <= int(response['data']['perPage']):
                is_next = False
            if len(comments) > 0:
                for i in comments:
                    i['publish_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(i['lastdate'])))
            page = page + 1
            result.extend(comments)
        return result


    def login(self, email, password):
        pwd = 'n*A' + password
        pwd = hashlib.md5(pwd.encode('utf-8')).hexdigest()
        response = self._post(config.api_url['login'], {
            'password': pwd,
            'email': email,
        })
        if response['error'] == 0:
            self.uid = response['data']['uid']
            self.shell = response['data']['shell']
            print(response)
        else:
            print('login error' + str(response))
            exit(0)

    def _get(self, path, params=None, stream=False, timeout=None):
        response = requests.get(self.base_url + path, params=params, stream=stream, timeout=timeout)
        return response.json()

    def _post(self, path, params=None, stream=False, timeout=None):
        response = requests.post(self.base_url + path, data=params, stream=stream, timeout=timeout)
        return response.json()

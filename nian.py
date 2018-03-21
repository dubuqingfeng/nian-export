#!/usr/bin/env python
# coding: utf-8
import csv
import json
import os

import requests

import config
from jinja2 import Environment, FileSystemLoader


class Nian():
    def __init__(self, base_url):
        self.base_url = base_url

    def init_user(self, uid, shell):
        self.uid = uid
        self.shell = shell

    def init_export_dir(self, uid):
        self.export_dir = 'exports/' + str(self.uid) + '/'
        self.image_dir = 'exports/images/' + str(self.uid) + '/'
        self.image_dream_dir = 'exports/images/dreams/' + str(self.uid) + '/'
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

    def export_dreams(self, method, result):
        images = []
        for i in result:
            images.append(i['image'])
        self.download_img(images, 'http://img.nian.so/dream/', self.image_dream_dir)
        self.export(method, result, 'dreams', template='dreams', csv_header=['id', 'title', 'image', 'percent'])

    def get_dream_steps(self, dream_id, page=1):
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
                print(response['data']['dream'])
            if len(steps) <= 0:
                is_next = False
            page = page + 1
            result.extend(steps)
        return result

    def export(self, method, data, filename, template=None, csv_header=None):
        if method == 'csv':
            self.export_csv(data, self.export_dir + filename + '.csv', csv_header)
        elif method == 'markdown':
            self.export_jinja2(data, self.export_dir + filename + '.md', template=template + '.md')
        elif method == 'json':
            self.export_json(data, self.export_dir + filename + '.json')
        elif method == 'html':
            self.export_jinja2(data, self.export_dir + filename + '.html', template=template + '.html')
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
        for image in images:
            url = img_base_url + image + '!large'
            if os.path.exists(dirname + image):
                continue
            r = requests.get(url, stream=True)
            print(r.status_code)
            if r.status_code == 200:
                with open(dirname + image, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
            else:
                print(url + 'error:' + r.status_code)

    def export_jinja2(self, data, filename, template):
        env = Environment(loader=FileSystemLoader('templates', 'utf-8'))
        env.get_template(template).stream(data=data, uid=self.uid).dump(filename)

    def _get(self, path, params=None, stream=False, timeout=None):
        response = requests.get(self.base_url + path, params=params, stream=stream, timeout=timeout)
        return response.json()

    def export_dream_steps(self):
        pass

    def get_comment_steps(self, steps):
        for i in steps:
            i['comments'] = self.get_comments(i['sid'])
            print(i)

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
            page = page + 1
            result.extend(comments)
        return result

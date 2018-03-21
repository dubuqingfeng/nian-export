#!/usr/bin/env python
# coding: utf-8
import csv
import json
import os

import requests

import config


class Nian():
    def __init__(self, base_url, ):
        self.base_url = base_url

    def init_user(self, uid, shell):
        self.uid = uid
        self.shell = shell

    def init_export_dir(self, uid):
        self.export_dic = 'exports/' + str(self.uid) + '/'
        isExists = os.path.exists(self.export_dic)
        if not isExists:
            os.makedirs(self.export_dic)

    def get_dreams(self, page=1):
        is_next = True
        result = []
        while is_next:
            response = self._get(config.api_url['user'] + self.uid + config.api_url['get_dreams'], {
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
        self.download_img(images, 'dreams')
        self.export(method, result, 'dreams', ['id', 'title', 'image', 'percent'])

    def _get(self, path, params=None, stream=False, timeout=None):
        response = requests.get(self.base_url + path, params=params, stream=stream, timeout=timeout)
        return response.json()

    def export(self, method, data, filename, csv_header=None):
        if method == 'csv':
            self.export_csv(data, self.export_dic + filename + '.csv', csv_header)
        elif method == 'markdown':
            self.export_markdown(data, self.export_dic + filename + '.csv')
        elif method == 'json':
            self.export_json(data, self.export_dic + filename + '.json')
        else:
            pass
        pass

    def export_csv(self, data, filename, csv_header):
        with open(filename, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_header)
            writer.writeheader()
            writer.writerows(data)

    def export_json(self, data, filename):
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    def download_img(self, images, dirname):
        pass

    def export_markdown(self, data, filename):
        pass

"""
    Update Cloudflare DNS records
"""
import os
from dataclasses import dataclass

import urllib
import requests
from log import logger

from dataclass_to_json import dataclass_to_json

API_KEY = os.getenv('CLOUDFLARE_API_KEY')


class CloudflareError(Exception):
    """
        Cloudflare Error
    """
    pass


@dataclass
class DnsRecord:
    """
        DNS Record
    """
    id: str
    type: str
    name: str
    content: str
    proxied: bool
    comment: str = None

    def set_content(self, content: str):
        self.content = content
        return self


class CloudflareClient:
    """
        docs: https://api.cloudflare.com/#dns-records-for-a-zone-list-dns-records
    """

    def __init__(self, api_key=API_KEY) -> None:
        self.__api_key = api_key
        self.base_url = 'https://api.cloudflare.com/client/v4'
        self.zone_mapping = {}
        self.headers = {
            'Authorization': f"Bearer {self.__api_key}",
            'Content-Type': 'application/json'
        }

    def init_zones(self):
        """
            Initialize zone mapping
        """
        zones = self.get_zones()
        for zone in zones['result']:
            self.zone_mapping[zone['name']] = zone['id']

        return self

    def validate_params(self, params):
        valid_params = {'comment', 'content',
                        'order', 'page', 'per_page', 'type'}

        validated_params = {x: params[x]
                            for x in params if params[x] and x in valid_params}
        return validated_params

    def get(self, path, **params):
        """
            Make a GET request to the Cloudflare API
        """
        query_params = urllib.parse.urlencode(self.validate_params(params))
        url = f"{self.base_url}/{path}" + f"?{query_params}"

        logger.info("GET %s", url)

        response = requests.get(url, headers=self.headers, timeout=60)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            response_body = response.json()
            error_msg = (response_body.get(
                'errors') or [{}])[0].get('message')

            raise CloudflareError(f"{response.status_code = }, {error_msg = }")

        return response.json()

    def get_zones(self):
        """
            Get all zones
        """
        return self.get('zones')

    def get_dns_records(self, zone_id, **params):
        """
            Get all DNS records for a zone
        """
        records = self.get(
            f"zones/{zone_id}/dns_records", **params)

        return [DnsRecord(
            id=record['id'],
            name=record['name'],
            type=record['type'],
            content=record['content'],
            proxied=record['proxied'],
            comment=record['comment'],
        ) for record in records['result']]

    def update_dns_records(self, zone_id: str, dns_record: DnsRecord):
        """
            Update a DNS record
        """
        json_data = dataclass_to_json(dns_record)
        response = requests.put(
            f"{self.base_url}/zones/{zone_id}/dns_records/{dns_record.id}", headers=self.headers, data=json_data, timeout=60)

        try:
            response.raise_for_status()
            print(f"Successfully updated {dns_record.name}")
        except requests.exceptions.HTTPError as error:
            print(response.json().get('errors'))
            raise error

        return response.json()


if __name__ == '__main__':
    client = CloudflareClient()

    for zone in client.get_zones()['result']:
        print(f"Zone: {zone['name']}, ID: {zone['id']}")
        for record in client.get_dns_records(zone['id'])['result']:
            print(f"  {record['name']}, {record['type']}, {record['content']}")

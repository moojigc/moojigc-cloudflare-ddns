"""
    Update Cloudflare DNS records
"""
import os
from dataclasses import dataclass

import requests

from dataclass_to_json import dataclass_to_json

API_KEY = os.getenv('CLOUDFLARE_API_KEY')


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

    def get(self, url):
        """
            Make a GET request to the Cloudflare API
        """
        response = requests.get(
            f"{self.base_url}/{url}", headers=self.headers, timeout=60)
        response.raise_for_status()

        return response.json()

    def get_zones(self):
        """
            Get all zones
        """
        return self.get('zones')

    def get_dns_records(self, zone_id):
        """
            Get all DNS records for a zone
        """
        records = self.get(f"zones/{zone_id}/dns_records")

        return [DnsRecord(
            id=record['id'],
            name=record['name'],
            type=record['type'],
            content=record['content'],
            proxied=record['proxied'],
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

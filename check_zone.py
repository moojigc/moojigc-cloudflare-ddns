#!/usr/bin/python3

import argparse
import requests
from cloudflare import CloudflareClient


def get_my_ip() -> str:
    response = requests.get('https://ifconfig.me', timeout=60)
    response.raise_for_status()
    return response.text


def list(
    client: CloudflareClient,
    zone_name: str,
):

    records = client.get_dns_records(client.zone_mapping[zone_name])

    print(f"DNS Records for {zone_name}:")
    for record in records:
        print(
            f"Name: {record.name}, Type: {record.type}, Content: {record.content}")

    return records


def update_ip_address(
    client: CloudflareClient,
    zone_name: str,
    record_name: str,
    ip_address: str,
):
    records = list(client, zone_name)
    records_dict = {
        record.name: record for record in records if record.type == "A"}
    record = records_dict[record_name]

    print(f"Updating {record_name} to {ip_address}")
    record.set_content(ip_address)
    print(record)

    client.update_dns_records(
        zone_id=client.zone_mapping[zone_name],
        dns_record=record,
    )


def update_zone_ip_address(
    client: CloudflareClient,
    zone_name: str,
    ip_address: str,
    record_name: str = None,
):

    records = [x for x in list(client, zone_name) if x.type == "A"]

    for record in records:
        if record.content == ip_address:
            print(
                f"Skipping {record.name} as it already has the correct IP address")
            continue

        print(f"Updating {record.name} to {ip_address}")
        record.set_content(ip_address)
        print(record)

        client.update_dns_records(
            zone_id=client.zone_mapping[zone_name],
            dns_record=record,
        )


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('action', choices=['list', 'update-one', 'update-all'])
    args.add_argument('--zone-name', required=True, type=str,
                      help='Zone name, i.e. domain name')
    args.add_argument('--record-name', required=False, type=str)
    args.add_argument('--ip-address', required=False,
                      type=str, default=get_my_ip())
    parsed_args = args.parse_args()

    fn_map = {
        'list': list,
        'update-one': update_ip_address,
        'update-all': update_zone_ip_address,
    }

    client = CloudflareClient().init_zones()

    fn_map[parsed_args.action](
        client,
        zone_name=parsed_args.zone_name,
        record_name=parsed_args.record_name,
        ip_address=parsed_args.ip_address,)

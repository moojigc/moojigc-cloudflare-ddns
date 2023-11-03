#!/usr/bin/python3

import argparse
import requests
from cloudflare import CloudflareClient
from log import logger
import logging


def get_my_ip() -> str:
    response = requests.get('https://ifconfig.me', timeout=60)
    response.raise_for_status()
    return response.text


def list_records(
    client: CloudflareClient,
    zone_name: str,
    **kwargs,
):
    records = client.get_dns_records(
        client.zone_mapping[zone_name], **kwargs)

    print(f"DNS Records for {zone_name}:")
    for record in records:
        print(
            f"ID: {record.id} Name: {record.name}, Type: {record.type}, Content: {record.content}, Comment: {record.comment}")

    return records


def update_ip_address(
    client: CloudflareClient,
    zone_name: str,
    record_name: str,
    ip_address: str = lambda: get_my_ip(),
    **kwargs,
):
    records = list_records(client, zone_name)
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
    comment: str = None,
    **kwargs,
):

    records = [x for x in list_records(
        client, zone_name, comment=comment, type="A")]

    for record in records:
        if record.content == ip_address:
            logger.warn(
                "Skipping %s as it already has the correct IP address", record.name)
            continue

        logger.info("Updating %s to %s", record.name, ip_address)
        record.set_content(ip_address)
        logger.info(record)

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
                      type=str)
    args.add_argument('--log', required=False, type=str)
    args.add_argument('--comment', required=False, type=str)
    args.add_argument('--type', required=False,
                      type=str, help='DNS record type')
    parsed_args = args.parse_args()
    logger.setLevel((parsed_args.log or "").upper() or logging.INFO)
    logger.debug(parsed_args)

    fn_map = {
        'list': list_records,
        'update-one': update_ip_address,
        'update-all': update_zone_ip_address,
    }

    client = CloudflareClient().init_zones()

    fn_map[parsed_args.action](
        client,
        **parsed_args.__dict__,)

import json
import os
import asyncio
import httpx

import apiclient


async def process_cred(cred, shared_client):
    client = apiclient.KCLSClient(cred['username'], cred['password'], client=shared_client)
    await client.async_login()
    items = await client.async_get_checked_out_items()
    return cred, items


async def async_main():
    if 'KCLS_CREDS' in os.environ:
        creds = json.loads(os.environ['KCLS_CREDS'])
    else:
        creds = [
            {
                'username': os.environ['KCLS_USERNAME'],
                'password': os.environ['KCLS_PASSWORD'],
            }
        ]

    async with httpx.AsyncClient() as shared_client:
        tasks = [process_cred(cred, shared_client) for cred in creds]
        results = await asyncio.gather(*tasks)

    for cred, items in results:
        print(f'# {cred.get("display_name", cred["username"])}')
        for item in items:
            print(f'{item.title} // {item.author} // {item.barcode} // {item.due_date}')
        print()


def main():
    asyncio.run(async_main())


if __name__ == '__main__':
    main()

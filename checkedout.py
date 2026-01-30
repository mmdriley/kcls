import asyncio
import json
import os

import httpx

import apiclient


async def get_user_items(client, username, password):
    kclsclient = apiclient.KCLSClient(client)
    await kclsclient.login(username, password)
    return await kclsclient.get_checked_out_items()


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

    async with httpx.AsyncClient() as httpx_client:
        async def one_user_items(username, password):
            c = apiclient.KCLSClient(httpx_client)
            await c.login(username, password)
            return await c.get_checked_out_items()

        tasks = [one_user_items(cred['username'], cred['password']) for cred in creds]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for cred, r in zip(creds, results):
        print(f'# {cred.get("display_name", cred["username"])}')

        if isinstance(r, Exception):
            print(str(r))
        else:
            for item in r:
                print(
                    f'{item.title} // {item.author} // {item.barcode} // {item.due_date}'
                )
        print()


if __name__ == '__main__':
    asyncio.run(async_main())

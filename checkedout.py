import json
import os
import asyncio
import httpx

import apiclient


async def process_cred(cred, shared_client):
    try:
        client = apiclient.KCLSClient(client=shared_client)
        await client.login(cred['username'], cred['password'])
        items = await client.get_checked_out_items()
        return cred, items, None
    except ValueError as e:
        if str(e) == 'Invalid credentials':
            return cred, [], 'Bogus Credentials'
        return cred, [], str(e)
    except Exception as e:
        return cred, [], str(e)


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

    for cred, items, error in results:
        print(f'# {cred.get("display_name", cred["username"])}')
        if error:
            print(error)
        else:
            for item in items:
                print(f'{item.title} // {item.author} // {item.barcode} // {item.due_date}')
        print()


def main():
    asyncio.run(async_main())


if __name__ == '__main__':
    main()

import json
import os

import apiclient


def main():
    if 'KCLS_CREDS' in os.environ:
        creds = json.loads(os.environ['KCLS_CREDS'])
    else:
        creds = [
            {
                'username': os.environ['KCLS_USERNAME'],
                'password': os.environ['KCLS_PASSWORD'],
            }
        ]

    for cred in creds:
        client = apiclient.KCLSClient(cred['username'], cred['password'])
        print(f'# {cred.get("display_name", cred["username"])}')
        for item in client.get_checked_out_items():
            print(f'{item.title} // {item.author} // {item.barcode} // {item.due_date}')
        print()


if __name__ == '__main__':
    main()

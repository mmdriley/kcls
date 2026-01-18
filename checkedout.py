import apiclient


def main():
    client = apiclient.default_client()
    for item in client.get_checked_out_items():
        print(f'{item.title} // {item.author} // {item.barcode} // {item.due_date}')


if __name__ == '__main__':
    main()

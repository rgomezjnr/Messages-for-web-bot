#!/usr/bin/env python
 
import csv
import time
import getpass
import textwrap
import argparse

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from msedge.selenium_tools import Edge, EdgeOptions

DEFAULT_DELAY = 4
DEFAULT_START_RANGE = 2                     # Row number in CSV file to begin with, 2 if CSV has header
CSV_NAME_COLUMN = 1                         # e.g. 'Given Name' column from contacts.google.com CSV export
CSV_PHONE_COLUMN = 3                        # e.g. 'Phone 1 - Value' column from contacts.google.com CSV export
USER_DATA_DIR = 'C:\\Users\\' + getpass.getuser() + '\\AppData\\Local\\Microsoft\\Edge\\User Data\\'
PROFILE_DIR = 'Default'
MESSAGES_URL = 'https://messages.google.com/web/conversations/new'

parser = argparse.ArgumentParser(
    prog='messages-for-web-bot',
    description='Automatically send text messages using Google Messages for web',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''\
        By default, MESSAGE will be sent to all contacts in CONTACTS CSV file
        Add curly brackets {} in MESSAGE to substitute contact name in MESSAGE

        Examples

        Send text message to all contacts in contacts.csv and substitute contact name in message:
        python messages-for-web-bot.py contacts.csv "Hey {}, want to play ball this Friday at 6?"

        Send text message to first 10 contacts (row entries 2-11) in contacts.csv:
        python messages-for-web-bot.py --end_range 11 contacts.csv "Hello"

        Send text message to 12-20 contact entries in contacts.csv:
        python messages-for-web-bot.py --range 12 20 contacts.csv "Hello"

        Send text message to remaining contacts after row 20 in contacts.csv:
        python messages-for-web-bot.py --start_range 21 contacts.csv "Hello"
    ''')
)
parser.add_argument('CONTACTS', type=str, help='CSV file containing contacts to send text messages to')
parser.add_argument('MESSAGE', type=str, help='Content of text message to send to contacts, double-quoted')
parser.add_argument('-n', '--dry_run', help='Run script without actually sending text messages', action='store_true')
parser.add_argument('-d', '--delay', type=int, default=DEFAULT_DELAY, help='Time delay value between automated browser actions, in seconds')
parser.add_argument('-s', '--start_range', type=int, default=DEFAULT_START_RANGE, help='Starting row entry in CONTACTS CSV file to send text messages to, inclusive')
parser.add_argument('-e', '--end_range', type=int, help='Ending row entry in CONTACTS CSV file to send text messages to, inclusive')
#parser.add_argument('-e', '--end_range', type=int, choices=range(2, math.inf), metavar='[2-∞]', help='Ending row entry in CONTACTS CSV file to send text messages to, inclusive')
parser.add_argument('-r', '--range', type=int, nargs=2, help='Specify range (row entries) in CONTACTS CSV file to send text messages to')
#parser.add_argument('-x', '--exclude', type=int, help='Exclude row entry/entries in CONTACTS CSV file from sending text messages to')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1.0')
args = parser.parse_args()

if args.range:
    args.start_range = args.range[0]
    args.end_range = args.range[1]

options = EdgeOptions()
options.use_chromium = True
options.add_argument('user-data-dir={}'.format(USER_DATA_DIR))
options.add_argument('profile-directory={}'.format(PROFILE_DIR))
browser = Edge(options = options)

time.sleep(args.delay)

with open(args.CONTACTS, newline='') as contacts_file:
    contacts = csv.reader(contacts_file)

    for contact in contacts:
        try:
            if args.end_range + 1 == contacts.line_num:
                break
        except TypeError:
            pass

        if contacts.line_num >= args.start_range:
            browser.get(MESSAGES_URL)
            time.sleep(args.delay)

            browser.switch_to.active_element.send_keys(contact[CSV_PHONE_COLUMN] + Keys.RETURN)

            time.sleep(args.delay)

            if args.dry_run:
                browser.switch_to.active_element.send_keys(args.MESSAGE.format(contact[CSV_NAME_COLUMN]))
            else:
                browser.switch_to.active_element.send_keys(args.MESSAGE.format(contact[CSV_NAME_COLUMN]) + Keys.RETURN)

            time.sleep(args.delay)

browser.quit()

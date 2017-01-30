#!/usr/bin/env python
#
# Very basic example of using Python and IMAP to iterate over emails in a
# gmail folder/label.  This code is released into the public domain.
#
# RKI July 2013
# http://www.voidynullness.net/blog/2013/07/25/gmail-email-with-python-via-imap/
#
import sys
import imaplib
import getpass
import email
import email.header
import datetime

import json
from pprint import pprint

with open('config.json') as json_data:
    d = json.load(json_data)
    EMAIL_ACCOUNT = d['email_address']
    SERVER_ADDRESS = d['server_address']
    PASSWORD = d['password'] or getpass.getpass()

#EMAIL_FOLDER = "INBOX"
EMAIL_FOLDER = "INBOX.Archives.2013"

def process_mailbox(M):
    """
    Do something with emails messages in the folder.
    For the sake of this example, print some headers.
    """

    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print "No messages found!"
        return

    numbers = data[0].split()
    total = len(numbers)
    total_float = float(total)

    seen = 0
    emails = {}
    for num in numbers:
        print '{0:.2f}%'.format((seen / total_float) * 100)
        seen = seen + 1;
        #rv, data = M.fetch(num, '(RFC822)')
        rv, data = M.fetch(num, '(BODY.PEEK[])')
        if rv != 'OK':
            print "ERROR getting message", num
            return

        msg = email.message_from_string(data[0][1])
        decode = email.header.decode_header(msg['Subject'])[0]
        #subject = unicode(decode[0])
        subject = decode[0]

        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple))


        plain_text = None
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                plain_text = part.get_payload(decode=True)

        emails[num] = {
            'subject'   : subject,
            'date'      : local_date,
            'plain_text': plain_text
        }

        continue

        print 'Message %s: %s' % (num, subject)
        print 'Raw Date:', msg['Date']
        # Now convert to local date-time
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple))
            print "Local Date:", \
                local_date.strftime("%a, %d %b %Y %H:%M:%S")
    return emails

def get_inbox_listing():
    M = imaplib.IMAP4_SSL(SERVER_ADDRESS)

    try:
        rv, data = M.login(EMAIL_ACCOUNT, PASSWORD)
    except imaplib.IMAP4.error:
        print "LOGIN FAILED!!! "
        sys.exit(1)

    print rv, data

    rv, mailboxes = M.list()
    #if rv == 'OK':
    #    print "Mailboxes:"
    #    print mailboxes

    rv, data = M.select(EMAIL_FOLDER)
    if rv == 'OK':
        print "Processing mailbox...\n"
        emails = process_mailbox(M)
        M.close()
    else:
        print "ERROR: Unable to open mailbox ", rv

    M.logout()
    return emails

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

#EMAIL_FOLDER = "INBOX"
EMAIL_FOLDER = "INBOX.Archives.2013"

def process_mailbox(M):
    """
    Do something with emails messages in the folder.
    For the sake of this example, print some headers.
    """

    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print("No messages found!")
        return

    numbers = data[0].split()
    total = len(numbers)
    total_float = float(total)

    seen = 0
    emails = {}
    for num in numbers:
        print('{0:.2f}%'.format((seen / total_float) * 100))
        seen = seen + 1;
        #rv, data = M.fetch(num, '(RFC822)')
        rv, data = M.fetch(num, '(BODY.PEEK[])')
        if rv != 'OK':
            print("ERROR getting message", num)
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
            print(part.get_content_type())
            if part.get_content_type() == "text/plain":
                plain_text = part.get_payload(decode=True)

        from_email = msg['from']
        if '<' in from_email:
            from_email = from_email.split('<')[1]
        if '>' in from_email:
            from_email = from_email.split('>')[0]

        emails[num] = {
            #'id'        : msg['Message-ID'],
            'from'       : msg['from'],
            'from_email' : from_email,
            'subject'    : subject,
            'date'       : local_date,
            'plain_text' : plain_text
        }

    return emails

def get_inbox_listing(config):
    M = imaplib.IMAP4_SSL(config.server_address)

    try:
        rv, data = M.login(config.email_address, config.password)
    except imaplib.IMAP4.error:
        print('LOGIN FAILED!')
        sys.exit(1)

    print(rv, data)

    rv, mailboxes = M.list()
    #if rv == 'OK':
    #    print "Mailboxes:"
    #    print mailboxes

    rv, data = M.select(EMAIL_FOLDER)
    if rv == 'OK':
        print('Processing mailbox...\n')
        emails = process_mailbox(M)
        M.close()
    else:
        print("ERROR: Unable to open mailbox ", rv)

    M.logout()
    return emails

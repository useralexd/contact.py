class btn:
    hide_log = 'Hide log'
    show_log = 'Show log'
    block = 'Block'
    unblock = 'Unblock'
    reply = 'Reply'
    skip = 'Skip'
    back = 'Back'
    set_messages = 'Set messages'
    help = 'Help'
    list_chats = 'List chats'
    list_blocked = 'List blocked chats'
    menu = 'Main menu'


class msg:
    help = '''Hey {first_name}!

I will notify you about all messages sent to me. You can use me to hide your real telegram account.

You can block users. Blocked user won't bother you via me and will recieve special <b>blocked</b> message.

I will track you availability. \
If you weren't answering to users for 1 hour, they will recieve special <b>unavailable</b> message.

Use inline buttons to interact with me. /start command will show you the main menu.

<b>For any help and queries please contact --</b> <a href="telegram.me/phash_bot">me</a> \
<b>or check out</b> <a href="https://github.com/p-hash/proxybot">source code</a>.'''
    menu = '''Hey {first_name}!

Here is the main menu. Let me describe the buttons below:

<b>List users</b> and <b>List blocked users</b> will show these lists respectively.

<b>Set messages</b> will let you set special messages for users.

<b>Help</b> sends little help, containing a developer contact and source code link.
'''
    new_msg = '''New message from {chat:html}

{message}'''

    noone_to_reply = 'No one to reply!'
    bot_started = "Bot started"
    
    checked_available = 'Your current status is <b>Available</b>'
    checked_unavailable = 'Your current status is <b>Unavailable</b>'
    
    chatlist_header = 'Chat list: \n\n'
    no_chats = 'There are no chats yet.'
    blockedlist_header = 'Blocked list: \n\n'
    none_blocked = '''You haven't blocked any chat yet.'''

    invalid_content_type = 'Invalid content type'

    master_intro = '''Okay, lets set up messages for your users.'''
    master_edited = '''\
Your previous <b>{msg_type}</b> message:
<code>=========================</code>
{old_msg}
<code>=========================</code>

Your new <b>{msg_type}</b> message:
<code>=========================</code>
{new_msg}
<code>=========================</code>
'''
    master_step_descr = {
        'start': '''Set up your <b>start</b> message.

<b>Start</b> message is what user sees when he/she starts this bot.

Your <b>start</b> message''',
        'unavailable': '''Set up your <b>unavailable</b> message.

<b>Unavailable</b> message will be sent to users if you weren't answering for 1 hour.

Your <b>unavailable</b> message''',
        'block': '''Set up your <b>block</b> message.

<b>Block</b> message is what user sees if he/she were blocked.

Your <b>block</b> message'''
    }
    master_step = ''':
<code>=========================</code>
{msg}
<code>=========================</code>

Now you can send me new message or tap <b>Skip</b> button to \
leave it as it is.'''
    master_notset = '''\
 is not set!
Kindly send me your new <b>{msg_type}</b> message.'''
    master_set = '''\
Your <b>{msg_type}</b> message is set:
<code>=========================</code>
{new_msg}
<code>=========================</code>'''
    master_done = '''Alright! All messages for users are set.

Press the button below to open <b>the main menu</b>.'''
    master_skipped = '''\
Your <b>{msg_type}</b> message:
<code>=========================</code>
{msg}
<code>=========================</code>
'''


class ans:
    done = 'Done!'
    reply = 'Okay, now send me a message!'
    blocked = 'Chat blocked!'
    unblocked = 'Chat unblocked!'
    error = 'Error!.'
    skipped = 'Skipped..'
    returned = 'Returned..'
    menu = 'Menu'
    help = 'Help'


pager_marks = ['« ', '< ', '·', ' >', ' »']

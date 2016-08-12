class btn:
    hide_log = 'Hide log'
    show_log = 'Show log'
    block = 'Block'
    unblock = 'Unblock'
    reply = 'Reply'
    user = '{index}. {user.first_name}'
    skip = 'Skip'
    back = 'Back'


class msg:
    user_full = '''<b>User</b>
<code>Id:</code> {user.id}
<code>Username:</code> @{user.username}
<code>First Name:</code> {user.first_name}
<code>Last Name:</code> {user.last_name}
<code>Is blocked?</code> <i>{user.blocked}</i>
'''
    user_line = '<code>{index}.</code> {user.first_name} (@{user.username})\n'
    
    help = '''Hey {first_name}!

<b>For any help and queries please contact -</b> <a href="telegram.me/phash_bot">me</a> \
<b>or check out</b> <a href="https://github.com/p-hash/proxybot">source code</a>.'''
    new_msg = '''New message from {user.first_name} (@{user.username})

{message}'''

    noone_to_reply = 'No one to reply!'
    bot_started = "Bot started"
    
    checked_available = 'Your current status is <b>Available</b>'
    checked_unavailable = 'Your current status is <b>Unavailable</b>'
    
    userlist_header = 'User list: \n\n'
    blockedlist_header = 'Blocked list: \n\n'
    log_header = 'Chat with {user.first_name} (@{user.username}):\n\n'

    invalid_content_type = 'Invalid content type'

    master_intro = '''Okay, lets set up messages for your users.\n\n'''
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
    master_step = '''\
Your <b>{msg_type}</b> message:
<code>=========================</code>
{msg}
<code>=========================</code>

Now you can send me new <b>{msg_type}</b> message or tap <b>Skip</b> button to \
leave it as it is.'''
    master_notset = '''\
Your <b>{msg_type}</b> message is not set!
Kindly send me your new <b>{msg_type}</b> message.'''
    master_set = '''\
Your <b>{msg_type}</b> message is set:
<code>=========================</code>
{new_msg}
<code>=========================</code>'''
    master_done = '''Alright! All messages for users are set.'''
    master_skipped = '''\
Your <b>{msg_type}</b> message:
<code>=========================</code>
{msg}
<code>=========================</code>
'''


class ans:
    done = 'Done!'
    reply = 'Okay, now send me a message!'
    blocked = 'User blocked!'
    unblocked = 'User unblocked!'
    error = 'Error!.'
    skipped = 'Skipped..'
    returned = 'Returned..'


pager_marks = ['« ', '< ', '·', ' >', ' »']

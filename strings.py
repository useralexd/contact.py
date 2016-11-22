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
    list = {
        'user': 'Users',
        'group': 'Groups',
        'channel': 'Channels',
        'blocked': 'Blocked'
    }
    menu = 'Main menu'
    toggle_md = 'Toggle markdown'


class msg:
    sent = '<b>Sent successfully!</b> You can send me one more to the same chat.'
    help = '''Hey {first_name}!

I will notify you about all messages sent to me. You can use me to hide your real telegram account.

You can use markdown in your messages to users.
Simple guide to markdown:
*bold* _italic_ `code`

You can add me to groups and channels, BUT I won't recieve new messages in them.
The idea is write to chats from behind the bot using markdown.

You can block users. Blocked user won't bother you via me and will recieve special <b>blocked</b> message.

I will track you availability. \
If you weren't answering to users for 1 hour, they will recieve special <b>unavailable</b> message.

Use inline buttons to interact with me. /start command will show you the main menu.

<b>For any help and queries please contact --</b> <a href="telegram.me/phash_bot">me</a> \
<b>or check out</b> <a href="https://github.com/p-hash/proxybot">source code</a>.'''
    menu = '''Hey {first_name}!
Here is the main menu. Let me describe the buttons below:

<b>Users</b>, <b>Groups</b>, <b>Channels</b> and <b>Blocked</b> will show you those lists respectively.
<b>Set messages</b> will let you set the default messages I'll answer to users based on situation.
<b>Help</b> sends little help, containing a developer contact and source code link.
'''
    new_msg = '''New message from {chat:html}

{message}'''
    new_group = '''The bot was added to {:full}\n
<b>Don't violate the rules and take care: \
this group might be updated to supergroup! I can't properly handle this case!!!</b>'''
    new_channel = '''The bot was added to {:full}\n
<b>Make sure your bot is admin of the \
channel to send messages to it!</b>
I won't track message history for channels. Sorry about that.'''
    new_sgroup = '''The bot was added to {:full}\n
<b>Don't violate the rules of the group!</b>'''

    noone_to_reply = 'No one to reply!'

    list_header = {
        'user': 'Private chat list: \n\n',
        'group': 'Group chat list: \n\n',
        'channel': 'Channels list: \n\n',
        'blocked': 'Blocked list: \n\n'
    }
    no_items = {
        'user': 'There are no chats yet',
        'group': 'The bot wasn\'t added to any group yet',
        'channel':
            'Bot wasn\'t added to any channel yet.\nAdd me to channel as admin and forward me any message from it.',
        'blocked': 'You haven\'t blocked any chat yet'
    }

    invalid_content_type = 'Invalid content type'
    error = 'Error occured\n{}'

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

<b>Start</b> message is what user sees when he/she starts this bot. \
It is my autoreply on user's <code>/start</code> command.
Example: <pre>Hello there! Write me to contact Admin.</pre>

Your <b>start</b> message''',
        'unavailable': '''Set up your <b>unavailable</b> message.

<b>Unavailable</b> message will be sent to users if you weren't answering for 1 hour. \
This autoreply should notify user that you're human so they wont expect fast answer and block the bot.
Example: <pre>It might take a while for admin to reply... Make sure you haven't block the bot!</pre>

Your <b>unavailable</b> message''',
        'block': '''Set up your <b>block</b> message.

<b>Block</b> message is what user sees if he/she were blocked. \
I automatically reply with it instead of resending message to you.
Example: <pre>Oops, you were blocked. Sorry!</pre>

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
    md_on = 'Markdown is ON now! \nTake care using MD symbols such as: \n_italic_ *bold* `code` [link](ggl.com)'
    md_off = 'Markdown is OFF now!'


pager_marks = ['« ', '< ', '·', ' >', ' »']

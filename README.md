#<p align="center">Telegram Proxy Bot 
A simple BITM, for [Telegram](https://telegram.org/) acting as some kind of "proxy". Can use it as "virtual" second account for your purposes without revealing your "actual" identity.

Credits to **Groosha** for the actual version

Credits to [Mr_Gigabyte](https://github.com/mrgigabyte/proxybot) for additional features


 * [ChangeLog!](#changelog)
 * [Prerequisites](#prerequisites)
 * [How to install](#how-to-install)
 * [What's new ?](#whats-new-)
 * [How it works ?](#how-it-works)
    * [Basic Functionality](#basic-functionality)
    * [Blocking and Unblocking Feature](#blocking-and-unblocking-feature)
    * [Available and Unavailable Feature](#available-and-unavailable-feature)
 * [Notes and restrictions](#notes-and-restrictions)
 * [Upcoming features](#upcoming-features)
 * [Remember](#remember)
 * [F.A.Q.](#faq)
 * [Contact](#contact)

##ChangeLog!
####Version0.2.0
   * **Major Update**: Start Message editing by `/setstartmessage`
   Start message is the fist message user sees, when he/she starts the bot.
   * **Bugs in this version**: Hopefully no

####Version0.1.0
   * **Major Update**: 
     1. All storing data functionality moved to MongoDB. 
     2. Added paging to users list and blocked list.
     3. Simplified user blocking using inline keyboards.
     4. Code refactored and beautified.
   * **Bugs in this version**: Hopefully no

   
 
## Prerequisites
* Python 3 (works only with Python3);
* [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI/) library (with bot 2.0 support);
* [pyMongo](https://pypi.python.org/pypi/pymongo) driver and MongoDB credentials
* Telegram account.
* Basic Knowledge about coding of course! 
* And the ability to read the manual patiently :D 

## How to install
* Get your own bot's token from [@BotFather](https://telegram.me/botfather);
* Get your MongoDB (If you don't want to install it, try online services such as [mLab](https://mlab.com/))
* Find out your account's unique ID (you can use [ID bot](https://telegram.me/my_id_bot) or just send message via Curl or something else and get `message.chat.id` from response JSON);
* Fill in the necessary variables in `config.py`;
* Start bot: `bash launch.sh`

## What's new ???
* You can now set Start Message the same way you do with the Block Message and Unavailable Message. New commands are `/setstartmessage` and `/viewstartmessage`
* Bot sends _usercard_ with each user's message (which increases the number of messages, i know. I hope, I'll get to it later). _Usercard_ shows all info about user. Ream more about blocking and unblocking [here](#blocking-and-unblocking-feature).
* Admins can set their status as `/available` or `/unavailable`. This means that when you will not be available bot will notify the user if he/she tries to text you by sending him your unavailable message, just like the way you have a pre-recorded message on answering machines! The bot will however forward you the message. You can set and view your unavailable message by typing `/setunavailablemessage` and `/setunavailablemessage` respectively.
* You can now view the list of all users bot has seen! Type `/viewuserslist`. The list will contain basic info about every user and a command to their usercard.
* You can now view the list of users you've blocked! Type `/viewblocklist`. The list will contain basic info about every user and a command to their usercard.
* You can check your status whether you're currently available or unavailable by typing `/checkstatus`
* `/help` command is also there for admins to see all the available commands
* `/viewblockmessage` and `/setblockmessage` to view and set the block message that the user will see once he/she is blocked
* [In Reply to](#in-reply-to) feature. Admin can now see what message the user has force replied to

## How it works
### Basic Functionality
The idea of this bot is pretty simple: you just place the bot between you and the one you want to chat with. The upside is that no one will find out your unique chat id or some other info (nickname, first name or avatar, for example). They won't also know your last seen time. However, the downside is that you can't initiate chat with someone (Because you're writing from bot and bots can't start chats to prevent spam), so you'll have to ask people to write to your bot first. 


<p align="center"> ![A simple scheme of interaction](https://habrastorage.org/files/4a2/d19/753/4a2d19753eb34073bfda0b872bf228b3.png)

<p align="center">![Screenshot](http://i.imgur.com/YZoiTjd.png)

#### Setting Start Message
You can set Start Message -- the message, which user sees when he/she starts the bot.
Use `/setstartmessage` command for setting it and `/viewstartmessage` for viewing it.

### Blocking and Unblocking Feature
It was messy and complicated for me in Mr_Gigabyte's implementation, so I've fully rewrited it.

There is a message which I call _usercard_. It has all information about user and an inline keyboard with only one button, which allows to block or unblock user. _Usercard_ can be requested by `/userNNNNNN` command, where `NNNNNN` is Telegram user\_id. Bot also send _usercard_ to admin before each user's message. A list of `/userNNNNNN` commands can be found in all users list (`/viewuserlist`) and blocked user list (`/viewblocklist`)

Data storage moved from couple text files to MongoDB, which will help us to add functionality in future.

So here are the commands connected to blocking: <br>
* `/setblockmessage` <-- To **set the block text** that the user will see once he/she is blocked <br>
* `/viewblockmessage` <-- To **view** your own block message
* `/viewuserlist` <-- To **view** all users in a list with their `/userNNNNNN` commands
* `/viewblocklist` <-- To **view** blocked users list with their `/userNNNNNN` commands
* `/userNNNNNN` <-- To **view** _usercard_. `NNNNNN` here stands for Telegram user\_id
<br>

#### Screenshots:
#####Basic Blocking Functionality:
![screenshot](http://i.imgur.com/wjcE4Yy.png)<br><br>
#####Setting the blocking text:
![screenshot](http://i.imgur.com/1JVLQRr.png)<br><br>
#####Viewing the Block List and the User List:
<p align="cente">![screenshot](http://i.imgur.com/6hXC3lR.png)<br><br>


### Available and Unavailable Feature
There can be at times when you as an admin are unavailable or don't temporarily have access to the bot, but you at the same time want to notify all the users about your unavailability just like the way we have on answering machines ? 
<br>
<br>
**"Joshua is Unavailable! Kindly leave your message after the beep.........."** 
<br>
<br>
Keeping this in mind here's the `/unavailable` and `/available` feature!
<br>
You can now set your status as **available** or **unavailable** <br>
<br>
So now the admins set the status by typing:
* `/available` <--- To set the status as available
* `/unavailable` <--- to set the status as unavailable<br>
To check the current status simply send `/checkstatus` to the bot<br><br>

If your status is set to **unavailable** then the bot will simply forward the message to the admin and notify the user about the unavailability of the admin **( by sending an unavailable message)**<br><br>
To set the unavailable message simply send:
* `/setunavailablemessage`

To view the unavailable message simply send:
* `/viewunavailablemessage`

####Screenshots :
##### Setting Unavailable Message :
![screenshot](http://i.imgur.com/kVegDzP.png)<br><br>
##### Basic Feature :
![screenshot](http://i.imgur.com/uvMbmfg.png)<br><br>
##### Checking Status:
<p align="center">![screenshot](http://i.imgur.com/R3VIqfw.png)<br><br>

##In Reply To:
Well as stated before/in the previous version. The admins were not able to see the text the user has force replied to, since the bot only forwards every new text and not the old ones.. So admin wouldn't know if the user has replied to a previously sent text or not. Now admins can see the previously send message to which the user replied.

###Screenshot:
<p align="center">![screenshot](http://i.imgur.com/uvMbmfg.png)<br><br>


## Notes and restrictions
1. Message formatting (both Markdown and HTML) is disabled. You can easily add `parse_mode` argument to `send_message` function to enable it.<br>
**example:**
``` python 
bot.send_message(message.chat.id, "Please click on [this](www.google.com)to search on Google",parse_mode="Markdown")
```

2. You(Admins) should **always** use "reply" function, because bot will check `message_id` of selected "message to reply".
3. Database is needed to store users' statuses and log messages.
4. Supported message types in reply: `text`, `sticker`, `photo`, `video`, `audio`, `voice`, `document`, `location`.
5. To block a user simply tap `Block` button under his _usercard_. It will change its name to `Unblock` and user will be blocked.
6. This bot only works in the private chats.
7. You can use the `/help` command to view all the commands which you can use an admin
![screenshot](http://i.imgur.com/hgWuEuz.png)

## Upcoming Features
* Viewing messages log per user
* In Reply To feature for users
* Anti-Spam Feature, limiting messages sent per-second
* Broadcast feature for admins, they can broadcast a certain message to selected users they want

## Remember!
I understand, that "proxy" bots can be used to prevent spammers from being reported, so if you encounter such bots that are used to do "bad" things, feel free to report them: [abuse@telegram.org](mailto:abuse@telegram.org)

## F.A.Q
#### 1. Will this bot work in groups/supergroups/channels ?
For the time being this bot just works in private chats.

#### 2. Can I use Emojis in my unavailable message ?
Yes! You can use **ONLY** emojis or text in your unavailable message, you cannot save stickers/gifs in the unavailable message

#### 3. Will I be able to skip my school/college/job ? 
Unfortunately nope :( 

## Contact
You can contact me via my [Proxy Bot](https://telegram.me/phash_bot).<br>
**PS: Let me know if you need a new feature/tweak in this bot, please don't hesitate to text me :)**

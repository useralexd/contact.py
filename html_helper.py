max_len = 200


def shorten_text(msg):
    if len(msg.text) < max_len:
        return msg.text
    else:
        return msg.text[:max_len] + '... /msg' + msg.short_id


def escape_html(text):
    if text is None:
        return None
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def entities_to_html(text, entities):
    if entities is None:
        return escape_html(text)
    new_text = ''
    p = 0
    for entity in entities:
        l = entity.offset
        r = l + entity.length
        if r > max_len:
            break
        new_text += escape_html(text[p:l])
        p = r
        m = escape_html(text[l:r])
        if entity.type == 'bold' or entity.type == 'italic':
            new_text += '<{t}>{m}</{t}>'.format(t=entity.type[0], m=m)
        elif entity.type == 'code' or entity.type == 'pre':
            new_text += '<{t}>{m}</{t}>'.format(t=entity.type, m=m)
        elif entity.type == 'text_link':
            new_text += '<a href="{url}">{m}</a>'.format(url=entity.url, m=m)
        else:
            new_text += m
    new_text += escape_html(text[p:])
    return new_text


def entities_to_md(text, entities):
    if entities is None:
        return text
    new_text = ''
    p = 0
    for entity in entities:
        l = entity.offset
        r = l + entity.length
        new_text += text[p:l]
        p = r
        if entity.type == 'bold':
            new_text += '*{}*'.format(text[l:r].replace('*', '\*'))
        elif entity.type == 'italic':
            new_text += '_{}_'.format(text[l:r].replace('_', '\_'))
        elif entity.type == 'code':
            new_text += '`{}`'.format(text[l:r].replace('`', '\`'))
        elif entity.type == 'pre':
            new_text += '```{}```'.format(text[l:r])
        elif entity.type == 'text_link':
            new_text += '[{}]({})'.format(text[l:r], entity.url)
        else:
            new_text += text[l:r]
    new_text += text[p:]
    return new_text


def to_html(msg):
    if msg.content_type == 'text':
        text = shorten_text(msg)
        return entities_to_html(text, msg.entities)
    else:
        text = '<code>[{}]</code> '.format(msg.content_type)
        if msg.caption:
            text += escape_html(msg.caption)
        text += ' /msg' + msg.short_id
        return text

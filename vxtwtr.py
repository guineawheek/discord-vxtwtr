"""
copyright (c) 2024 guineawheek

Permission is hereby granted, free of charge, to any person obtaining a 
copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the 
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in 
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.
"""

import discord
import os
import sys
import re
import asyncio
from typing import Set, TypeVar

# the lookbehind prevents intentionally un-embedded links from embedding.
PATTERN = re.compile(r"(?<!<)(https://(x|twitter)\.com/[-a-zA-Z0-9()@:%_\+.~#?&//=]*)")
VIDEO_URL_BASE = r"https://pbs.twimg.com/ext_tw_video_thumb"
LINK_STRIP = re.compile(r"https://twitter\.com/\w*/status/[0-9]*")

T = TypeVar("T")
def unwrap_or(v: T | None, alt: T) -> T:
    if v is None:
        return alt
    return v

def twitterify(url: str) -> str:
    return url.replace("x.com", "twitter.com")


class VxTwtr(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message: discord.Message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        
        # attempts to avoid a race condition where discord takes a hot second to generate the embed
        # although sometimes discord _won't_ generate the embed but chances are after half a second it won't show up anyway
        asyncio.create_task(self.on_message_later(message))
        
    async def on_message_later(self, message: discord.Message):
        await asyncio.sleep(0.5)
        links: Set[str] = set(twitterify(u[0]) for u in PATTERN.findall(message.content))
        if not links:
            return

        failed_embed = set()
        succeeded_embed = set()
        for embed in message.embeds: 
            link = embed.url
            if link is None or not PATTERN.match(link):
                continue
            link = twitterify(link)

            if embed.image.url or embed.description:
                if unwrap_or(embed.image.url, "").startswith(VIDEO_URL_BASE):
                    # video links never embed correctly
                    failed_embed.add(link)
                else:
                    succeeded_embed.add(link)
            else:
                failed_embed.add(link)
        
        # add other embeds
        failed_embed.update(links - succeeded_embed)
        links_to_post = []
        for failed_link in failed_embed:
            m = LINK_STRIP.match(failed_link)
            if not m:
                continue
            links_to_post.append(m[0].replace("twitter.com", "vxtwitter.com"))
        
        send_text = "\n".join(links_to_post)
        if send_text:
            await message.channel.send(send_text)


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    client = VxTwtr(intents=intents)
    key = os.getenv("TOKEN")
    if key is None:
        print("TOKEN env variable needs to be supplied with a discord token", file=sys.stderr)
        sys.exit(1)
    client.run(key)
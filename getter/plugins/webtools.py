# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import time
import urllib.parse
import speedtest
from validators.ip_address import ipv4
from . import (
    kasta_cmd,
    plugins_help,
    is_url,
    parse_pre,
    humanbytes,
    humanbool,
    aioify,
    Fetch,
    MyIp,
    Pinger,
)


@kasta_cmd(
    pattern="(google|duck|yandex|bing|yahoo|baidu|ecosia)(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    engine = kst.pattern_match.group(1)
    keywords = await kst.client.get_text(kst, group=2)
    if not keywords:
        await kst.eor("`Provide a keywords!`", time=5)
        return
    yy = await kst.eor("`Searching...`")
    if engine == "google":
        search = "Google"
        url = "https://www.google.com/search?q={}"
    elif engine == "duck":
        search = "DuckDuckGo"
        url = "https://duckduckgo.com/?q={}&kp=-2&kac=1"
    elif engine == "yandex":
        search = "Yandex"
        url = "https://yandex.com/search/?text={}"
    elif engine == "bing":
        search = "Bing"
        url = "https://www.bing.com/search?q={}"
    elif engine == "yahoo":
        search = "Yahoo"
        url = "https://search.yahoo.com/search?p={}"
    elif engine == "baidu":
        search = "Baidu"
        url = "https://www.baidu.com/s?wd={}"
    elif engine == "ecosia":
        search = "Ecosia"
        url = "https://www.ecosia.org/search?q={}"
    result = url.format(keywords.replace("\n", " ").replace(" ", "+")).strip()
    keywords = keywords.replace("\n", " ").strip()
    await yy.eor("**🔎 {} Search Result:**\n\n[{}]({})".format(search, keywords, result))


@kasta_cmd(
    pattern="(un|)short(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2)
    if not text or not (is_url(text) is True):
        await kst.eor("`Provide a valid link!`", time=5)
        return
    yy = await kst.eor("`Processing...`")
    if kst.pattern_match.group(1).strip() == "un":
        res = await Fetch(
            text,
            real=True,
            allow_redirects=False,
            statuses=set(range(301, 308)),
        )
        if not res:
            return await yy.eod("`Try again now!`")
        output = "• **Unshorted Link:** {}\n• **Original Link:** {}".format(res.headers.get("location"), text)
    else:
        url = f"https://da.gd/s?url={text}"
        res = await Fetch(url)
        if not res:
            return await yy.eod("`Try again now!`")
        output = "• **Shorted Link:** {}\n• **Original Link:** {}".format(res.strip(), text)
    await yy.eor(output)


@kasta_cmd(
    pattern="ip$",
    no_crash=True,
)
async def _(kst):
    yy = await kst.eor("`Processing...`")
    ip = await MyIp()
    await yy.eor(ip, parse_mode=parse_pre)


@kasta_cmd(
    pattern="ipinfos?(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    ipaddr = await kst.client.get_text(kst)
    if not ipaddr or not (ipv4(ipaddr) is True):
        await kst.eor("`Provide a valid IP address!`", time=5)
        return
    yy = await kst.eor("`Processing...`")
    url = f"http://ip-api.com/json/{ipaddr}?fields=status,message,continent,country,countryCode,regionName,city,zip,lat,lon,timezone,currency,isp,mobile,query"
    res = await Fetch(url, re_json=True)
    if not res:
        return await yy.eod("`Try again now!`")
    if str(res.get("status")).lower() == "success":
        coordinates = str(res.get("lat") or "") + "," + str(res.get("lon") or "")
        text = """<b><u>IP Address Information</u></b>
├  <b>IP:</b> <code>{}</code>
├  <b>City:</b> <code>{}</code>
├  <b>Region:</b> <code>{}</code>
├  <b>Country:</b> <code>{}</code>
├  <b>Country Code:</b> <code>{}</code>
├  <b>Currency:</b> <code>{}</code>
├  <b>Continent:</b> <code>{}</code>
├  <b>Coordinates:</b> <code>{}</code>
├  <b>Time Zone:</b> <code>{}</code>
├  <b>ISP:</b> <code>{}</code>
├  <b>Mobile:</b> <code>{}</code>
└  <b>Google Map:</b> <code>{}</code>""".format(
            res.get("query"),
            res.get("city") or "?",
            res.get("regionName") or "?",
            res.get("country") or "?",
            res.get("countryCode") or "?",
            res.get("currency") or "?",
            res.get("continent") or "?",
            coordinates,
            res.get("timezone") or "?",
            res.get("isp") or "?",
            humanbool(res.get("mobile")),
            f"https://www.google.com/maps?q={coordinates}",
        )
    else:
        text = """<b><u>IP Address Information</u></b>
├  <b>IP:</b> <code>{}</code>
├  <b>Status:</b> <code>{}</code>
└  <b>Message:</b> <code>{}</code>""".format(
            res.get("query"),
            res.get("status"),
            res.get("message"),
        )
    await yy.eor(text, parse_mode="html")


@kasta_cmd(
    pattern="speedtest$",
    no_crash=True,
)
async def _(kst):
    start = time.perf_counter()
    yy = await kst.eor("`Processing...`")
    try:
        st = await aioify(speedtest.Speedtest)
        st.get_best_server()
        st.download()
        st.upload()
        resp = st.results.dict()
        client = resp.get("client")
        text = """<b><u>SpeedTest completed in {}ms</u></b>
├  <b>Download:</b> <code>{}</code>
├  <b>Upload:</b> <code>{}</code>
├  <b>Ping:</b> <code>{}</code>
├  <b>Internet Service Provider:</b> <code>{}</code>
┊  ├  <b>Rating:</b> <code>{}</code>
┊  ├  <b>IP:</b> <code>{}</code>
┊  ├  <b>Country:</b> <code>{}</code>
└  <b>Sponsor:</b> <code>{}</code>""".format(
            round(time.perf_counter() - start, 3),
            humanbytes(resp.get("download")),
            humanbytes(resp.get("upload")),
            resp.get("ping"),
            client.get("isp"),
            client.get("isprating"),
            client.get("ip"),
            client.get("country"),
            resp.get("server").get("sponsor"),
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(f"**ERROR:**\n`{err}`")


@kasta_cmd(
    pattern="dns(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    link = await kst.client.get_text(kst)
    if not link:
        await kst.eor("`Provide a valid link!`", time=5)
        return
    toget = link
    check_link = is_url(toget)
    if not (check_link is True):
        toget = f"http://{link}"
        check_link = is_url(toget)
    if not (check_link is True):
        return await kst.eod("`Input is not supported link!`")
    yy = await kst.eor("`Processing...`")
    hostname = ".".join(urllib.parse.urlparse(toget).netloc.split(".")[-2:])
    url = f"https://da.gd/dns/{hostname}"
    res = await Fetch(url)
    if res:
        await yy.eor(f"<b>DNS Records {hostname}</b>\n<pre>{res.strip()}</pre>", parse_mode="html")
        return
    await yy.eor(f"`Cannot resolve {hostname} dns.`")


@kasta_cmd(
    pattern="whois(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    link = await kst.client.get_text(kst)
    if not link:
        await kst.eor("`Provide a valid link or IP address!`", time=5)
        return
    toget = link
    check_link = is_url(toget)
    if not (check_link is True):
        toget = f"http://{link}"
        check_link = is_url(toget)
    if not (check_link is True):
        return await kst.eod("`Input is not supported link!`")
    yy = await kst.eor("`Processing...`")
    if ipv4(link) is True:
        hostname = link
    else:
        hostname = ".".join(urllib.parse.urlparse(toget).netloc.split(".")[-2:])
    url = f"https://da.gd/w/{hostname}"
    res = await Fetch(url)
    if res:
        await yy.eor(f"<b>WHOIS For {hostname}</b>\n<pre>{res.strip()}</pre>", parse_mode="html")
        return
    await yy.eod(f"`Cannot resolve {hostname} whois.`")


@kasta_cmd(
    pattern="http(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    link = await kst.client.get_text(kst)
    if not link:
        await kst.eor("`Provide a valid link!`", time=5)
        return
    toget = link
    check_link = is_url(toget)
    if not (check_link is True):
        toget = f"http://{link}"
        check_link = is_url(toget)
    if not (check_link is True):
        return await kst.eod("`Input is not supported link!`")
    yy = await kst.eor("`Processing...`")
    url = f"https://da.gd/headers?url={toget}"
    res = await Fetch(url)
    if res:
        await yy.eor(f"<b>HTTP Headers {toget}</b>\n<pre>{res.strip()}</pre>", parse_mode="html")
        return
    await yy.eod(f"`Cannot resolve {toget} headers.`")


@kasta_cmd(
    pattern="pinger(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    dns = await kst.client.get_text(kst)
    if not dns:
        await kst.eor("`Provide a valid DNS or IP address!`", time=5)
        return
    yy = await kst.eor("`Processing...`")
    duration = Pinger(dns)
    await yy.eor(f"• **DNS:** `{dns}`\n• **Ping Speed:** `{duration}`")


plugins_help["webtools"] = {
    "{i}google [keywords]/[reply]": "How to Google...",
    "{i}duck [keywords]/[reply]": "How to DuckDuckGo...",
    "{i}yandex [keywords]/[reply]": "How to Yandex...",
    "{i}bing [keywords]/[reply]": "How to Bing...",
    "{i}yahoo [keywords]/[reply]": "How to Yahoo...",
    "{i}baidu [keywords]/[reply]": "How to Baidu...",
    "{i}ecosia [keywords]/[reply]": "How to Ecosia...",
    "{i}short [link]/[reply]": "Shorten a link into `da.gd` link.",
    "{i}unshort [short_link]/[reply]": "Reverse the shortened link to real link.",
    "{i}ip": "Get my current public IP address.",
    "{i}ipinfo [ip_address]/[reply]": "Get information a given IP address.",
    "{i}speedtest": "Test my server speed by ookla.",
    "{i}dns [link]/[reply]": "Fetch and return all DNS records for a given link.",
    "{i}whois [link/ip]/[reply]": "Whois a given link or IP address.",
    "{i}http [link]/[reply]": "Show HTTP Headers a given link.",
    "{i}pinger [dns/ip]/[reply]": "Pings a specific DNS or IP address.",
}

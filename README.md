

[![Bot API Version](https://img.shields.io/badge/Bot%20API-v4.8-f36caf.svg?style=flat-square)](https://core.telegram.org/bots/api)


Telegram ticketing implementation:

<table>
<tr>
<th><img src="https://i.imgur.com/EEvyQLZ.jpg" /></th>
<th><img src="https://i.imgur.com/zRPvA0f.jpg" /></th>
</tr>
</table>

## Documentation

`reviewsParser` was built on top of [`Telegraf`](https://github.com/telegraf/telegraf) libary.

[Telegraf documentation](http://telegraf.js.org).

and python source code that parce URL for new upcoming reviews.

## Features

When a user sends a review to the site review section it will parse a new review which will be forwarded to the telegram group or person. Add reviews are stored in local SQLlite database by last date.


Features:
* Parsing sites per comment sections ( js or pure html )
* Database with stored reviews
* Alertign user or group of new incoming reviews

## Installation


**Docker** container:

Either with docker-compose:

```
docker-compose up -d
```

set: 
 - URL
 - TG token
 - chatID 



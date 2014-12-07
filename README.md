Das Orakel
==========

Dies ist das Orakel, das im Support-Raum von lima-city oft anzutreffen ist.  Es
antwortet auf einige Fragen und reagiert auf manche Ereignisse.

Systemvoraussetzungen
=====================

Um das Orakel ausführen zu können wird Python 3 benötigt, mit folgenden Modulen:
- SleekXMPP
- dnspython3
- pika
- pypygo
- beautifulsoup4

Außerdem wird ein konfigurierter, AMQP-fähiger Message Broker benötigt (z.B. [RabbitMQ](http://www.rabbitmq.com/)).

Konfiguration
=============

Über die Datei ```orakel.cfg``` wird der Bot konfiguriert:

```
[messaging]
hostname = localhost
username = guest
password = guest
exchange = oracle

[xmpp]
jid = username@jabber.lima-city.de
password = secret
room = support@conference.jabber.lima-city.de
nick = Orakel

[db]
questions = messages.csv
searchengines = searchengines.csv
storage = storage.json

[modules]
greetings = hallo,moin,hi,hai,servus,aloha,huhu
hands = False
flooding = 750
paste = https://paste42.de/
noalphabet = k,T
op = mod-nick
troll = Du wurdest gemuted.

[timeouts]
hands = 10
greet = 120
alphabet = 10
count = 10
```

- `troll`: Durch `;` getrennte Liste von Troll-Nachrichten
- `hands`: Reagieren auf `\o/`, `o-` & Co.
- `*grace`: Diese Zeit (in Sekunden) muss vergehen, bevor auf ein Event wieder
  reagiert wird.

Hilfe
=====

Siehe [help.md](https://github.com/hackyourlife/orakel/blob/master/help.md)

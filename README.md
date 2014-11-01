Das Orakel
==========

Dies ist das Orakel, das im Support-Raum von lima-city oft anzutreffen ist.  Es
antwortet auf einige Fragen und reagiert auf manche Ereignisse.

Konfiguration
=============

Über die Datei ```orakel.cfg``` wird der Bot konfiguriert:

```
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

[timeouts]
hands = 10
greet = 120
alphabet = 30
```

- `hands`: Reagieren auf `\o/`, `o-` & Co.
- `*grace`: Diese Zeit (in Sekunden) muss vergehen, bevor auf ein Event wieder
  reagiert wird.

Hilfe
=====

Siehe [help.md](https://github.com/hackyourlife/orakel/blob/master/help.md)

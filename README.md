Das Orakel
==========

Dies ist das Orakel, das im Support-Raum von lima-city oft anzutreffen ist.  Es
antwortet auf einige Fragen und reagiert auf manche Ereignisse.

Konfiguration
=============
```js
var config = {
	jid: 'username@jabber.lima-city.de/orakel',
	password: 'password',
	room_jid: 'support@conference.jabber.lima-city.de',
	room_nick: 'Orakel',
	hands: false,
	handsgrace: 10,
	greetgrace: 120
};
```

- `hands`: Reagieren auf `\o/`, `o-` & Co.
- `*grace`: Diese Zeit (in Sekunden) muss vergehen, bevor auf ein Event wieder
  reagiert wird.

Hilfe
=====

Siehe [help.md](https://github.com/hackyourlife/orakel/blob/master/help.md)

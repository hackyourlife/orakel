<!-- vim:set ft=markdown: -->

Fragen
======

Das Orakel beantwortet einige Fragen. Welche dies sind lässt sich der
[Definition](https://github.com/hackyourlife/orakel/blob/master/messages.csv)
entnehmen.

Aktionen
========

* `sag`: Das Orakel gibt den Text, der `sag` folgt aus. Aus `sag hallo` wird
  `hallo`.
* `merke`: Der folgende Text wird gemerkt. Er kann mit `sprich` wieder
  ausgegeben werden.
* `sprich`: siehe `merke`
* `ist das schlimm` → `ja`, `nein` oder `vielleicht`
* `stimmt das` → `ja` oder `nein`
* `ist das falsch` → `ja` oder `nein`
* `aus!`: Das Orakel hört auf, auf `\o/` & Co. zu reagieren.
* `fass!`: Gegenteil von `aus!`

Allgemeines
===========

Das Orakel reagiert auf folgende Meldungen, denen nicht `Orakel` vorangestellt
ist.

* `ping`: Das Orakel antwortet mit `pong`
* `\o/`, `/o/`, `\o\`, `o-`, `_o/`: was eben dazu gehört
* manche Fragen werden direkt beantwortet

Privater Chat
=============

* `?`: Liste aller geladenen Fragen wird ausgegeben
* `ping` → `pong`

Moderator-Aktionen
=================

Befehle
-------

* `kick <nick> [reason]`
* `show auto kick jid`
* `show auto kick nick`
* `show mute`

Konfiguration
-------------

* `auto kick jid <jid>`
* `auto kick nick <nick>`
* `troll jid <jid>`
* `troll nick <nick>`
* `mute <nick>`

Konfigurationsanweisungen können durch ein vorangestelltes `no` wieder
aufgehoben werden. Beispiel: `no mute user` hebt die Konfigurationsanweisung
`mute user` auf.

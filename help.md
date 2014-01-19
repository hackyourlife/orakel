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

Operator-Aktionen
-----------------
* `ops`: Liste der Operatoren wird angezeigt
* `op nick`: `nick` wird als Operator hinzugefügt
* `deop nick`: `nick` wird der Operator-Status entzogen
* `trolled`: Liste aller getrollten wird angezeigt
* `troll nick`: Der Benutzer `nick` bekommt bei jeder geschriebenen Zeile eine störende private Nachricht
* `untroll nick`: Der Benutzer `nick` wird nicht länger getrollt

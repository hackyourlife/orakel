#!/bin/node

var util = require('util');
var fs = require('fs');
var xmpp = require('node-xmpp');

eval(fs.readFileSync('config.js').toString());

function oneof(list) {
	return list[Math.floor((Math.random() * list.length))];
}

config.abcgrace = 30;

var capslocked = {};
var capscleared = {};
var knownquestions = {};
var questionlist = [];

var state = {
	lasthands: 0,
	lastgreet: 0,
	lastabc: 0,
	remembered: '…',
	mutelist: [],
	operators: []
};

function saveState() {
	util.log('saving state');
	var s = JSON.stringify(state);
	fs.writeFileSync('state', s);
}

function loadState() {
	util.log('loading state');
	var s = fs.readFileSync('state').toString();
	state = JSON.parse(s);
}

function setProperty(name, value) {
	state[name] = value;
	saveState();
}

function mute(user) {
	util.log('muting user "' + user + '"');
	if(state.mutelist.indexOf(user) != -1)
		return;
	state.mutelist.push(user);
	saveState();
}

function unmute(user) {
	util.log('unmuting user "' + user + '"');
	var id = state.mutelist.indexOf(user);
	if(id != -1)
		state.mutelist.splice(id, 1);
	saveState();
}

function isMuted(user) {
	return state.mutelist.indexOf(user) != -1;
}

function addOperator(user) {
	util.log('"' + user + '" is now operator');
	if(state.operators.indexOf(user) != -1)
		return;
	state.operators.push(user);
	saveState();
}

function rmOperator(user) {
	util.log('"' + user + '" is no longer operator');
	var id = state.operators.indexOf(user);
	if(id != -1)
		state.operators.splice(id, 1);
	saveState();
}

function isOperator(user) {
	return state.operators.indexOf(user) != -1;
}

function readMessages(file) {
	var data = fs.readFileSync(file).toString().split('\n');
	for(var i = 0; i < data.length; i++) {
		var line = data[i].trim();
		if(line.length < 3)
			continue;
		var x = line.indexOf(';');
		if(x == -1)
			continue;
		var question = line.substring(0, x).trim();
		var response = line.substring(x + 1).trim();
		knownquestions[question] = response;
		questionlist.push(question);
	}
	util.log(questionlist.length + ' questions loaded');
}

readMessages('messages.csv');
loadState();

function clearCapsLocked(from) {
	if(capslocked[from] !== undefined)
		capscleared[from] = capslocked[from];
	else
		capscleared[from] = undefined;
	capslocked[from] = undefined;
}

function processCapsLocked(from) {
	if(capslocked[from] === undefined) {
		capslocked[from] = 1;
	} else {
		capslocked[from]++;
	}

	if(capscleared[from] !== undefined) {
		capslocked[from] += capscleared[from];
		capscleared[from] = undefined;
		return true;
	}
	return capslocked[from];
}

function processPrivate(message, from) {
	var parts = message.split(' ');
	if(parts.length == 1) {
		switch(parts[0]) {
			case 'ping':
				return { sendPublic: false, text: 'pong' };
			case '?':
				return { sendPublic: false, text: 'Öffentlich: ' +
					questionlist.join(', ') };
			case 'save':
				saveState();
				return null;
			case 'load':
				loadState();
				return null;
			case 'trolled':
				if(!isOperator(getNick(from)))
					return null;
				return { sendPublic: false, text: 'Trolled: ' + state.mutelist.join(', ') };
			case 'ops':
			case 'operators':
				if(!isOperator(getNick(from)))
					return null;
				return { sendPublic: false, text: 'Operators: ' + state.operators.join(', ') };
		}
	} else if(parts.length > 1) {
		switch(parts[0]) {
			case 'say':
				return {
					sendPublic: true,
					text: message.substring(message.indexOf('say') + 4).trim()
				};
			case 'troll':
				if(!isOperator(getNick(from)))
					return null;
				var username = parts[1];
				mute(username);
				return {
					sendPublic: false,
					text: 'User "' + username + '" wird getrollt'
				};
			case 'untroll':
				if(!isOperator(getNick(from)))
					return null;
				var username = parts[1];
				unmute(username);
				return {
					sendPublic: false,
					text: 'User "' + username + '" wird nicht mehr getrollt'
				};
			case 'op':
				if(!isOperator(getNick(from)))
					return null;
				var username = parts[1];
				addOperator(username);
				return {
					sendPublic: false,
					text: 'User "' + username + '" ist jetzt Operator'
				};
			case 'deop':
				if(!isOperator(getNick(from)))
					return null;
				var username = parts[1];
				rmOperator(username);
				return {
					sendPublic: false,
					text: 'User "' + username + '" ist kein Operator mehr'
				};
			case 'merke':
				setProperty('remembered', message.substring(parts[0].length + 1).trim());
				return null;
			case 'hands':
				config.hands = parts[1] == 'on';
				return null;
			case 'no':
				if(parts.length > 2) {
					switch(parts[1]) {
						case 'troll':
							if(!isOperator(getNick(from)))
								return null;
							var username = parts[2];
							unmute(username);
							return {
								sendPublic: false,
								text: 'User "' + username + '" wird nicht mehr getrollt'
							};
						case 'op':
							if(!isOperator(getNick(from)))
								return null;
							var username = parts[2];
							rmOperator(username);
							return {
								sendPublic: false,
								text: 'User "' + username + '" ist kein Operator mehr'
							};
					}
				}
				return null;
		}
	}
	return null;
}

function process(message, from) {
	var nick = getNick(from);
	if(isMuted(nick)) {
		privmsg(from, oneof(['Du wurdest gemuted', 'La le lu, nur der Mann im Mond hört zu …', 'Lalalalala', 'Hihihihihi', 'Trolololol', 'Hahahahaha']));
	}
	if(isMentation(message)) {
		var msg = message.substring(config.room_nick.length + 1);
		if(msg.charAt(0) == ':' || msg.charAt(0) == ',')
			msg = message.substring(1);
		msg = msg.trim();

		if(/^bist du ein bot\??$/i.test(msg))
			return 'Nein';
		if(/^(wer|was) bist du\??$/i.test(msg))
			return 'das Orakel';
		if(/^was machst du\??$/i.test(msg))
			return 'existieren';
		if(/^wer ist dein meister\??$/i.test(msg))
			return '/me hat keinen Meister';
		if(/^ist das schlimm\??$/i.test(msg))
			return oneof(['ja', 'nein', 'vielleicht']);
		if(/^stimmt das\??$/i.test(msg) || /^stimmt das[, ]/i.test(msg))
			return oneof(['ja', 'nein']);
		if(/^ist das falsch\??/i.test(msg))
			return oneof(['nein', 'ja']);
		if(/^(wie spät(ist es)?|zeit)\??/i.test(msg))
			return new Date();

		var parts = msg.split(' ');
		if(parts.length == 1) {
			var command = parts[0].toLowerCase();
			if(command.charAt(command.length - 1) == '?')
				command = command.substring(0, command.length - 1)
			if(knownquestions[command] !== undefined)
				return knownquestions[command];
			switch(command) {
				case 'sprich':
				case 'sprich!':
					return state.remembered;
				case 'hä?':
					return 'Wos is?';
				case 'aus!':
					config.hands = false;
					return ':(';
				case 'fass!':
					config.hands = true;
					return ':)';
				case 'hallo':
				case 'moin':
				case 'hi':
				case 'hai':
				case 'servus':
				case 'huhu':
					return 'hallo';
				case 'stinkt':
					return 'nein';
				case 'ping': // anti-tchab hack
					switch(nick) {
						case 'tchab':
							return oneof(['Für dich immer noch »pink«!', 'Gib a rua, Schwuggele', 'Klappe zu, Schwulibert!']);
						case 'T':
							return oneof(['pong', '*pflopp*', 'peng!']);
					}
					return oneof(['leck mich!', 'nix da', 'du kannst mich mal :P', 'hupf in Gatsch!']);
				case 'pink':
					return 'ponk';
				default:
					return null;
			}
		} else {
			switch(parts[0]) {
				case 'merke':
					setProperty('remembered', msg.substring(parts[0].length + 1).trim());
					break;
				case 'sag':
					return msg.substring(parts[0].length + 1).trim();
				case 'Du':
				case 'du':
					return 'nein ' + nick + ', ' + parts[0] + ' ' + msg.substring(parts[0].length + 1).trim();
				case 'stinkt':
					return 'nein';
				case 'troll':
					if(!isOperator(getNick(from)))
						return null;
					var username = parts[1];
					mute(username);
					return 'User "' + username + '" wird getrollt';
				case 'untroll':
					if(!isOperator(getNick(from)))
						return null;
					var username = parts[1];
					unmute(username);
					return 'User "' + username + '" wird nicht mehr getrollt';
				case 'op':
					if(!isOperator(getNick(from)))
						return null;
					var username = parts[1];
					addOperator(username);
					return 'User "' + username + '" ist jetzt Operator';
				case 'deop':
					if(!isOperator(getNick(from)))
						return null;
					var username = parts[1];
					rmOperator(username);
					return 'User "' + username + '" ist kein Operator mehr';
				case 'no':
					if(parts.length > 2) {
						switch(parts[1]) {
							case 'troll':
								if(!isOperator(getNick(from)))
									return null;
								var username = parts[2];
								unmute(username);
								return 'User "' + username + '" wird nicht mehr getrollt';
							case 'op':
								if(!isOperator(getNick(from)))
									return null;
								var username = parts[2];
								rmOperator(username);
								return 'User "' + username + '" ist kein Operator mehr';
						}
					}
					break;
			}
			return null;
		}
	} else {
		// greet - self
		var greetings = [ 'hallo', 'moin', 'hi', 'hai', 'servus', 'aloha', 'huhu' ];
		var greet = false;
		var deltagreet = (Date.now() - state.lastgreet) / 1000;
		for(var i = 0; i < greetings.length; i++) {
			if(message.toLowerCase() == greetings[i] + ' ' + config.room_nick.toLowerCase())
				greet = true;
		}
		if(greet && (deltagreet > config.greetgrace)) {
			setProperty('lastgreet', Date.now());
			return oneof(['hi', 'hai', 'hallo', 'huhu']);
		}

		// caps
		/*
		var caps = 0;
		var nocaps = 0;
		for(var i = 0; i < message.length; i++) {
			var c = message[i];
			if((c >= 'A') && (c <= 'Z'))
				caps++;
			if((c >= 'a') && (c <= 'z'))
				nocaps++;
		}
		var respond = false;
		if(((caps + nocaps) >= 5) && (caps > nocaps) && (caps > 5)) {
			respond = processCapsLocked(from);
		} else {
			clearCapsLocked(from);
		}
		var nick = from.substring(config.room_jid.length + 1);
		switch(respond) {
			case 1:
				return nick + ': klemmt bei dir zufällig die SHIFT-Taste?';
			case 2:
				return nick + ': hör auf zu schreien!';
			case 3:
				return 'root?';
			case true:
				return nick + ': du lernst wohl nicht…';
		}
		*/

		var delta = (Date.now() - state.lasthands) / 1000;
		// questions
		if(message.indexOf('?') !== -1) {
			var metaquestion = /wer (von euch )?kennt sich.* mit .* aus|(jemand|wer) (hier|da).* der sich (mit .* auskennt|auskennt mit)|kennt sich(hier )? wer mit .* aus/gi;
			var alive = /^((hi|hallo) )?(ist )?(gerade )?(wer|jemand|irgendwer) (da|hier)$/i;
			var noalive = /^(niemand|keiner) (da|hier)$/i;
			var mysql = /^wo finde ich (die|meine) mysql[ -](zugangs)?daten|^wo sehe ich die daten für MySQL|^wie komme? ich (hier )?auf meine mysql/gi;
			var pma = /^kann (mir )?(jemand|wer|irgendwer) sagen wo ich (hier )?(mein )?phpmyadmin finde/gi;
			var filemanager = /^wei[sß] (jemand|wer|irgendwer),? wo (der file-?manager (hin(gekommen)?|zu finden) ist|ich den file-?manager finde)/gi;
			var ftp = /^(wie|wo) (bekommt|findet) man (die|seine) ftp[- ](zugangs-?)?daten|(wie|wo) (bekomme|finde) ich (meine|die) ftp[- ](zugangs-?)?daten/gi;
			var rm = /^(wo|wie) kann ((man sich|ich mich)|(ich meinen|man seinen) (acc|account)) (hier )?löschen$|^wo ist? der account[- ](löschen|entfernen)[- ]knopf$/gi;
			var buydb = /^((man muss|muss man) (hier )?)?(dbs?|mysql|datenbank(en)?) kaufen$/gi;
			var understand = false;
			var questions = message.split('?');
			for(var i = 0; i < questions.length; i++) {
				var question = questions[i];
				if(metaquestion.test(question)) {
					return '„Don\'t ask to ask, or ask if anyone is here, or if anyone is alive, or if anyone uses something. Just ask!“';
				} else if(mysql.test(question)) {
					return 'Die Zugangsdaten zum MySQL-Server findest du unter https://www.lima-city.de/usercp/databases';
				} else if(filemanager.test(question)) {
					return 'Den lima-city-Filemanager findest du unter http://filemanager.lima-city.de/';
				} else if(ftp.test(question)) {
					return 'Deine FTP-Zugangsdaten findest du unter https://www.lima-city.de/usercp/ftp';
				} else if(pma.test(question)) {
					return 'PHPMyAdmin findest du unter http://mysql.lima-city.de/';
				} else if(alive.test(question)) {
					return 'nein';
				} else if(noalive.test(question)) {
					return 'siehst du wen?';
				} else if(rm.test(question)) {
					return 'https://www.lima-city.de/usercp/page%3Adelete';
				} else if(buydb.test(question)) {
					return 'Du bekommst eine Datenbank nach 10 Beiträgen im Forum, wenn du eine Domain kaufst, oder du kaufst sie dir gegen echtes Geld. Außerdem kannst du auch Datenbanken von anderen Anbietern hier nutzen.';
				}
			}
		} else if(message.toLowerCase() == 'ping') {
			if(isMuted(nick)) {
				return oneof([ 'Bäh!', 'peng!' ]);
			}
			return 'pong';
		} else if(message.toLowerCase() == '*ping*') {
			return '*pong*';
		} else if(message.toLowerCase() == 'pink') {
			return 'ponk';
		} else if(/^[A-Za-z]$/.test(message)) {
			delta = (Date.now() - state.lastabc) / 1000;
			if(delta > config.abcgrace) {
				setProperty('lastabc', Date.now());
				var charcode = message.toUpperCase().charCodeAt(0);
				var next = charcode + 1;
				if(next > 0x5A)
					next = 0x41;
				var c = String.fromCharCode(next);
				if(/^[a-z]$/.test(message))
					c = c.toLowerCase();
				return c;
			}
		} else if(config.hands) {
			if(message == '\\o/') {
				if(delta > config.handsgrace) {
					setProperty('lasthands', Date.now());
					return '\\o/';
				}
				return null;
			} else if(message == '/o/') {
				return '\\o\\';
			} else if(message == 'o-') {
				return '-o';
			} else if(message == '_o/') {
				return '\\o_';
			}
		}
	}
	return null;
}

function isMentation(message) {
	if(message.toLowerCase().substring(0, config.room_nick.length) == config.room_nick.toLowerCase()) {
		var c = message.charAt(config.room_nick.length);
		if(c == ' ' || c == ':' || c == ',')
			return true;
	}
	return false;
}

function getNick(from) {
	return from.substring(config.room_jid.length + 1);
}

function privmsg(to, text) {
	util.log('privmsg => ' + to + ': ' + text);
	cl.send(new xmpp.Element('message', { to: to, type: 'chat' })
		.c('body')
		.t(text));
}

var cl = new xmpp.Client({
	jid: config.jid,
	password: config.password
});

cl.on('online', function() {
	util.log('we are online');

	cl.send(new xmpp.Element('presence', { type: 'available' })
		.c('show')
		.t('chat'));
	cl.send(new xmpp.Element('presence', { to: config.room_jid + '/' + config.room_nick })
		.c('x', { xmlns: 'http://jabber.org/protocol/muc' })
		.c('history', { maxstanzas: 0, seconds: 1 }));

	setInterval(function() {
		cl.send(new xmpp.Message({}));
	}, 30000);
});

cl.on('stanza', function(stanza) {
	if(stanza.attr.type == 'error') {
		util.error(stanza);
		return;
	}

	if(!stanza.is('message') || !stanza.attrs.type == 'groupchat')
		return;

	if(stanza.attrs.from == config.room_jid + '/' + config.room_nick)
		return;

	var body = stanza.getChild('body');

	if(!body)
		return;

	var message = body.getText();

	var private = stanza.attrs.type == 'chat';

	var response = null;
	if(private) {
		response = processPrivate(message, stanza.attrs.from);
		if(response == null)
			return;
		util.log(stanza.attrs.from + ': "' + message + '" => "' + response.text + '"');
		var params = {};
		if(response.sendPublic) {
			params = {
				to: config.room_jid,
				type: 'groupchat'
			};
		} else {
			params = {
				to: stanza.attrs.from,
				type: 'chat'
			};
		}

		cl.send(new xmpp.Element('message', params)
			.c('body')
			.t(response.text));
		return;
	} else {
		response = process(message, stanza.attrs.from);
	}
	if(response === null)
		return;
	util.log('"' + message + '" => "' + response + '"');

	// is private
	var params = {};
	if(stanza.attrs.from.indexOf(config.room_jid) === 0) {
		params.to = config.room_jid;
		params.type = 'groupchat';
		// mentation?
		//if(isMentation(message)) {
		//	response = stanza.attrs.from.substring(config.room_jid.length + 1)
		//		+ ': ' + response;
		//}
	} else {
		params.to = stanza.attrs.from;
		params.type = 'chat';
	}

	// send response
	cl.send(new xmpp.Element('message', params)
		.c('body')
		.t(response));
});

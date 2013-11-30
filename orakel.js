var util = require('util');
var fs = require('fs');
var xmpp = require('node-xmpp');

eval(fs.readFileSync('config.js').toString());

function oneof(list) {
	return list[Math.floor((Math.random() * list.length))];
}

var capslocked = {};
var capscleared = {};

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
				return { sendPublic: false, text: 'Öffentlich: lima-city?, hilfe?, zip?, ftp?, mysql?, pma?, filemanager?, subdomain?, auktion?, ticket?, phpinfo?, metafrage?' };
		}
	} else if(parts.length > 1) {
		switch(parts[0]) {
			case 'say':
				return {
					sendPublic: true,
					text: message.substring(message.indexOf('say') + 4).trim()
				};
		}
	}
	return null;
}

var remembered = '…';
function process(message, from) {
	if(isMentation(message)) {
		var msg = message.substring(config.room_nick.length + 1);
		if(msg.charAt(0) == ':')
			msg = message.substring(1);
		msg = msg.trim();

		if(/^bist du ein bot\??$/i.test(msg))
			return 'Nein';
		if(/^(wer|was) bist du\??$/i.test(msg))
			return 'das Orakel';
		if(/^ist das schlimm\??$/i.test(msg))
			return oneof(['ja', 'nein', 'vielleicht', 'möglicherweise']);

		var parts = msg.split(' ');
		if(parts.length == 1) {
			switch(parts[0]) {
				case 'lima-city?':
					return 'https://www.lima-city.de/';
				case 'hilfe?':
					return 'https://www.lima-city.de/2008/help';
				case 'formate?':
				case 'inhalte?':
				case 'zip?':
					return 'https://www.lima-city.de/2008/speicherplatz#inhalte';
				case 'ftp?':
					return 'https://www.lima-city.de/usercp/ftp';
				case 'mysql?':
					return 'https://www.lima-city.de/usercp/databases';
				case 'pma?':
					return 'http://mysql.lima-city.de/';
				case 'filemanager?':
					return 'http://filemanager.lima-city.de/';
				case 'subdomain?':
					return 'https://www.lima-city.de/usercp/subdomains';
				case 'auktion?':
					return 'https://www.lima-city.de/auctions';
				case 'ticket?':
					return 'https://www.lima-city.de/usercp/tickets/';
				case 'phpinfo?':
					return 'http://system.lima-city.de/info.php';
				case 'metafrage?':
				case 'metaquestion?':
					return '„Don\'t ask to ask, or ask if anyone is here, or if anyone is alive, or if anyone uses something. Just ask!“';
				case 'sprich':
					return remembered;
				case 'hä?':
					return 'Wos is?';
				case 'hallo':
				case 'moin':
				case 'hi':
				case 'hai':
				case 'servus':
					return 'hallo';
				case 'stinkt':
					return 'nein';
				default:
					return null;
			}
		} else {
			switch(parts[0]) {
				case 'merke':
					remembered = msg.substring(parts[0].length + 1).trim();
					break;
				case 'sag':
					return msg.substring(parts[0].length + 1).trim();
				case 'stinkt':
					return 'nein';
			}
			return null;
		}
	} else {
		// greet - self
		var greetings = [ 'hallo', 'moin', 'hi', 'hai', 'servus', 'aloha' ];
		var greet = false;
		for(var i = 0; i < greetings.length; i++) {
			if(message.toLowerCase() == greetings[i] + ' ' + config.room_nick.toLowerCase())
				greet = true;
		}
		if(greet) {
			return 'hi';
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

		// questions
		if(message.indexOf('?') !== -1) {
			var metaquestion = /wer (von euch )?kennt sich.* mit .* aus|(jemand|wer) (hier|da).* der sich (mit .* auskennt|auskennt mit)|kennt sich(hier )? wer mit .* aus/gi;
			var alive = /^((hi|hallo) )?(ist )?(gerade )?(wer|jemand|irgendwer) (da|hier)$/i;
			var mysql = /^wo finde ich meine mysql[ -](zugangs)?daten|^wo sehe ich die daten für MySQL|^wie komme? ich auf meine mysql/gi;
			var understand = false;
			var questions = message.split('?');
			for(var i = 0; i < questions.length; i++) {
				var question = questions[i];
				if(metaquestion.test(question)) {
					return '„Don\'t ask to ask, or ask if anyone is here, or if anyone is alive, or if anyone uses something. Just ask!“';
				} else if(mysql.test(question)) {
					return 'Die Zugangsdaten zum MySQL-Server findest du unter https://www.lima-city.de/usercp/databases';
				} else if(alive.test(question)) {
					return 'nein';
				}
			}
		} else if(message.toLowerCase() == 'ping') {
			return 'pong';
		} else if(message == '\\o/') {
			return '\\o/';
		} else if(message == '/o/') {
			return '\\o\\';
		} else if(message == 'o-') {
			return '-o';
		}
	}
	return null;
}

function isMentation(message) {
	if(message.toLowerCase().substring(0, config.room_nick.length) == config.room_nick.toLowerCase()) {
		var c = message.charAt(config.room_nick.length);
		if(c == ' ' || c == ':')
			return true;
	}
	return false;
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
		console.log(stanza.attrs.from + ': "' + message + '" => "' + response.text + '"');
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
	console.log('"' + message + '" => "' + response + '"');

	// is private
	var params = {};
	if(stanza.attrs.from.indexOf(config.room_jid) === 0) {
		params.to = config.room_jid;
		params.type = 'groupchat';
		// mentation?
		if(message.substring(0, config.room_nick.length) == config.room_nick) {
			response = stanza.attrs.from.substring(config.room_jid.length + 1)
				+ ': ' + response;
		}
	} else {
		params.to = stanza.attrs.from;
		params.type = 'chat';
	}

	// send response
	cl.send(new xmpp.Element('message', params)
		.c('body')
		.t(response));
});

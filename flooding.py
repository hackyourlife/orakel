# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

class Flooding(object):
	def __init__(self, config):
		self.config = config
		self.maxlength = config.getint("modules", "flooding")
		self.paste = config.get("modules", "paste")

	def __call__(self, msg, nick, send_message):
		if len(msg) >= self.maxlength:
			send_message('ey! Nutz in Zukunft bitte z.B. %s !' %
					self.paste)
			return True
		return False

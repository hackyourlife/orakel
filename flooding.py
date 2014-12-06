# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

from module import Module, MUC

class Flooding(Module):
	def __init__(self, maxlength, paste, **keywords):
		super(Flooding, self).__init__([MUC], name=__name__, **keywords)
		self.maxlength = maxlength
		self.paste = paste

	def muc_msg(self, msg, **keywords):
		if len(msg) >= self.maxlength:
			self.send_muc("ey! Nutz in Zukunft bitte z.B. %s !" %
					self.paste)

# -*- coding: utf-8 -*-

import locale
import gettext
import os

path_i18n = os.getcwd() + '/i18n/'

t = gettext.translation('Obb', path_i18n)
_ = t.ugettext
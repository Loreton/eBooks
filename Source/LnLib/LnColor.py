#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# updated by ...: Loreto Notarantonio
# Version ......: 24-03-2020 17.17.55

import sys, os

# ---- importing colorama as zip file...
# this_path = os.path.dirname(__file__)
# colorama = os.path.join(this_path, 'colorama.zip')
# sys.path.append(colorama)
# import colorama_039 as colorama
# or ...
from . import colorama_039 as colorama
# ----


class LnColor:
    colorama.init(wrap=True, convert=None, strip=None, autoreset=False)
    # for i in dir('LnColors'): print (i)
    '''
        devo mantenere i valori seguenti perché a volte
        devo mandare una stringa pronta con il colore e non posso usare il printColor(msg) oppure il getColor()
        in quanto ho una stringa multicolor
        usageMsg = " {COLOR}   {TEXT} {COLRESET}[options]".format(COLOR=C.YEL, TEXE='Loreto', COLRESET=C.RESET)

    '''
    FG         = colorama.Fore
    BG         = colorama.Back
    HI         = colorama.Style

    _black       = FG.BLACK
    _red         = FG.RED              ; _redH     = _red     + HI.BRIGHT
    _green       = colorama.Fore.GREEN ; _greenH   = _green   + HI.BRIGHT
    _yellow      = FG.YELLOW           ; _yellowH  = _yellow  + HI.BRIGHT
    _blue        = FG.BLUE             ; _blueH    = _blue    + HI.BRIGHT
    _magenta     = FG.MAGENTA          ; _magentaH = _magenta + HI.BRIGHT
    _cyan        = FG.CYAN             ; _cyanH    = _cyan    + HI.BRIGHT
    _white       = FG.WHITE            ; _whiteH   = _white   + HI.BRIGHT

    RESET        = HI.RESET_ALL
    BW           = FG.BLACK + BG.WHITE
    BWH          = FG.BLACK + BG.WHITE + HI.BRIGHT
    YelloOnBlask = FG.BLACK + BG.YELLOW

    _default = HI.RESET_ALL + FG.WHITE + BG.BLACK
    callerFunc = sys._getframe(1).f_code.co_name




        #  aliases
    _error    = _redH
    _warning  = _magentaH
    _info     = _greenH
    _fucsia   = _magentaH

    def __init__(self, filename=None):
        self._stdout = None
        self._stdout_colored = None
        self.colored_text = ''
        self.normal_text  = ''

        if filename:
            name,ext = filename.rsplit('.',1)
            colored_filename = name + '_colored.' + ext

            self._stdout = open(filename, "w", encoding='utf-8')
            self._stdout_colored = open(colored_filename, "w", encoding='utf-8')


    def setColor(self,  color=''):
        print (self._default + color, end='' )

    def getColored(self, **args):
        self._prepareText (**args)
        return self.colored_text


    def toFile(self, end):
        if self._stdout:
            self._stdout.write('{0}{1}'.format(self.normal_text, end))
            self._stdout.flush()

        if self._stdout_colored:
            self._stdout_colored.write('{0}{1}'.format(self.colored_text, end))
            self._stdout_colored.flush()



    def resetColor(self, **args): self.pprint(color=self._default, **args)


    def error(self, **args): self.pprint(color=self._redH, **args)

    def yellow(self, **args): self.pprint(color=self._yellow, **args)
    def cyan(self, **args): self.pprint(color=self._cyan, **args)
    def magenta(self, **args): self.pprint(color=self._magenta, **args)

    def yellowH(self, **args): self.pprint(color=self._yellowH, **args)
    def cyanH(self, **args): self.pprint(color=self._cyanH, **args)
    def magentaH(self, **args): self.pprint(color=self._magentaH, **args)

        # ----------------------------------------------
        # - print
        # ----------------------------------------------
    def pprint(self, end='\n', autoreset=True, toFile=False, **args):
        self._prepareText (**args)

        try:
            print (self.colored_text, end=end )

        except (UnicodeEncodeError):
            print ('{0} function: {1} - UnicodeEncodeError on next line {2}'.format(
                    LnColor.redH,
                    _function_name),
                end=end )
            print (self.normal_text.encode(string_encode, 'ignore'), end=end )


        if autoreset:
            print(self._default, end='')

        if toFile:
            self.toFile(end=end)

        self.colored_text = ''
        self.normal_text  = ''



    def _prepareText(self, color='', text='', tab=0, string_encode='latin-1'):
        _function_name = sys._getframe().f_code.co_name
        thisTAB = ' '*tab
        if not isinstance(text, str):
            text = str(text)
        # ----------------------------------------------
        # - intercettazione del tipo text per fare un
        # - print più intelligente.
        # ----------------------------------------------
            # - convertiamo bytes in string
        if isinstance(text, bytes):
            text = text.decode('utf-8')

            # - convertiamo list in string (con il tab in ogni riga)
        if isinstance(text, list):
            myMsg = []
            for line in text:
                myMsg.append('{}{}'.format(thisTAB, line))
            text = '\n'.join(myMsg)
            thisTAB = ''

            # - aggiungiamo il tab in ogni riga
        elif '\n' in text:
            myMsg = []
            for line in text.split('\n'):
                myMsg.append('{}{}'.format(thisTAB, line))
            text = '\n'.join(myMsg)
            thisTAB = ''

        self.colored_text = '{0}{1}{2}'.format(thisTAB, color, text)
        self.normal_text  = '{0}{1}'.format(thisTAB, text)

# ============================================================================
# FILE: output.py
# License: MIT license
# ============================================================================
import re
import shlex
import subprocess

from .base import Base


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'output'
        # why doesn't this seem to be working?
        self.default_action = 'yank'

    def define_syntax(self):
        cmd = self.context['args'][0]
        if re.fullmatch(r'hi(ghlight)?(!)?', cmd):
            self.define_syntax_for_highlight(cmd)
        if re.match(r'^let($| )', cmd):
            self.define_syntax_for_let()

    def gather_candidates(self, context):
        args = context['args']

        if not args:
            return []

        first = args[0]
        output = []
        if first[0] != '!':
            cmdline = ' '.join(args)
            output = self.vim.call('execute', cmdline).splitlines()[1:]
        else:
            cmdline = ' '.join([first[1:]] + args[1:])
            try:
                output = [x.decode(context['encoding']) for x in
                          subprocess.check_output(shlex.split(cmdline))
                          .splitlines()]
            except subprocess.CalledProcessError:
                return []
        return [{'word': x} for x in output]

    def define_syntax_for_highlight(self, cmd):
        self.vim.command('syntax include syntax/vim.vim')
        hi_list = self.vim.call('execute', cmd).splitlines()[1:]
        for hi in (h.split()[0] for h in hi_list):
            syn_hi_name = (
                'syntax match vimHiGroup' +
                ' /' + hi + r'\>/' +
                ' nextgroup=' + hi +
                ' skipwhite'
            )
            syn_hi_xxx = (
                'syntax match ' + hi +
                ' /xxx/' +
                ' contained' +
                ' nextgroup=@vimHighlightCluster' +
                ' skipwhite'
            )
            self.vim.command(syn_hi_name)
            self.vim.command(syn_hi_xxx)

    def define_syntax_for_let(self):
        self.vim.command('syntax include syntax/vim.vim')
        syn_var_name = (
            r'syntax match vimVar /^\s*\S\+/' +
            ' nextgroup=deniteSource_outputLetAll'
            # ' skipwhite'
        )

        # FIXME:
        # is there a more elegant way to do an include like this?
        #
        # why doesn't it work for me to just have vimNumber and vimOperGroup
        # in nextgroup of syn_var_name above?
        #
        # also why don't I get string highlighting when I use vimString instead
        # of vimOperGroup?
        #
        # can't get vimFuncName highlighting working
        syn_include = (
            r'syntax match deniteSource_outputLetAll /.*/' +
            # ' contains=@vimNumber,@vimOperGroup' +
            ' contains=@vimStringGroup' +
            # ' contains=@vimNumber,@vimStringGroup' +
            ' contained'
        )

        syn_hash_num = (
            r'syntax match vimNumber /#-\?\d\+\ze$/'
        )
        syn_dot_num = (
            r'syntax match vimNumber /\d\+\(\.\d\+\)\+\ze$/'
        )
        self.vim.command(syn_var_name)
        self.vim.command(syn_include)
        self.vim.command(syn_hash_num)
        self.vim.command(syn_dot_num)

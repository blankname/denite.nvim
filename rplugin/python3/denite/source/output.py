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
        # need string, list, dictionary
        # self.vim.command('set syntax=vim')
        # why doesn't quickfixsigns_class_rel exhibit the prob?
        self.vim.command('syntax include syntax/vim.vim')
        syn_var_name = (
            # 'syntax match vimVar /^\h[a-zA-Z0-9#_]*\>/' +
            # r'syntax match vimVar /^\s*\S\+\ze /' +
            r'syntax match vimVar /^\s*\S\+/' +
            # ' nextgroup=allThings' +
            ' nextgroup=@vimNumber' +
            # ' nextgroup=@vimNumber,@vimOperGroup' +
            # r'syntax match allThings /.*/' +
            # ' contains=@vimOperGroup' +
            # ' nextgroup=@vimOperGroup' +
            # ' nextgroup=@vimOperParen' +
            # ' nextgroup=@vimFilter' +
            # ' nextgroup=@vimOperGroup,@vimFilter' +
            # ' nextgroup=@vimSep,@vimString' +
            # ' nextgroup=@vimFuncBodyList,@vimFuncList' +
            ' oneline' +
            ' skipwhite'
        )

        # is there a more elegant way to do an include like this?
        # why isn't vimFuncName working
        # syn_include = (
        #     r'syntax match allThings /.*/' +
        #     # ' contains=@vimNumber,@vimParenSep' +
        #     # ' contains=@vimNumber,@vimSep' +
        #     ' contains=@vimNumber,@vimOperGroup' +
        #     ' oneline' +
        #     ' contained'
        # )

        # syn_cluster = (
        #     'syntax cluster vimOperGroup contains=@vimOperGroup'
        # )
        # self.vim.command(syn_cluster)

        # to avoid trying to match over multiple lines/results
        # syn_oper_group_new_end = (
        #     # r'syntax region vimOperGroup oneline start=/{/ end=/}/ end=/$/'
        #     r'syntax region vimOperGroup oneline start=/{/ end=/}/ end=/$/'
        # )
        # syn_string_new_end_single = (
        #     r'syntax region vimString start=/\'/ end=/\'/ end=/$/'
        # )
        # syn_string_new_end_double = (
        #     r'syntax region vimString start=/"/ end=/"/ end=/$/'
        # )

        syn_hash_num = (
            # r'syntax match vimNumber /#-\?\d\+\(\s|$\)/'
            r'syntax match vimNumber /#-\?\d\+\ze$/'
            # r'syntax match vimNumber /#-\?\d\+\ze([^\S]|$)*/'
        )
        syn_dot_num = (
            # r'syntax match vimNumber /\d\+\.(\.|\d*)\+/'
            # r'syntax match vimNumber /\d\+\.(\d\+(\.)\?)*/'
            # r'syntax match vimNumber /\d\+\(\.\d\+\)\+\(\s|$\)/'
            r'syntax match vimNumber /\d\+\(\.\d\+\)\+\ze$/'
        )
        self.vim.command(syn_var_name)
        # self.vim.command(syn_include)
        self.vim.command(syn_hash_num)
        self.vim.command(syn_dot_num)

        # self.vim.command(syn_oper_group_new_end)
        # self.vim.command(syn_string_new_end_single)
        # self.vim.command(syn_string_new_end_double)
        # let_hi = (
        #     # 'syntax cluster deniteSource_outputLetCluster' +
        #     'syntax cluster vimString' +
        #     ' contains=@vimStringGroup'
        # )
        # self.vim.command(let_hi)
        # self.vim.command('echom "here"')


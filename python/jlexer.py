#!/usr/bin/env python3

from pygments.lexer import RegexLexer, include, bygroups
from pygments.token import *

Verb = Operator
Adverb = Keyword.Type
Conjunction = Keyword
Punct = Punctuation
Noun = Name
RankConst = Name.Tag
Control = Name.Label
DefHeader = Name.Function
ExplicitDef = Name.Decorator
DirectDef = Name.Decorator
Def = Name.Decorator
Copula = Generic

bdef_noun_multi = r"(\(+\s*)*(noun|0)\)*\s+(\(*define\)*|(def|:)\s*\(*0\)*)"
qdef_verb_inline = r"(adverb|conjunction|verb|monad|dyad|[1-4]|13)\s+(def|:)\s*'"
bdef_verb_multi  = r"(\(+\s*)*(adverb|conjunction|verb|monad|dyad|[1-4]|13)\)*\s+(\(*define\)*|(def|:)\s*\(*0\)*)\s*"
bqdef_verb_inline = r"(adverb|conjunction|verb|monad|dyad|[1-4]|13)\s+(def|:)\s*\('"

class CustomLexer(RegexLexer):
    name = 'J'
    aliases = ['J']
    filenames = ['*.ijs']

    tokens = {
        'root': [
            (r"#!.*", Comment.Hashbang), 
            include('expdef'),
            include('literal'),
            include('syntax'),
            include('string'),
            (r"\{\{", DirectDef, 'ddef'), 
        ],
        'literal': [
            (r"\b[A-Za-z][A-Za-z0-9_]*\b", Literal),
        ],
        'syntax': [
            (r"=[.:']", Copula), 
            include('unpack'),
            include('comment'),
            include('conjunction'),
            include('verb'),
            include('adverb'),
            include('noun'),
            include('rank'),
            include('number'),
            include('punct'),
            include('whitespace'),
        ],
        'punct': [
            (r"\(|(?<=.)\)", Punctuation), 
        ],
        'whitespace' : [
            (r"\s+", Whitespace),
        ],
        'unpack': [
            (r"(')(`?)([\w\s]*)(')(\s*=[.:])",
                bygroups(Def, Conjunction, Literal, Def, Copula),
            )
        ],
        'unpack_in_def': [
            (r"'(?=(`?\s*[a-zA-Z][a-zA-Z0-9_]*)+\s*'\s*=[.:])",
                Name.Function, 'unpack_assign_in_def'),
        ],
        'unpack_assign_in_def': [
            (r"'", Name.Function),
            (r"`", Conjunction), 
            include('args'),
            include('literal'),
            include('whitespace'),
            (r"=[.:']", Copula, '#pop'), 
        ],
        'string': [ (r"'[^']*'", String) ],
        'nstring': [ (r"''.*?''", String) ],
        'expdef': [
            include('bdef_noun'),
            include('qdef_verb'),
            include('bdef_verb'),
            include('bqdef_verb'),
        ],
        'bdef_noun' : [
            (bdef_noun_multi, ExplicitDef,
                'bdef_noun_multi'),
            (r"^\)", ExplicitDef), 
        ],
        'bdef_noun_multi': [
            (r"(?s).*?(?=^\))", String, '#pop'),
        ],
        'bdef_verb': [
            (bdef_verb_multi, ExplicitDef,
                'bdef_verb_multi'),
        ],
        'bdef_verb_multi': [
            include('control'),
            include('expdef'),
            include('syntax'),
            include('args'),
            include('string'),
            include('literal'),
            (r"^\)", ExplicitDef, '#pop'),
        ],
        'qdef_verb': [
            (qdef_verb_inline, ExplicitDef,
                'qdef_verb_inline'),
        ],
        'qdef_verb_inline': [
            include('control'),
            include('syntax'),
            include('args'),
            include('nstring'),
            include('literal'),
            (r"'", ExplicitDef, '#pop'),
        ],
        'bqdef_verb': [
            (bqdef_verb_inline, ExplicitDef,
                'bqdef_verb_inline'),
        ],
        'bqdef_verb_inline': [
            include('control'),
            include('syntax'),
            include('args'),
            include('nstring'),
            include('literal'),
            (r"'\)", ExplicitDef, '#pop'),
            (r"'", ExplicitDef),
        ],
        'comment': [
            (r"NB\.(?![.:]).*", Comment), 
        ],
        'args': [
            (r"[mnxy](?!\w)", Noun),
            (r"[uv](?!\w)", Verb),
        ],
        'ddef': [
            (r"\)[mdvac*]", DefHeader),
            (r"\)n", DefHeader, 'directstring'),
            (r"\}\}", DirectDef, '#pop'), 
            include('unpack_in_def'),
            include('control'),
            include('args'),
            include('syntax'),
            include('string'),
            include('literal'),
        ],
        'directstring': [
            (r"\}\}", DirectDef), 
            (r"(?s).*?(?=\}\})", String, '#pop'),
        ],
        'verb': [
            (r"__?:", Verb),
            (r";:", Verb),
            (r"\{::", Verb),
            (r"[;=!]", Verb),
            (r"[-+*<>#$%|,][.:]?", Verb),
            (r"(?<!\{)\{(?!\{)[.:]?", Verb), # single '{'
            (r"\}[.:]", Verb),
            (r"~[.:]", Verb),
            (r"\^\.?", Verb),
            (r"[/\\]:", Verb),
            (r"\[:?", Verb),
            (r"\](?!:)", Verb),
            (r"\?\.?", Verb),
            (r"\bp\.\.", Verb),
            (r"\b[AcCeEiIjLoprT]\.", Verb),
            (r"\b[ipqsuxZ]:", Verb),
            (r"_?[0-9]:", Verb),
            (r'"[.:]', Verb),
        ],
        'adverb': [
            (r"(?<!\})\}(?!\})", Adverb), # single '}'
            (r"~", Adverb),
            (r"\/(\.\.?)?", Adverb),
            (r"\b[bfM]\.", Adverb),
            (r"\]:", Adverb),
            (r"\\\.?", Adverb),
        ],
        'conjunction': [
            (r"\s+\.", Conjunction),
            (r"^\s*:", Conjunction),
            (r"\.$", Conjunction),
            (r"\.[.:]", Conjunction),
            (r";\.", Conjunction),
            (r"\^:", Conjunction),
            (r":[.:]?", Conjunction),
            (r"![.:]{1}", Conjunction),
            (r"`[:]?", Conjunction), 
            (r"[@&][.:]?", Conjunction),
            (r"&\.:", Conjunction),
            (r"\b[dtmDH]\.", Conjunction),
            (r"\b[DLS]\:", Conjunction),
            (r"\bF[.:][.:]?", Conjunction),
            (r"[\[\]]\.", Conjunction),
        ],
        'rank': [
            (r'(")((\s*_?([0-9]+x?)?){1,3})',
                bygroups(Conjunction, RankConst),
            ), 
        ],
        'noun': [
            (r"a[.:]", Noun),
            (r"_\.", Noun),
            (r"_(?![:_\d])", Noun),
        ],
        'number': [
            (r"_?\.?\d+(?!:)[_\.0-9Ea-z]*", Number),
            (r"_(?=_)", Number),
        ],
        'control' : [
            (r"\b(assert|break|case|catch|catchd)\.", Control),
            (r"\b(catcht|continue|do|else|elseif)\.", Control),
            (r"\b(end|fcase|for|if|return|select)\.", Control),
            (r"\b(throw|trap|try|while|whilst)\.", Control),
            (r"\b(for_|goto_|label_)([^.]+)(\.)",
                bygroups(Control, Literal, Control),
            ),
        ],
    }

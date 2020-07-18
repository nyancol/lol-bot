import re, collections
from typing import Union, Any, List, Optional, Tuple
from operator import add, sub, mul, truediv
from enum import Enum
from functools import partial
import json

from pcsd_cog.events import EventData

Token = collections.namedtuple("Token", ["name", "value"])
RuleMatch = collections.namedtuple("RuleMatch", ["name", "matched"])

token_map = {
             "+": "ADD",
             "-": "ADD",
             "*": "MUL",
             "/": "MUL",
             "(": "LPAR",
             ")": "RPAR",
             "in": "ADD"
            }

rule_map = {
    "add" : ["mul ADD add", "mul"],
    "mul" : ["atom MUL mul", "atom"],
    "atom": ["NUM", "ALPHA", "LPAR add RPAR", "neg"],
    "neg" : ["ADD atom"],
}

fix_assoc_rules = "add", "mul"

bin_calc_map = { 
                "*": mul,
                "/": truediv,
                "+": add,
                "-": sub,
               }


def getattr_rec(obj: Any, attr_list: List[str]) -> Union[List[Any], Any]:
    if not attr_list:
        return obj


    a_list = attr_list[:]
    attr: str = a_list.pop(0)

    try:
        getattr(obj, attr)
    except TypeError:
        return attr_list

    if isinstance(getattr(obj, attr), list):
        obj_elements = getattr(obj, attr)
        return [getattr_rec(e, a_list) for e in obj_elements]
    return getattr_rec(getattr(obj, attr), a_list)


class AggOperand(Enum):
    MAX = (max,)
    MIN = (min,)
    SUM = (sum,)
    COUNT = (len,)

    def __init__(self, f):
        self._value_ = f

    def __call__(self, l, **args):
        return self.value(l, **args)


def calc_binary(x, event: EventData):
    while len(x) > 1:
        x[:3] = [ bin_calc_map[x[1]](x[0], x[2]) ]
    return x[0]


def extract_event_data(attr: str, event: EventData) -> Any:
    regex_agg = r"(SUM|MAX|MIN|COUNT|sum|max|min|count)\((.+)\)(.*)"
    agg_op: Optional[AggOperand] = None
    remaining: Optional[List[str]] = None

    match = re.match(regex_agg, attr)
    if match:
        agg_op = AggOperand[match.group(1).upper()]
        attr = match.group(2)
        if match.group(3):
            remaining = [e for e in match.group(3).split('.') if e]

    value: str = attr
    try:
        value = json.loads(value)
    except json.decoder.JSONDecodeError:
        pass

    try:
        attr = attr.split('.')
        if agg_op is None:
            try:
                value = getattr_rec(event, attr)
            except AttributeError:
                value = json.loads(attr)
        elif agg_op and remaining is None:
            try:
                value = agg_op(getattr_rec(event, attr))
            except AttributeError as exc:
                value = agg_op(json.loads(attr[0]))
        elif agg_op and remaining:
            list_values = getattr(event, attr[0])
            agg_attr = agg_op(list_values, key=lambda v: getattr_rec(v, attr[1:][:]))
            value = getattr_rec(agg_attr, remaining)
    except (AttributeError, TypeError):
        pass
    return value


calc_map = {
    "ALPHA": extract_event_data,
    "NUM"  : lambda f, _: float(f),
    "atom" : lambda x, _: x[len(x)!=1],
    "neg"  : lambda op,num: (num,-num)[op=="-"],
    "mul"  : calc_binary,
    "add"  : calc_binary,
    "contains"  : calc_binary,
}

def match(rule_name: str, tokens: List[Token]) -> Tuple[Optional[RuleMatch], Optional[List[Token]]]:
    if tokens and rule_name == tokens[0].name:      # Match a token?
        return tokens[0], tokens[1:]
    for expansion in rule_map.get(rule_name, ()):   # Match a rule?
        remaining_tokens = tokens
        matched_subrules = []
        for subrule in expansion.split():
            matched, remaining_tokens = match(subrule, remaining_tokens)
            if not matched:
                break   # no such luck. next expansion!
            matched_subrules.append(matched)
        else:
            return RuleMatch(rule_name, matched_subrules), remaining_tokens
    return None, None   # match not found


def _recurse_tree(tree: RuleMatch, func) -> Union[List[Any], Any]:
    if tree.name in rule_map:
        return [func(tree=tm) for tm in tree.matched]
    else:
        return tree[1]


def flatten_right_associativity(tree: RuleMatch) -> RuleMatch:
    new = _recurse_tree(tree, flatten_right_associativity)
    if tree.name in fix_assoc_rules and len(new)==3 and new[2].name==tree.name:
        new[-1:] = new[-1].matched
    return RuleMatch(tree.name, new)


def evaluate(event: EventData, tree: RuleMatch):
    p_evaluate = partial(evaluate, event=event)
    solutions = _recurse_tree(tree, p_evaluate)
    return calc_map.get(tree.name, lambda x,_: x)(solutions, event)



class Expression:
    def __init__(self, expr):
        self.expr = expr

    def resolve(self, event: EventData) -> Union[bool, str, float]:
        # split_expr = re.findall(rf"[\d.]+|[\w.]+|[\+\-\*/()]", self.expr)
        exp_agg = r"\w+\([\. ,\w\d\]\[]+\)\.?[\.\w]*"
        digits = r"[\d\.]+"
        alphanum = r"[\w][\w\.\* ]*"
        operators = r"[\+\-\*/()]"
        lists = r'\[[ \w\d",]+\]'

        split_expr = re.findall(lists + "|" + exp_agg + "|" + digits + "|" + alphanum + "|" + operators, self.expr)
        # print(self.expr, split_expr)
        tokens = []
        for x in split_expr:
            if x.isdigit() \
                    or (len(x.split('.')) == 2 \
                            and x.split('.')[0].isdigit() \
                            and x.split('.')[1].isdigit()):
                tokens.append(Token("NUM", x))
            elif x in token_map:
                tokens.append(Token(token_map[x], x))
            else:
                tokens.append(Token("ALPHA", x))

        tree = match('add', tokens)[0]
        tree = flatten_right_associativity(tree)
        return evaluate(event, tree)

    def __repr__(self):
        return self.expr

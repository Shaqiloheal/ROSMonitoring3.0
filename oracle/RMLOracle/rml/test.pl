:- module('spec', [trace_expression/2, match/2]).
:- use_module(monitor('deep_subdict')).
match(_event, overheat_temperature) :- deep_subdict(_{'data':Val,'topic':"temperature"}, _event), >(Val, 50.0).
match(_event, good_temperature) :- deep_subdict(_{'data':Val,'topic':"temperature"}, _event), ','((Val>=0.0), (Val=<50.0)).
match(_, any).
trace_expression('Main', Main) :- Main=star((((good_temperature:eps)\/(negative_temperature:eps))\/(overheat_temperature:eps))).

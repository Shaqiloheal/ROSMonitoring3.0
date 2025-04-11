:- module('spec', [trace_expression/2, match/2]).
:- use_module(monitor('deep_subdict')).
match(_event, low_battery) :- deep_subdict(_{'data':Val,'topic':"battery_percentage"}, _event), ','((Val>=0.0), (Val<20.0)).
match(_event, normal_battery) :- deep_subdict(_{'data':Val,'topic':"battery_percentage"}, _event), ','((Val>=20.0), (Val=<100.0)).
match(_event, invalid_battery) :- deep_subdict(_{'data':Val,'topic':"battery_percentage"}, _event), ;((Val<0.0), (Val>100.0)).
match(_, any).
trace_expression('Main', Main) :- Main=star((normal_battery:eps)).

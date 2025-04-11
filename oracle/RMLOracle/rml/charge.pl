:- module('spec', [trace_expression/2, match/2]).
:- use_module(monitor('deep_subdict')).
match(_event, charging_feedback) :- deep_subdict(_{'current_percentage':Val}, _event), ','((Val>=0.0), (Val=<100.0)).
match(_event, charging_result) :- deep_subdict(_{'success':'true'}, _event).
match(_, any).
trace_expression('Main', Main) :- Main=(plus((charging_feedback:eps))*optional((charging_result:eps))).

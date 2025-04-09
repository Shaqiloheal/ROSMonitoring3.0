#!/usr/bin/env python

# begin imports
import json
import yaml
import websocket
import sys
import rclpy
import rosidl_runtime_py
from rclpy.node import Node
from threading import *
from rosmonitoring_interfaces.msg import MonitorError
from std_msgs.msg import *
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from custom_action_interfaces.action.Fibonacci import *
# done import

class ROSMonitor_monitor_action(Node):


	def callbackfibonacci__goal(self,data):
		self.get_logger().info("monitor has observed "+ str(data))
		dict= rosidl_runtime_py.message_to_ordereddict(data)
		dict['topic']='fibonacci/_goal'
		dict['time']=float(self.get_clock().now().to_msg().sec)
		self.ws_lock.acquire()
		self.logging(dict)
		self.ws_lock.release()
		self.get_logger().info("event successfully logged")

	def callbackfibonacci__feedback(self,data):
		self.get_logger().info("monitor has observed "+ str(data))
		dict= rosidl_runtime_py.message_to_ordereddict(data)
		dict['topic']='fibonacci/_feedback'
		dict['time']=float(self.get_clock().now().to_msg().sec)
		self.ws_lock.acquire()
		self.logging(dict)
		self.ws_lock.release()
		self.get_logger().info("event successfully logged")

	def callbackfibonacci__result(self,data):
		self.get_logger().info("monitor has observed "+ str(data))
		dict= rosidl_runtime_py.message_to_ordereddict(data)
		dict['topic']='fibonacci/_result'
		dict['time']=float(self.get_clock().now().to_msg().sec)
		self.ws_lock.acquire()
		self.logging(dict)
		self.ws_lock.release()
		self.get_logger().info("event successfully logged")

	def __init__(self,monitor_name,log,actions):
		self.monitor_publishers={}
		self.config_publishers={}
		self.config_subscribers={}
		self.config_client_services={}
		self.config_server_services={}
		self.config_client_actions={}
		self.config_server_actions={}
		self.services_info={}
		self.actions_info={}
		self.dict_msgs={}
		self.ws_lock=Lock()
		self.name=monitor_name
		self.actions=actions
		self.logfn=log
		self.topics_info={}
		super().__init__(self.name)
		# creating the verdict and error publishers for the monitor
		self.monitor_publishers['error']=self.create_publisher(topic=self.name+'/monitor_error',msg_type=MonitorError,qos_profile=1000)

		self.monitor_publishers['verdict']=self.create_publisher(topic=self.name+'/monitor_verdict',msg_type=String,qos_profile=1000)

		# done creating monitor publishers

		self.publish_topics=False
		self.topics_info['fibonacci/_goal']={'package': 'custom_action_interfaces.action.Fibonacci', 'type': 'Goal'}
		self.topics_info['fibonacci/_feedback']={'package': 'custom_action_interfaces.action.Fibonacci', 'type': 'Feedback'}
		self.topics_info['fibonacci/_result']={'package': 'custom_action_interfaces.action.Fibonacci', 'type': 'Result'}
		self.config_subscribers['fibonacci/_goal']=self.create_subscription(topic='fibonacci/_goal',msg_type=Goal,callback=self.callbackfibonacci__goal,qos_profile=1000)

		self.config_subscribers['fibonacci/_feedback']=self.create_subscription(topic='fibonacci/_feedback',msg_type=Feedback,callback=self.callbackfibonacci__feedback,qos_profile=1000)

		self.config_subscribers['fibonacci/_result']=self.create_subscription(topic='fibonacci/_result',msg_type=Result,callback=self.callbackfibonacci__result,qos_profile=1000)

		self.get_logger().info('Monitor' + self.name + ' started and ready' )
		self.get_logger().info('Logging at' + self.logfn )



	def logging(self,json_dict):
		try:
			with open(self.logfn,'a+') as log_file:
				log_file.write(json.dumps(json_dict)+'\n')
			self.get_logger().info('Event logged')
		except:
			self.get_logger().info('Unable to log the event')

def main(args=None):
	rclpy.init(args=args)
	log = './log_action.txt'
	actions = {}
	actions['fibonacci/_goal']=('log',0)
	actions['fibonacci/_feedback']=('log',0)
	actions['fibonacci/_result']=('log',0)
	monitor = ROSMonitor_monitor_action('monitor_action', log, actions)
	rclpy.spin(monitor)
	monitor.ws.close()
	monitor.destroy_node()
	rclpy.shutdown()

if __name__ == '__main__':
	main()

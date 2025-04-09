#!/usr/bin/env python

# begin imports
import json
import rosidl_runtime_py
import rclpy
from rclpy.node import Node
from threading import Lock
from rosmonitoring_interfaces.msg import MonitorError
from std_msgs.msg import String
from custom_action_interfaces.action import Fibonacci
from custom_action_interfaces.action._fibonacci import Fibonacci_FeedbackMessage
from custom_action_interfaces.action._fibonacci import Fibonacci_GetResult_Response

# done import

class ROSMonitor_monitor_fibonacci(Node):

    def __init__(self, monitor_name, log, actions):
        super().__init__(monitor_name)

        self.monitor_publishers = {}
        self.ws_lock = Lock()
        self.name = monitor_name
        self.actions = actions
        self.logfn = log

        # Monitor publishers
        self.monitor_publishers['error'] = self.create_publisher(
            MonitorError, self.name + '/monitor_error', 10)

        self.monitor_publishers['verdict'] = self.create_publisher(
            String, self.name + '/monitor_verdict', 10)

        # Subscribe to the feedback topic
        self.feedback_subscriber = self.create_subscription(
            Fibonacci_FeedbackMessage,
            '/fibonacci/_action/feedback',
            self.feedback_callback,
            10
        )

        # Subscribe to the result topic
        self.result_subscriber = self.create_subscription(
            Fibonacci_GetResult_Response,
            '/fibonacci/_action/result/response',
            self.result_callback,
            10
        )

        self.get_logger().info('Monitor ' + self.name + ' started and ready')
        self.get_logger().info('Logging at ' + self.logfn)

    def feedback_callback(self, feedback_msg):
        """Callback when feedback is observed."""
        self.get_logger().info("Monitor observed feedback: " + str(feedback_msg))

        feedback = feedback_msg.feedback

        data_dict = {}
        data_dict['feedback'] = rosidl_runtime_py.message_to_ordereddict(feedback)
        data_dict['action'] = '/fibonacci'
        data_dict['time'] = float(self.get_clock().now().seconds_nanoseconds()[0])

        self.ws_lock.acquire()
        self.logging(data_dict)
        self.ws_lock.release()

        self.get_logger().info("Feedback event successfully logged")

    def result_callback(self, result_msg):
        """Callback when result is observed."""
        self.get_logger().info("Monitor observed result: " + str(result_msg))

        result = result_msg.result

        data_dict = {}
        data_dict['result'] = rosidl_runtime_py.message_to_ordereddict(result)
        data_dict['action'] = '/fibonacci'
        data_dict['time'] = float(self.get_clock().now().seconds_nanoseconds()[0])

        self.ws_lock.acquire()
        self.logging(data_dict)
        self.ws_lock.release()

        self.get_logger().info("Result event successfully logged")

    def logging(self, json_dict):
        """Simple file logger."""
        try:
            with open(self.logfn, 'a+') as log_file:
                log_file.write(json.dumps(json_dict) + '\n')
            self.get_logger().info('Event logged')
        except Exception as e:
            self.get_logger().info('Unable to log the event: ' + str(e))

def main(args=None):
    rclpy.init(args=args)
    log = './log_fibonacci.txt'
    actions = {}
    actions['/fibonacci'] = ('log', 0)
    monitor = ROSMonitor_monitor_fibonacci('monitor_fibonacci', log, actions)
    rclpy.spin(monitor)
    monitor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

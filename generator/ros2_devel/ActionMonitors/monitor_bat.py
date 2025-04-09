#!/usr/bin/env python

# ========================================
# Import required modules
# ========================================

import json  # For serializing log data to JSON
import rosidl_runtime_py  # For handling ROS2 message serialization
import rclpy  # ROS2 Python client library
from rclpy.node import Node  # Base class for all ROS2 nodes
from threading import Lock  # To ensure thread-safe file writing

# Import custom ROS2 messages
from rosmonitoring_interfaces.msg import MonitorError  # Custom MonitorError message
from std_msgs.msg import String  # Standard ROS2 String message

# ========================================
# IMPORT YOUR ACTION HERE (Battery)
# ========================================
from custom_action_interfaces.action import Battery  # The main Battery Action
from custom_action_interfaces.action._battery import Battery_FeedbackMessage  # Feedback message
from custom_action_interfaces.action._battery import Battery_GetResult_Response  # Result response

# ========================================
# Define the Generic ROS2 Monitor Node specialized for Battery
# ========================================

class ROSMonitor_monitor_bat(Node):
    """
    ROS2 Node to monitor feedback and result topics of the Battery Action server.
    Logs feedback and results to a JSON file for offline analysis.
    """

    def __init__(self, monitor_name, log, actions, action_namespace):
        """
        Initialize the monitor node, create publishers and subscribers.

        Args:
            monitor_name (str): Name of the monitor node.
            log (str): File path to save event logs.
            actions (dict): Actions to monitor (for compatibility).
            action_namespace (str): Namespace of the Battery Action (e.g., '/battery')
        """
        super().__init__(monitor_name)

        self.name = monitor_name
        self.logfn = log
        self.actions = actions
        self.action_namespace = action_namespace

        self.monitor_publishers = {}
        self.ws_lock = Lock()

        # Create publishers for monitor events
        self.monitor_publishers['error'] = self.create_publisher(
            MonitorError, self.name + '/monitor_error', 10
        )
        self.monitor_publishers['verdict'] = self.create_publisher(
            String, self.name + '/monitor_verdict', 10
        )

        # Subscribe to the Action's feedback topic
        self.feedback_subscriber = self.create_subscription(
            Battery_FeedbackMessage,
            f"{self.action_namespace}/_action/feedback",
            self.feedback_callback,
            10
        )

        # Subscribe to the Action's result topic
        self.result_subscriber = self.create_subscription(
            Battery_GetResult_Response,
            f"{self.action_namespace}/_action/result/response",
            self.result_callback,
            10
        )

        # Log successful initialization
        self.get_logger().info(f"Monitor '{self.name}' started and ready")
        self.get_logger().info(f"Logging events to {self.logfn}")

    def feedback_callback(self, feedback_msg):
        """
        Callback for processing incoming feedback messages.

        Args:
            feedback_msg (Battery_FeedbackMessage): Received feedback.
        """
        self.get_logger().info(f"Monitor observed feedback: {str(feedback_msg)}")

        feedback = feedback_msg.feedback

        data_dict = {
            'feedback': rosidl_runtime_py.message_to_ordereddict(feedback),
            'action': self.action_namespace,
            'time': float(self.get_clock().now().seconds_nanoseconds()[0])
        }

        with self.ws_lock:
            self.logging(data_dict)

        self.get_logger().info("Feedback event successfully logged")

    def result_callback(self, result_msg):
        """
        Callback for processing incoming result messages.

        Args:
            result_msg (Battery_GetResult_Response): Received result.
        """
        self.get_logger().info(f"Monitor observed result: {str(result_msg)}")

        result = result_msg.result

        data_dict = {
            'result': rosidl_runtime_py.message_to_ordereddict(result),
            'action': self.action_namespace,
            'time': float(self.get_clock().now().seconds_nanoseconds()[0])
        }

        with self.ws_lock:
            self.logging(data_dict)

        self.get_logger().info("Result event successfully logged")

    def logging(self, json_dict):
        """
        Writes the provided event dictionary to the log file in JSON format.

        Args:
            json_dict (dict): Dictionary containing the event data to log.
        """
        try:
            with open(self.logfn, 'a+') as log_file:
                log_file.write(json.dumps(json_dict) + '\n')
            self.get_logger().info('Event successfully written to log')
        except Exception as e:
            self.get_logger().info(f'Unable to log the event: {str(e)}')

# ========================================
# Main function
# ========================================

def main(args=None):
    """
    Main entry point for running the Battery Action monitor node.
    """
    rclpy.init(args=args)

    # ===========================
    # Modify these variables if needed
    # ===========================
    log = './log_battery.txt'  # Where to save the Battery action events
    actions = {}
    actions['/battery'] = ('log', 0)
    action_namespace = '/battery'  # Must match the Battery action server's name exactly

    # Instantiate and spin the monitor
    monitor = ROSMonitor_monitor_bat('monitor_bat', log, actions, action_namespace)

    rclpy.spin(monitor)

    monitor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
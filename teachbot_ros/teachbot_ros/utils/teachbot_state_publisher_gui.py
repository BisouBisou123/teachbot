#!/usr/bin/env python3
"""
TeachbotState Publisher GUI
Simple GUI for publishing TeachbotState messages with potentiometer and button controls.
"""

import tkinter as tk
import threading
import math
import rclpy
from rclpy.node import Node
from teachbot_interfaces.msg import TeachbotState
from std_msgs.msg import Header
from sensor_msgs.msg import JointState


class TeachbotStatePublisherGUI(Node):
    def __init__(self):
        super().__init__('teachbot_state_publisher_gui')

        self.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint',
        ]
        self.joint_angles_deg = [0.0] * len(self.joint_names)
        
        # Create publisher
        self.publisher_ = self.create_publisher(TeachbotState, 'teachbot/state', 10)

        # Subscribe to robot joint states
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/teachbot/joint_states',
            self.on_joint_state,
            10,
        )
        
        # Create timer for publishing at 10 Hz
        self.timer = self.create_timer(0.1, self.publish_state)
        
        # State variables
        self.pot_percent = 0
        self.btn1_state = False
        self.btn2_state = False
        
        # Create GUI
        self.create_gui()
        
        self.get_logger().info('TeachbotState Publisher GUI started')
        self.get_logger().info('Subscribing to /teachbot/joint_states for joint angle forwarding')

    def on_joint_state(self, msg: JointState):
        """Update joint angles from /teachbot/joint_states (radians -> degrees)."""
        name_to_position = {
            name.split('/')[-1]: pos for name, pos in zip(msg.name, msg.position)
        }

        for index, joint_name in enumerate(self.joint_names):
            if joint_name in name_to_position:
                self.joint_angles_deg[index] = round(math.degrees(name_to_position[joint_name]), 1)
    
    def create_gui(self):
        """Create the GUI interface"""
        self.root = tk.Tk()
        self.root.title("TeachbotState Publisher")
        self.root.geometry("400x400")
        self.root.configure(bg='#2b2b2b')
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Title
        title = tk.Label(main_frame, text="TeachbotState Publisher", 
                        font=('Arial', 16, 'bold'), bg='#2b2b2b', fg='white')
        title.pack(pady=(0, 20))
        
        # Potentiometer section
        pot_frame = tk.Frame(main_frame, bg='#2b2b2b')
        pot_frame.pack(fill='x', pady=10)
        
        pot_label = tk.Label(pot_frame, text="Potentiometer (%)", 
                            font=('Arial', 12), bg='#2b2b2b', fg='white')
        pot_label.pack()
        
        self.pot_value_label = tk.Label(pot_frame, text="0%", 
                                       font=('Arial', 14, 'bold'), bg='#2b2b2b', fg='#4CAF50')
        self.pot_value_label.pack()
        
        self.pot_slider = tk.Scale(pot_frame, from_=0, to=100, orient='horizontal',
                                  command=self.on_slider_change, length=300,
                                  bg='#3b3b3b', fg='white', highlightthickness=0,
                                  troughcolor='#555555', activebackground='#4CAF50')
        self.pot_slider.pack(pady=10)
        
        # Buttons section
        buttons_frame = tk.Frame(main_frame, bg='#2b2b2b')
        buttons_frame.pack(pady=20)
        
        # Button 1 (Green toggle)
        self.btn1 = tk.Button(buttons_frame, text="BTN 1\nOFF", 
                             command=self.toggle_btn1,
                             width=12, height=3, font=('Arial', 12, 'bold'),
                             bg='#2d5016', fg='white', activebackground='#3d6026')
        self.btn1.grid(row=0, column=0, padx=10)
        
        # Button 2 (Red toggle)
        self.btn2 = tk.Button(buttons_frame, text="BTN 2\nOFF", 
                             command=self.toggle_btn2,
                             width=12, height=3, font=('Arial', 12, 'bold'),
                             bg='#5d1616', fg='white', activebackground='#7d2626')
        self.btn2.grid(row=0, column=1, padx=10)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Publishing at 10 Hz", 
                                    font=('Arial', 10), bg='#2b2b2b', fg='#888888')
        self.status_label.pack(side='bottom', pady=10)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_slider_change(self, value):
        """Handle slider value change"""
        self.pot_percent = int(value)
        self.pot_value_label.config(text=f"{self.pot_percent}%")
    
    def toggle_btn1(self):
        """Toggle button 1 state"""
        self.btn1_state = not self.btn1_state
        if self.btn1_state:
            self.btn1.config(text="BTN 1\nON", bg='#4CAF50', activebackground='#66BB6A')
        else:
            self.btn1.config(text="BTN 1\nOFF", bg='#2d5016', activebackground='#3d6026')
    
    def toggle_btn2(self):
        """Toggle button 2 state"""
        self.btn2_state = not self.btn2_state
        if self.btn2_state:
            self.btn2.config(text="BTN 2\nON", bg='#F44336', activebackground='#EF5350')
        else:
            self.btn2.config(text="BTN 2\nOFF", bg='#5d1616', activebackground='#7d2626')
    
    def publish_state(self):
        """Publish TeachbotState message"""
        msg = TeachbotState()
        
        # Set header
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'teachbot_gui'
        
        # Calculate pot_raw from pot_percent (0-100 -> 0-1023)
        msg.pistol.pot_raw = int((self.pot_percent / 100.0) * 1023)
        msg.pistol.pot_percent = self.pot_percent
        
        # Set button states
        msg.pistol.btn1 = self.btn1_state
        msg.pistol.btn2 = self.btn2_state
        
        # Joint angles from /teachbot/joint_states
        msg.joint_angles_deg = self.joint_angles_deg.copy()

        # Initialize other fields with default values
        msg.tcp_x = 0.0
        msg.tcp_y = 0.0
        msg.tcp_z = 0.0
        msg.tcp_rx = 0.0
        msg.tcp_ry = 0.0
        msg.tcp_rz = 0.0
        msg.encoder_errors = [False] * 6
        msg.encoder_warnings = [False] * 6
        msg.encoder_frequencies = [0.0] * 6
        msg.robot_model = 'gui_publisher'
        
        # Publish
        self.publisher_.publish(msg)
    
    def on_closing(self):
        """Handle window closing"""
        self.get_logger().info('Shutting down GUI...')
        self.root.quit()
        rclpy.shutdown()
    
    def spin_ros(self):
        """Spin ROS2 in a separate thread"""
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
    
    def run(self):
        """Run the GUI main loop"""
        # Start ROS2 spinning in a separate thread
        ros_thread = threading.Thread(target=self.spin_ros, daemon=True)
        ros_thread.start()
        
        # Run tkinter main loop
        self.root.mainloop()


def main(args=None):
    rclpy.init(args=args)
    
    try:
        gui_node = TeachbotStatePublisherGUI()
        gui_node.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='genetic_tune',  # Reemplaza con el nombre de tu paquete
            executable='gen_tuner',  # Reemplaza con el nombre de tu nodo
            output='screen'         # Puedes elegir 'screen', 'log' o 'both'
        )
    ])

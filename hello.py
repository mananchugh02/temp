import stem
from stem.control import Controller
import requests

def communicate_with_server():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        
        # Create a new circuit
        circuit_id = controller.new_circuit(
            path=['GuardNode', 'MiddleNode', 'ExitNode'],
            await_build=True
        )
        
        # Get the exit node's fingerprint
        with controller.get_network_map() as network_map:
            exit_fingerprint = network_map.find_router('ExitNode').digest()
        
        # Configure the circuit
        controller.set_conf('__LeaveStreamsUnattached', '1')
        controller.set_conf('MaxCircuitDirtiness', '10')
        
        # Attach a stream to the circuit
        controller.attach_stream(0, circuit_id)
        
        # Make a request to the server through the Tor network
        response = requests.get('http://your_server_ip/your_file', proxies={'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'})
        
        # Print the response
        print(response.text)

if __name__ == "__main__":
    communicate_with_server()

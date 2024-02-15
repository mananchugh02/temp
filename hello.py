import stem
from stem.control import Controller
import requests

with Controller.from_port(port=9051) as controller:
    controller.authenticate()
    circuit_id = controller.new_circuit( 
        path=['guard123lol', 'middle123lol', 'exit123lol'], 
        await_build=True
    )
    with controller.get_network_map() as network_map:
        exit_fingerprint = network_map.find_router('ExitNode').digest()
    controller.set_conf('__LeaveStreamsUnattached', '1')
    controller.set_conf('MaxCircuitDirtiness', '10')
    controller.attach_stream(0, circuit_id)
    response = requests.get('http://10.0.2.15/temp.html', proxies={'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'})
    print(response.text)

import stem.control
import requests

def download_file_through_tor(relay_paths, file_url):
    with stem.control.Controller.from_port() as controller:
        controller.authenticate()

        for path in relay_paths:
            try:
                # Create a circuit through the specified relay path
                circuit_id = controller.new_circuit(path, await_build=True)

                # Attach streams to the circuit
                def attach_stream(stream):
                    if stream.status == 'NEW':
                        controller.attach_stream(stream.id, circuit_id)

                controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

                try:
                    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us

                    # Make a request to download the file through Tor
                    response = requests.get(file_url, proxies={'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'})

                    # Print the downloaded content or save it to a file
                    print(response.text)

                finally:
                    # Remove the event listener and reset configuration
                    controller.remove_event_listener(attach_stream)
                    controller.reset_conf('__LeaveStreamsUnattached')

            except Exception as exc:
                print('Error downloading file through path:', path)
                print(exc)

# Specify the relay paths (fingerprint list) and the URL of the file to download
relay_paths = [
    ['guard123lol', 'middle123lol', 'exit123lol'],  # Example path, replace with actual relay fingerprints
]

# URL of the file to download (Apache server IP + file path)
file_url = 'http://10.0.2.15/temp.html'

# Call the function to download the file through Tor using the specified relay paths
download_file_through_tor(relay_paths, file_url)

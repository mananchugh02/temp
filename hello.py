import io
import pycurl

import stem.process

from stem.util import term

SOCKS_PORT = 7000

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
def query(url):
    """
    Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
    """

    output = io.BytesIO()

    query = pycurl.Curl()
    query.setopt(pycurl.URL, url)
    query.setopt(pycurl.PROXY, 'localhost')
    query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
    query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
    query.setopt(pycurl.WRITEFUNCTION, output.write)

    try:
        query.perform()
        return output.getvalue()
    except pycurl.error as exc:
        return "Unable to reach %s (%s)" % (url, exc)


# Start an instance of Tor configured to only exit through Russia. This prints
# Tor's bootstrap information as it starts. Note that this likely will not
# work if you have another Tor instance running.

def print_bootstrap_lines(line):
    if "Bootstrapped " in line:
        print(term.format(line, term.Color.BLUE))


print(term.format("Starting Tor:\n", term.Attr.BOLD))

tor_process = stem.process.launch_tor_with_config(
    config={
        'SocksPort': str(SOCKS_PORT),
        'ExitNodes': '{ru}',
    },
    init_msg_handler=print_bootstrap_lines,
)

print(term.format("\nChecking our endpoint:\n", term.Attr.BOLD))
print(term.format(query("https://www.atagar.com/echo.php"), term.Color.BLUE))

# Now that Tor is running, we can use the Tor network to download the file

relay_paths = [
    ['guard123lol', 'middle123lol', 'exit123lol'],  # Example path, replace with actual relay fingerprints
]

file_url = 'https://drive.google.com/uc?export=download&id=1ORyVVnnc7UfpiLW5_OED2ZAGpsB6oVYP'  # Replace with the actual URL of the file to download

# Download the file through Tor using the specified relay paths
download_file_through_tor(relay_paths, file_url)

tor_process.kill()  # stops tor

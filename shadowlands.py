import npyscreen, sys, os, hashlib, argparse, struct, time, locale, qrcode_terminal, threading
from pyfiglet import Figlet
from ledgerblue.comm import getDongle
from ledgerblue.commException import CommException
from web3.exceptions import UnhandledRequest
from web3.auto import w3

# Get a connection

block = ""
nodeVersion = ""
syncing = {}
localNode = True
ethAddress = ""

connected = w3.isConnected()
if connected and w3.version.node.startswith('Parity'):
    enode = w3.parity.enode
elif connected and w3.version.node.startswith('Geth'):
    enode = w3.admin.nodeInfo['enode']
else:
    localNode = False
    print("Could not find parity or geth locally")
    del sys.modules['web3.auto']
    os.environ['INFURA_API_KEY'] = '3404d141198b45b191c7af24311cd9ea'
    from web3.auto.infura import w3

if not w3.isConnected():
    print("Sorry chummer, couldn't connect to an Ethereum node.")
    exit()

def heartbeat():
    global nodeVersion, block, blocksBehind, syncing
    while True:
#       assert w3.isConnected()
       nodeVersion = w3.version.node
       block = str(w3.eth.blockNumber)
       syncing = w3.eth.syncing
       if syncing:
           blocksBehind = syncing['highestBlock'] - syncing['currentBlock']
            
       if localNode:
           time.sleep(.5)
       else:
           time.sleep(10)
    return

t = threading.Thread(target=heartbeat)
t.start()


# Check the file for tampering
def file_checksum():
    script_path = os.path.abspath(__file__)
    shahash = hashlib.sha256()
    with open(script_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            shahash.update(chunk)
    return shahash.hexdigest()


def ledgerEthAddress():
    dongle = getDongle(False)
    result = dongle.exchange(bytearray.fromhex('e002000011048000002c8000003c8000000000000000'))
    offset = 1 + result[0]
    address = result[offset + 1 : offset + 1 + result[offset]]
    return address

def header():
    print('Connected to ' + nodeVersion)
    if not syncing:
        print('[block ' + block + ']')
    else:
        print('[syncing:  ' + str(blocksBehind) + ' blocks to ' + str(syncing['highestBlock']) + ']')
 
## Loading Screen
#print('[ '+ file_checksum() + ' ]')
def loadingScreen():
    os.system("clear")
    header()       
    print(Figlet(font='slant').renderText('Shadowlands') )
    print('public terminal \t\t' + 'v0.01' )
    print( '\n\n\n\n\n' )
    print('Welcome, chummer.  Insert your credstick to log in.')
    return

boxDictionary = {
        '\\' : b'\xe2\x95\x9a',
        '-'  : b'\xe2\x95\x90',
        '/'  : b'\xe2\x95\x9d',
        '|'  : b'\xe2\x95\x91',
        '+'  : b'\xe2\x95\x94',
        '%'  : b'\xe2\x95\x97',
        }

def boxDecode(x):
    return (''.join(boxDictionary.get(i, i.encode('utf-8')).decode('utf-8') for i in x))

def ethBalance(address):
    bal = w3.eth.getBalance(address)
    return str(w3.fromWei(bal, 'ether'))

def mainMenu():
    os.system("clear")
    header()
    print('\n')
    print('  ' + ethAddress)
    print('\n')
    print(boxDecode('  +- Account Balances -------------%'))
    print(boxDecode('  |                                    '))
    print(boxDecode('  |  Ξth: ' + ethBalance(ethAddress) + ''))
    print(boxDecode('  |  Dai: ' + ethBalance(ethAddress) + ''))
    print(boxDecode('  |                                    '))
    print(boxDecode('  \\--------------------------------/'))
    print('\n')
    print(boxDecode('  +- Things to do -------------------------------------%'))
    print(boxDecode('  |                                    '))
    print(boxDecode('  |  (S)end ether and tokens '))
    print(boxDecode('  |  (V)iew your transaction history '))
    print(boxDecode('  |  (T)rade Ether for Dai '))
    print(boxDecode('  |  (O)pen a CDP loan [borrow dai against your ether]'))
    print(boxDecode('  |  (R)egister your ENS name '))
    print(boxDecode('  |  (C)hat on the whispernet '))
    print(boxDecode('  |  (P)ublic forums '))
    print(boxDecode('  |  (B)rowse the take-out menu '))
    print(boxDecode('  |                                    '))
    print(boxDecode('  \\----------------------------------------------------/'))
 
    return

def blastOff():
    timeout = 0.11
    for x in range(70):
      time.sleep(timeout)
      sys.stdout.write(".")
      sys.stdout.flush()
      timeout = timeout * 0.93
    return


loadingScreen()

while True:
    try: 
        #address = ledgerPublicAddress()
        address = ledgerEthAddress()
        ethAddress = '0x' + address.decode('utf-8') 
        sys.stdout.write("\033[F")
      #  print("\nSuccess.  Logging in with public address " + ethAddress)
        blastOff()

        break
    except(CommException, IOError):
        time.sleep(0.25)
        loadingScreen()

while True:
    mainMenu()
    time.sleep(0.25)


input()




# o = qrcode_terminal.qr_terminal_str('0xC579e6BF41789dEeF2E0AaCa8fBb8b0F0c762898', 1)

"""
def parse_bip32_path(path="44'/60'/0'/0"):
    if len(path) == 0:
        return ""
    result = ""
    elements = path.split('/')
    for pathElement in elements:
        element = pathElement.split('\'')
        if len(element) == 1:
            result = result + struct.pack(">I", int(element[0]))
        else:
            result = result + struct.pack(">I", 0x80000000 | int(element[0]))
            print("element[0]: " + element[0])
            print( "pathcode: " + (struct.pack(">I", 0x80000000 | int(element[0]))).encode('hex'))

    return result

def ledgerPublicAddress():
    donglePath = parse_bip32_path()
#apdu = "e0020100".decode('hex') + chr(len(donglePath) + 1) + chr(len(donglePath) / 4) + donglePath
    apdu = "e0020000".decode('hex') + chr(len(donglePath) + 1) + chr(len(donglePath) / 4) + donglePath

    dongle = getDongle(True)
    print 'donglepath: ' + donglePath.encode('hex')
    print "Apdu: " + bytes(apdu).encode('hex')
    #print "Apdu bytes: " + bytes(apdu)
    result = dongle.exchange(bytes(apdu))
    offset = 1 + result[0]
    address = result[offset + 1 : offset + 1 + result[offset]]

 #   print "Public key " + str(result[1 : 1 + result[0]]).encode('hex')
 #   print "Address 0x" + str(address)
    return address
"""



import yaml

WAIT_DEFAULT = 5
TIMEOUT_DEFAULT = 3
INVALID_DEFAULT = 3
REPEAT_DTMF = '#'
OPERATOR_DTMF = '*'

def timeout(num=TIMEOUT_DEFAULT):
    config.write('exten => t,1,NoOp()\n')
    config.write('exten => t,n,GoToIf($[${TIMEOUT_COUNT} > ' + 
                        str(num-2) + ']?HANGUP,s,1)\n')
    config.write('exten => t,n,Set(TIMEOUT_COUNT=$[${TIMEOUT_COUNT} + 1])\n')
    config.write('exten => t,n,Wait(.5)\n')
    config.write('exten => t,n,GoTo(s,restart)\n\n')

def invalid(num=INVALID_DEFAULT):
    config.write('exten => i,1,NoOp()\n')
    config.write('exten => i,n,GoToIf($[${INVALID_COUNT} > ' +
                        str(num-2) + ']?HANGUP,s,1)\n')
    config.write('exten => i,n,Set(INVALID_COUNT=$[${INVALID_COUNT} + 1])\n')
    config.write('exten => i,n,Wait(.5)\n')
    config.write('exten => i,n,GoTo(s,restart)\n\n')

def repeat(dtmf=REPEAT_DTMF):
    config.write('exten => ' + dtmf + ',1,NoOp()\n')
    config.write('exten => ' + dtmf + ',n,Wait(.5)\n')
    config.write('exten => ' + dtmf + ',n,GoTo(s,restart)\n\n')

def operator(dtmf=OPERATOR_DTMF):
    config.write('exten => ' + dtmf + ',1,NoOp()\n')
    config.write('exten => ' + dtmf + ',n,Dial(SIP/0)\n\n')

def line(doc, extension):

    pre = 'exten => ' + extension 

    config.write(pre + ',1,NoOp()\n')

    if extension == 's':
        config.write(pre + ',n,Set(TIMEOUT_COUNT=0)\n')
        config.write(pre + ',n,Set(INVALID_COUNT=0)\n')

        if 'init' in doc:
            config.write(pre + ',n,Set(' + doc['init'] + '=0)\n')

        config.write(pre + ',n(restart),NoOp()\n')

    if 'say' in doc:
        if isinstance(doc['say'], list):
            for i in doc['say']:
                if 'extensions' in doc:
                    config.write(pre + ',n,Background(' + i + ')\n')
                else:
                    config.write(pre + ',n,Playback(' + i + ')\n') 
        else:
            if 'extensions' in doc:
                config.write(pre + ',n,Background(' + doc['say'] + ')\n')
            else:
                config.write(pre + ',n,Playback(' + doc['say'] + ')\n') 
 
    if 'code' in doc:
        if isinstance(doc['code'], list):
            for i in doc['code']:
                config.write(pre + ',n,' + i + '\n')
        else:
           config.write(pre + ',n,' + doc['code'] + '\n')
        
    if 'jump' in doc:
        config.write(pre + ',n,Goto(' + doc['jump'] + ',s,1)\n')

    if 'dial' in doc:
        config.write(pre + ',n,Dial(' + doc['dial'] + ')\n')


    if 'extensions' in doc:
        (config.write(pre + ',n,WaitExten(' + ( str(doc['wait']) if 'wait' in doc 
                    else str(WAIT_DEFAULT) ) + ')\n'))

    if 'hangup' in doc:
        config.write(pre + ',n,Hangup()\n')
    
    config.write('\n')
   

f = open('yaml.yaml') 
docs = yaml.load_all(f)

config = open('dialplan.conf', 'w')

config.write('[HANGUP]\n')
config.write('exten => s,1,NoOp()\n')
config.write('exten => s,n,Hangup()\n\n')

config.write('[TIMEOUT]\n')
timeout()

config.write('[INVALID]\n')
invalid()

config.write('[REPEAT]\n')
repeat()

config.write('[OPERATOR]\n')
operator()

for doc in docs:

    config.write('[' + doc['name'] + ']\n')

    (timeout(doc['timeout']) if 'timeout' in doc 
                else config.write('include => TIMEOUT\n\n'))
    (invalid(doc['invalid']) if 'invalid' in doc 
                else config.write('include => INVALID\n\n'))
    (repeat(str(doc['repeat'])) if 'repeat' in doc 
                else config.write('include => REPEAT\n\n'))
    (operator(str(doc['operator'])) if 'operator' in doc 
                else config.write('include => OPERATOR\n\n'))

    config.write('\n')

    line(doc, 's') 

    if 'extensions' in doc:
        for e in doc['extensions']:
            line(e, str(e['dtmf']))
            
f.close()
config.close()

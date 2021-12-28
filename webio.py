import subprocess
from pywebio.output import put_buttons, put_processbar, put_text, put_button, clear, set_processbar, style, use_scope, put_table
from pywebio.input import PASSWORD, input, input_group

bot_on = False

def toggle():
    global cmd
    global bot_on

    if not bot_on:
        cmd = subprocess.Popen(['python3', 'gdbrowserbot.py'])
    else:
        cmd.kill()
    bot_on = not bot_on

def launch():
    toggle()
    status_text()

def status_text():
    global bot_on

    clear('status')

    if not bot_on:
        with use_scope('status'):
            put_text('Bot is off')

    elif bot_on:
        with use_scope('status'):
            style(put_text('Bot is on'), 'color:green')

def main():
    clear()
    put_button('Toggle bot', onclick=launch)
    status_text()

def login():
    #print("Connection: " + pywebio.session.info.user_ip)
    info = input_group("Admin login",[
        input('Username: ', name='username'),
        input('Password: ', name='password', type=PASSWORD)
    ])
    if info['username'] == 'roflboy' and info['password'] == 'jokezavr1234':
        main()
    else:
        clear()
        put_text('Incorrect username or password')

if __name__ == "__main__":  
    main()
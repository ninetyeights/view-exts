import os
import json
import subprocess
from sys import platform
import customtkinter
from PIL import Image

Path = os.path.join

customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk(fg_color='#fff')
app.geometry("920x850")
app.title('查看浏览器插件')

scroll_frame = customtkinter.CTkScrollableFrame(app, width=920, height=850, fg_color="#fff")
scroll_frame.pack()


def get_browsers():
    browsers = {
        'darwin': {
            'chrome': {
                'app_path': '/Applications/Google Chrome.app',
                'app_name': 'Google Chrome',
                'data_dir': os.path.expanduser('~') + '/Library/Application Support/Google/Chrome/'
            },
            'edge': {
                'app_path': '/Applications/Microsoft Edge.app',
                'app_name': 'Microsoft Edge',
                'data_dir': os.path.expanduser('~') + '/Library/Application Support/Microsoft Edge/'
            },
            'brave': {
                'app_path': '/Applications/Brave Browser.app',
                'app_name': 'Brave',
                'data_dir': os.path.expanduser('~') + '/Library/Application Support/BraveSoftware/Brave-Browser/'
            }
        },
        'win32': {
            'chrome': {
                'app_path': [
                    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                ],
                'app_name': 'Google Chrome',
                'data_dir': os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Google', 'Chrome',
                                         'User Data')
            },
            'edge': {
                'app_path': [
                    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
                    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                ],
                'app_name': 'Microsoft Edge',
                'data_dir': os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Microsoft', 'Edge',
                                         'User Data')
            },
            'brave': {
                'app_path': [
                    r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
                    r'C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe',
                ],
                'app_name': 'Brave',
                'data_dir': os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'BraveSoftware',
                                         'Brave-Browser',
                                         'User Data')
            }
        }
    }
    if platform == 'darwin':
        current = browsers[platform]
    elif platform == 'win32':
        current = browsers[platform]
    else:
        current = None
        exit(0)

    for key in current.keys():
        if platform == 'win32':
            has_path = False
            for path in current[key]['app_path']:
                if os.path.exists(path):
                    has_path = True
                    break
            if has_path is True:
                yield current[key]
        else:
            if os.path.exists(current[key]['app_path']):
                yield current[key]


def get_state(_path):
    with open(_path, 'r', encoding='utf-8') as fp:
        local_state = json.loads(fp.read())
        return local_state['profile']['info_cache']


def get_ext(_path):
    with open(_path, 'r', encoding='utf-8') as fp:
        return json.loads(fp.read())


browsers = list(get_browsers())

count = 0
data = list()
for browser in browsers:
    hasPath = os.path.exists(browser['data_dir'])
    if not hasPath:
        continue
    local_state_path = Path(browser['data_dir'], 'Local State')
    info_cache = get_state(local_state_path)
    for (i, key) in enumerate(info_cache.keys()):
        extensions_path = Path(browser['data_dir'], key, 'Extensions')
        # print(extensions_path)
        if not os.path.exists(extensions_path):
            continue
        print(extensions_path)
        for root, dirs, files in os.walk(extensions_path, topdown=False):
            for name in files:

                if name == 'manifest.json':
                    ext_info = get_ext(os.path.join(root, 'manifest.json'))
                    icons = None
                    try:
                        icons = ext_info['browser_action']['default_icon']
                    except:
                        pass

                    try:
                        icons = ext_info['icons']
                    except:
                        pass

                    if icons is not None:
                        count += 1
                        icon_path = list(icons.items())[0]
                        icon = Path(root, os.path.normpath(icon_path[1]))
                        id = os.path.normpath(root).split(os.sep)[-2]
                        obj = {
                            "icon": icon,
                            "profile": key,
                            "browser": browser['app_name'],
                            "id": id
                        }
                        data.append(obj)


def chunk(list, size):
    for i in range(0, len(list), size):
        yield list[i:i + size]


def click(b, p, id):
    # print(b, p, id)
    if platform == 'darwin':
        subprocess.Popen('')
    else:
        name = ''
        # print(b)
        if b == 'Google Chrome':
            name = 'chrome.exe'
        elif b == 'Microsoft Edge':
            name = 'msedge.exe'
        else:
            name = 'brave.exe'
        # print(f'start {name} --profile-directory="{p}" "chrome://extensions/?id={id}"')
        subprocess.Popen(f'start {name} --profile-directory="{p}"', shell=True)


chunk_data = list(chunk(data, 5))
for row in chunk_data:
    frame = customtkinter.CTkFrame(master=scroll_frame, fg_color="#fff")
    for (i, item) in enumerate(row):
        image = customtkinter.CTkImage(Image.open(item['icon']), size=(48, 48))
        image_button = customtkinter.CTkButton(master=frame,
                                               fg_color="#f1f5f9",
                                               hover_color="#bae6fd",
                                               text_color="#000",
                                               text=item['browser'] + '\n' + item['profile'],
                                               image=image, command=lambda b=item['browser'], p=item['profile'],
                                                                           id=item['id']: click(b, p, id))
        image_button.grid(row=0, column=i, padx=8, pady=8)
    frame.grid()

app.mainloop()

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
app.geometry("930x850")
app.title('查看浏览器插件')

scroll_frame = customtkinter.CTkScrollableFrame(app, width=920, height=850, fg_color="#fff")
scroll_frame.pack()

_label = customtkinter.CTkLabel(scroll_frame, text='正在加载数据中...').grid(row=0, column=0)

count = 0
exclude = ['ghbmnnjooekpmoecnnnilnnbdlolhkhi', 'nmmhkkegccagdldgiimedpiccmgmieda']
data = list()
data_obj = {
    "Google Chrome": {},
    "Microsoft Edge": {},
    "Brave": {},
}


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


def update_date(_path, key, browser, _id=None):
    global data_obj
    for root, dirs, files in os.walk(_path, topdown=False):
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
                    global count
                    count += 1
                    icon_path = list(icons.items())[0]
                    path = icon_path[1][1:] if icon_path[1].startswith('/') else icon_path[1]
                    icon = Path(root, os.path.normpath(path))
                    id = _id or os.path.normpath(root).split(os.sep)[-2]
                    # profile = dict()
                    # profile[browser['app_name'].replace(' ', '_')] = [key]
                    obj = {
                        "icon": icon,
                        "profile": [key],
                        "browser": browser['app_name'],
                        "id": id,
                        "name": ext_info['name']
                    }
                    data.append(obj)
                    if id not in data_obj[browser['app_name']]:
                        data_obj[browser['app_name']][id] = obj
                    else:
                        data_obj[browser['app_name']][id]['profile'].append(key)


browsers = list(get_browsers())

for browser in browsers:
    hasPath = os.path.exists(browser['data_dir'])
    if not hasPath:
        continue
    local_state_path = Path(browser['data_dir'], 'Local State')
    info_cache = get_state(local_state_path)
    for (i, key) in enumerate(info_cache.keys()):
        try:
            update_date(Path(browser['data_dir'], key, 'Extensions'), key, browser)
        except:
            pass

        try:
            with open(Path(browser['data_dir'], key, 'Preferences'), 'r', encoding='utf-8') as fp:
                obj = json.loads(fp.read())['extensions']['settings']
                for id, value in obj.items():
                    try:
                        _path = value['path']
                    except:
                        pass
                    if not os.path.isabs(_path):
                        _path = Path(browser['data_dir'], key, 'Extensions', _path)
                    if os.path.exists(_path) and id not in exclude:
                        update_date(_path, key, browser, id)
        except:
            pass



def chunk(list, size):
    for i in range(0, len(list), size):
        yield list[i:i + size]


def se_click(b, p):
    if b == 'Google Chrome':
        name = 'chrome.exe'
    elif b == 'Microsoft Edge':
        name = 'msedge.exe'
    else:
        name = 'brave.exe'
    subprocess.Popen(f'start {name} --profile-directory="{p}"', shell=True)


def click(item):
    # print(b, p, id)
    if platform == 'darwin':
        subprocess.Popen('')
    else:
        second = customtkinter.CTkToplevel(app)
        second.geometry('300x600')
        second.title(item['name'])
        second.deiconify()

        image = customtkinter.CTkImage(Image.open(item['icon']), size=(48, 48))
        btn = customtkinter.CTkButton(master=second,
                                      width=280,
                                      fg_color="#f1f5f9",
                                      hover_color="#bae6fd",
                                      text_color="#000",
                                      image=image,
                                      text=item['name'])
        btn.grid(row=0, column=0)

        ss_frame = customtkinter.CTkScrollableFrame(second, width=280, height=600, fg_color='#fff')
        ss_frame.grid(row=1, column=0)
        for profile in item['profile']:
            button = customtkinter.CTkButton(master=ss_frame,
                                             width=300,
                                             height=32,
                                             fg_color="#f1f5f9",
                                             hover_color="#bae6fd",
                                             text_color="#000",
                                             text=profile,
                                             command=lambda b=item['browser'], p=profile: se_click(b, p)
                                             )
            button.grid(pady=4)


for row_index, info in enumerate(data_obj.values()):
    chunk_data = list(chunk(list(info.values()), 5))
    top_frame = customtkinter.CTkFrame(master=scroll_frame, fg_color="#fff", width=920, height=64)
    for key, row in enumerate(chunk_data):
        frame = customtkinter.CTkFrame(master=top_frame, fg_color="#fff", width=920, height=64)
        for (i, item) in enumerate(row):
            image = customtkinter.CTkImage(Image.open(item['icon']), size=(48, 48))
            image_button = customtkinter.CTkButton(master=frame,
                                                   width=180,
                                                   height=48,
                                                   fg_color="#f1f5f9",
                                                   hover_color="#bae6fd",
                                                   text_color="#000",
                                                   text=item['name'] + '\n' + item['browser'],
                                                   image=image,
                                                   command=lambda item=item: click(item),
                                                   anchor='w'
                                                   )
            image_button.place(x=i * 180, y=0, relx=0, rely=0)
        frame.grid(row=row_index+key, column=0)
    top_frame.grid(row=row_index)

app.mainloop()

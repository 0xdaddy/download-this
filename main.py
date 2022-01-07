import requests,json,uuid,time,typing,colorama,os,urllib.request

class APIs:
    login_attempt_count: int = 0
    csrftoken: str = None
    headers: dict = None
    session_id: str = None
    cookies:dict = None

    def __init__(self,username,password) -> None:
        self.username: str = username
        self.password: str = password
        self.phone_id: str = str(uuid.uuid4())
        self.adid:     str = str(uuid.uuid4())
        self.guid:     str = str(uuid.uuid4())
        self.uuid:     str = str(uuid.uuid4())
        self.device_id = f'android-{uuid.uuid4()}'

    def make_headers(self) -> dict:
        headers:dict = {}
        headers['User-Agent'] = 'Instagram 155.0.0.27.107 Android (20/5.6; 320dpi; 1080x1260; HUAWEI; VIVO-Z9QXB; zqjk; mm3693; en_US)'
        headers['Connection'] = 'close'
        security = requests.get('https://i.instagram.com/api/v1/si/fetch_headers/',headers=headers, verify=True)
        headers['csrftoken'] = security.cookies.get_dict()['csrftoken']
        self.csrftoken = security.cookies.get_dict()['csrftoken']
        headers['x-mid'] = security.cookies.get_dict()['mid']
        headers['Accept'] = '*/*'
        headers['X-Ig-Connection-Type'] = 'WIFI'
        headers['X-Ig-Capabilities'] = '3brTvx0='
        headers['X-Fb-Http-Engine'] = 'Liger'
        headers['X-Fb-Client-Ip'] = 'True'
        headers['X-Fb-Server-Cluster'] = 'True'
        headers['Connection'] = 'close'
        return headers
    
    def login(self) -> bool:
        
        data: dict = {
        };self.headers = self.make_headers()
        data['jazoest'] = '22602'
        data['username'] = self.username
        data['enc_password'] = '#PWD_INSTAGRAM:0:{0}:{1}'.format(int(time.time()),self.password)
        data['adid'] = self.adid
        data['guid'] = self.guid
        data['device_id'] = self.device_id
        data['google_tokens'] = '[]'
        data['login_attempt_count'] = f'{self.login_attempt_count}';self.login_attempt_count += 1
        data['_csrftoken'] = self.csrftoken
        payload = {}
        payload['signed_body'] = f'SIGNATURE.{json.dumps(data)}'
        login_res = requests.post('https://i.instagram.com/api/v1/accounts/login/', headers=self.headers, data=payload)
        if login_res.text.__contains__('logged_in_user'):
            self.cookies = login_res.cookies.get_dict()
            self.session_id = self.cookies['sessionid']
            return True
        else:
            return False

    def get_dm(self) -> requests.Response:return requests.get('https://i.instagram.com/api/v1/direct_v2/inbox/?limit=1',headers=self.headers, cookies=self.cookies)

    def SendDM(self,user_id, msg) -> None:
        urlApi = 'https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/'
        data = {
        'text': msg,
        '_uuid': self.uuid,
        '_csrftoken': self.csrftoken,
        'recipient_users': f'[[{user_id}]]',
        '_uid': self.uuid,
        'action': 'send_item',
        'client_context': int(time.time()) * 1000}
        requests.post(urlApi, data=data , headers=self.headers, cookies=self.cookies )
    

    def SendImage(self, image_file,thread_id) -> bool:
        upload_id = int(time.time()) * 1000
    
        content_headers =  self.headers.copy()
        x_entity_name = f'{upload_id}_0_{int(time.time())}'
        content_headers['Content-Type'] = 'application/octet-stream'
        content_headers['X-Instagram-Rupload-Params'] =json.dumps({'retry_context': json.dumps({ 'num_step_auto_retry': '0', 'num_reupload': '0', 'num_step_manual_retry': '0' }),'media_type': '1','upload_id': f'{upload_id}','xsharing_user_ids': json.dumps([]),'image_compression': json.dumps({ 'lib_name': 'moz', 'lib_version': '3.1.m', 'quality': '80' }),})
        content_headers['X-Entity-Name'] = x_entity_name
        content_headers['X-Entity-Type'] = 'image/jpeg'
        content_headers['Offset'] = '0'
        content_headers['X_fb_photo_waterfall_id'] = str(uuid.uuid4())
        content_headers['Content-Length'] = str(os.path.getsize(image_file))
        content_headers['X-Entity-Length'] = str(os.path.getsize(image_file))
        image_res = requests.post(f'https://i.instagram.com/rupload_igphoto/{x_entity_name}',data=open(image_file,'rb'),headers=content_headers, cookies=self.cookies)
        upload_id = image_res.json()['upload_id']
       
        client_context = int(time.time()) * 1000


        config_image = requests.post('https://i.instagram.com/api/v1/direct_v2/threads/broadcast/configure_photo/',data={
        'action': 'send_item',
        'is_shh_mode': '0',
        'thread_ids': '[{}]'.format(','.join([thread_id])),
        'send_attribution': 'inbox',
        'client_context': f'{client_context}',
        'device_id': f'{self.device_id}',
        'mutation_token': f'{client_context}',
        '_uuid': f'{self.uuid}',
        'allow_full_aspect_ratio': 'true',
        'upload_id': f'{upload_id}',
        'offline_threading_id': f'{client_context}'
            },headers=self.headers,cookies=self.cookies)

        try:
            if config_image.json()['status_code'] == '200':
                return True
            else:
                return False
        except Exception:
            return False


    def SendVideo(self, video_file,thread_id,upload_media_height,upload_media_width,upload_media_duration_ms) -> bool:
        upload_id = int(time.time()) * 1000
    
        content_headers =  self.headers.copy()
        x_entity_name = f'{upload_id}_0_{int(time.time())}'
        content_headers['Content-Type'] = 'application/octet-stream'
        content_headers['X-Instagram-Rupload-Params'] =json.dumps({
            'upload_media_height':f'{upload_media_height}',
            'direct_v2':'1',
            'rotate':'0',
            'xsharing_user_ids':json.dumps([]),
            'upload_media_width':f'{upload_media_width}',
            'hflip':'false',
            'upload_media_duration_ms':f'{upload_media_duration_ms}',
            'upload_id':f'{upload_id}' ,
            'retry_context':json.dumps({
                'num_step_auto_retry':'0',
                'num_reupload':'0',
                'num_step_manual_retry':'0'
                }),
            'media_type':'2'})
        content_headers['X-Entity-Name'] = x_entity_name
        content_headers['X-Entity-Type'] = 'video/mp4'
        content_headers['Segment-Start-Offset'] = '0'
        content_headers['Offset'] = '0'
        content_headers['Segment-Type'] = '3'
        content_headers['X_fb_video_waterfall_id'] = str(uuid.uuid4())
        content_headers['Content-Length'] = str(os.path.getsize(video_file))
        content_headers['X-Entity-Length'] = str(os.path.getsize(video_file))
        vid_res = requests.post(f'https://i.instagram.com/rupload_igvideo/{x_entity_name}/',headers=content_headers,data=open(video_file,'rb'),cookies=self.cookies)
        if vid_res.status_code == 200:

            client_context = int(time.time()) * 1000
            config_vid = requests.post('https://i.instagram.com/api/v1/direct_v2/threads/broadcast/configure_video/',headers=self.headers,cookies=self.cookies,data={
        'action':'send_item',
        'is_shh_mode': '0',
        'thread_ids': '[{}]'.format(','.join([thread_id])),
        'send_attribution': 'direct_thread',
        'client_context': f'{client_context}',
        'video_result':'',
        'device_id': f'{self.device_id}',
        'mutation_token': f'{client_context}',
        '_uuid': f'{self.uuid}',
        'upload_id':f'{upload_id}',
        'offline_threading_id': f'{client_context}'
        })
            try:
                if config_vid.json()['status_code'] == '200':
                    return True
                else:
                    return False
            except Exception:
                return False

    def get_media_info(self,id)-> requests.Response:return requests.get(f'https://i.instagram.com/api/v1/media/{id}/info/',headers=self.headers,cookies=self.cookies)

    def get_id(self,username)->str: 
        api_get_user_dtl = requests.get(f'https://i.instagram.com/api/v1/feed/user/{username}/username/' , headers=self.headers, cookies=self.cookies)
        if 'Not authorized to view user' not in api_get_user_dtl.text and 'pk' in api_get_user_dtl.text:
            return str(api_get_user_dtl.json()['user']['pk'])
        else:
            web_get_user_dtl = requests.get(f'https://www.instagram.com/{username}/?__a=1' , headers=self.headers, cookies=self.cookies)
            if 'id' in web_get_user_dtl.text and '<!DOCTYPE html>' not in web_get_user_dtl.text:
                return str(web_get_user_dtl.json()['graphql']['user']['id'])
            else:
                print('['+colorama.Fore.RED+'!!'+colorama.Fore.RESET+'] Unable to get id of provider user') #exit 
                exit(1);
  
    def get_media_info(self,id)-> requests.Response: return requests.get(f'https://i.instagram.com/api/v1/media/{id}/info/',headers=self.headers,cookies=self.cookies)

def clear() -> None: os.system('cls') if os.name == 'nt' else os.system('clear')

def banner() -> None:
    clear()
    print(colorama.Fore.RED+'''
▓█████▄ ▄▄▄█████▓ ██░ ██  ██▓  ██████ 
▒██▀ ██▌▓  ██▒ ▓▒▓██░ ██▒▓██▒▒██    ▒ 
░██   █▌▒ ▓██░ ▒░▒██▀▀██░▒██▒░ ▓██▄   
░▓█▄   ▌░ ▓██▓ ░ ░▓█ ░██ ░██░  ▒   ██▒
░▒████▓   ▒██▒ ░ ░▓█▒░██▓░██░▒██████▒▒
 ▒▒▓  ▒   ▒ ░░    ▒ ░░▒░▒░▓  ▒ ▒▓▒ ▒ ░
 ░ ▒  ▒     ░     ▒ ░▒░ ░ ▒ ░░ ░▒  ░ ░
 ░ ░  ░   ░       ░  ░░ ░ ▒ ░░  ░  ░  
   ░              ░  ░  ░ ░        ░  
 ░                            [ - Download this - ]
'''+colorama.Fore.RESET)

def main() -> typing.Any:
    try:
        file_path = 'database/data.json'
        os.system('title DEVIL HERE ^| insta @0xdevil')
        banner()
        print('['+colorama.Fore.LIGHTRED_EX+'@'+colorama.Fore.RESET+'] This tool by | insta: 0xdevil\n\n')
        username = input('['+colorama.Fore.MAGENTA+'+'+colorama.Fore.RESET+'] Username: ')
        password = input('['+colorama.Fore.MAGENTA+'+'+colorama.Fore.RESET+'] Password: ')
        API = APIs(username,password)
        if API.login():
            print('\n['+colorama.Fore.GREEN+'$'+colorama.Fore.RESET+'] Logged in')
            print('['+colorama.Fore.YELLOW+'~'+colorama.Fore.RESET+f'] SessionID {API.session_id}')
            user_to_serv = input('['+colorama.Fore.YELLOW+'?'+colorama.Fore.RESET+'] Username that you want to service: ')
            database = json.load(open(file_path))
            if user_to_serv not in database:
                database[user_to_serv] = {}
                database[user_to_serv]['video'] = '0'
                database[user_to_serv]['photo'] = '0'
                json.dump(database , open(file_path,'w'), sort_keys=True, indent=4)
                database = json.load(open(file_path))
                user_to_serv_id = API.get_id(user_to_serv)
                API.SendDM(user_to_serv_id,'ارسلي بوست وراح احمله وارسله لك\nارسلي كلمة "معلوماتي" وراح اعلمك كم حملة بوست صوره او فيديو\nارسلي كلمة "انتقل لخدمة @username" وسأنتقل لخدمة اسم المستخدم')
            else:
                user_to_serv_id = API.get_id(user_to_serv)
            time.sleep(1) 
            API.SendDM(user_to_serv_id,'تقدر تسخدمني الأن')
            time.sleep(1)
            API.SendDM(user_to_serv_id,'انت بس ارسلي البوست ولا تسولف معي عشان لا انبعص =)')
            time.sleep(2)
            times_check = 0
            while True:
                banner()
                print('['+colorama.Fore.LIGHTWHITE_EX+'#'+colorama.Fore.RESET+'] Wait for client to send something')
                try:
                    dm = API.get_dm()
                    items = dm.json()['inbox']['threads'][0]['items'][0]
                    item_type = items['item_type']
                    thread_id = dm.json()['inbox']['threads'][0]['thread_id'] 
                    user_id = dm.json()['inbox']['threads'][0]['users'][0]['pk']
                    if str(user_id) == str(user_to_serv_id):
                        if item_type == 'text':
                            text = str(items['text'])
                            if text == 'معلوماتي':
                                banner()
                                print('['+colorama.Fore.LIGHTYELLOW_EX+'#'+colorama.Fore.RESET+'] Client request it info')
                                time.sleep(1.5)
                                message = f'''مرحبا\nلديك عدد\nمقاطع: {database[user_to_serv]['video']}\nصور: {database[user_to_serv]['photo']}'''
                                API.SendDM(user_to_serv_id, message)
                            elif 'انتقل لخدمة' in text or 'إنتقل لخدمة' in text:
                                print('['+colorama.Fore.LIGHTYELLOW_EX+'#'+colorama.Fore.RESET+'] Client request to move service')
                                API.SendDM(user_to_serv_id,'حسنا !')
                                user_to_serv =  text.split('انتقل لخدمة')[1]
                                if '@' in user_to_serv:
                                    user_to_serv = user_to_serv.split('@')[1]
                                newuser_to_serv_id = API.get_id(user_to_serv)
                                if str(user_to_serv_id) == str(newuser_to_serv_id):
                                    API.SendDM(user_to_serv_id, 'تستهبل؟')
                                    time.sleep(1)
                                    API.SendDM(user_to_serv_id, 'انا بالفعل اقوم بخدمتك =)')
                                else:
                                    user_to_serv_id = newuser_to_serv_id
                                    time.sleep(1) 
                                    API.SendDM(user_to_serv_id,'تقدر تسخدمني الأن')
                                    time.sleep(1)
                                    API.SendDM(user_to_serv_id,'انت بس ارسلي البوست ولا تسولف معي عشان لا انبعص =)')
                                    if user_to_serv not in database:
                                        database[user_to_serv] = {}
                                        database[user_to_serv]['video'] = '0'
                                        database[user_to_serv]['photo'] = '0'
                                        json.dump(database , open(file_path,'w'), sort_keys=True, indent=4)
                                        database = json.load(open(file_path))
                                        user_to_serv_id = API.get_id(user_to_serv)

                        elif item_type == 'media_share':
                            banner()
                            print('['+colorama.Fore.LIGHTYELLOW_EX+'#'+colorama.Fore.RESET+'] Client request to download a media')
                            media_content = items['media_share']
                            media_id = media_content['id']
                            media_info = API.get_media_info(media_id).json()
                            media_items = media_info['items'][0]
                            media_type = media_items['media_type']
                            if str(media_type) == str(1):       
                                API.SendDM(user_to_serv_id,'قد يأخذ التحميل عدة دقائق يرجى التحلي بالصبر !')
                                print('['+colorama.Fore.LIGHTYELLOW_EX+'#'+colorama.Fore.RESET+'] media_type=photo')
                                url_image = media_items['image_versions2']['candidates'][0]['url']
                                print('['+colorama.Fore.LIGHTYELLOW_EX+'#'+colorama.Fore.RESET+f'] media_url={url_image}')
                                urllib.request.urlretrieve(url_image,'image.jpg',None)
                                if API.SendImage('image.jpg',thread_id):
                                    print('['+colorama.Fore.LIGHTGREEN_EX+'#'+colorama.Fore.RESET+f'] Done download and send !')
                                    count = int(database[user_to_serv]['photo'])
                                    photos_count =  count + 1
                                    database[user_to_serv]['photo'] = str(photos_count) 
                                    json.dump(database , open(file_path,'w'), sort_keys=True, indent=4)
                                    database = json.load(open(file_path))
                                    os.remove('image.jpg')

                            elif str(media_type) == str(2):
                                API.SendDM(user_to_serv_id,'قد يأخذ التحميل عدة دقائق يرجى التحلي بالصبر !')
                                print('['+colorama.Fore.LIGHTYELLOW_EX+'#'+colorama.Fore.RESET+'] media_type=video')       
                                media_content = items['media_share']
                                media_id = media_content['id']
                                media_info = API.get_media_info(media_id)
                                video_items = media_info.json()['items'][0]
                                video_info = video_items['video_versions'][0]
                                url_video = video_info['url']
                                video_width = video_info['width']
                                video_height = video_info['height']
                                video_duration = video_items['video_duration']
                                print('['+colorama.Fore.LIGHTYELLOW_EX+'#'+colorama.Fore.RESET+f'] media_url={url_video}')
                                urllib.request.urlretrieve(url_video,'video.mp4',None)
                                if API.SendVideo('video.mp4',str(thread_id),str(video_height),str(video_width),str(video_duration)):
                
                                    print('['+colorama.Fore.LIGHTGREEN_EX+'#'+colorama.Fore.RESET+f'] Done download and send !')
                                    count = int(database[user_to_serv]['video'])
                                    photos_count =  count + 1
                                    database[user_to_serv]['video'] = str(photos_count) 
                                    json.dump(database , open(file_path,'w'), sort_keys=True, indent=4)
                                    database = json.load(open(file_path))
                                    os.remove('video.mp4')
                        elif item_type == 'clip':
                            banner()
                            API.SendDM(user_to_serv_id,'قد يأخذ التحميل عدة دقائق يرجى التحلي بالصبر !')
                            clip = items['clip']['clip']
                            media_type = clip['media_type']
                            if str(media_type) == str(2):
                                print('['+colorama.Fore.LIGHTYELLOW_EX+'#'+colorama.Fore.RESET+'] media_type=clip_video')      
                                clip_info = clip['video_versions'][0]
                                clip_url = clip_info['url']
                                print('['+colorama.Fore.LIGHTYELLOW_EX+'#'+colorama.Fore.RESET+f'] media_url={clip_url}')
                                urllib.request.urlretrieve(clip_url,'clip.mp4',None)
                                clip_width = clip_info['width']
                                clip_height = clip_info['height']
                                clip_duration = clip['video_duration']
                                if API.SendVideo('clip.mp4', thread_id,clip_height,clip_width,clip_duration):
                                    print('['+colorama.Fore.LIGHTGREEN_EX+'#'+colorama.Fore.RESET+f'] Done download and send !')
                                    count = int(database[user_to_serv]['video'])
                                    photos_count =  count + 1
                                    database[user_to_serv]['video'] = str(photos_count) 
                                    json.dump(database , open(file_path,'w'), sort_keys=True, indent=4)
                                    database = json.load(open(file_path))
                                    os.remove('clip.mp4')
                                
                except Exception as ex:
                    print(str(ex))

                if times_check == 0:
                    times_check += 1
                    time.sleep(1)
                    API.SendDM(user_to_serv_id, 'لاتنسى تضيفني @0xdevil =)')
                elif times_check != 30:
                    times_check += 1
                elif times_check == 30:
                    times_check = 1
                    API.SendDM(user_to_serv_id, 'لاتنسى تضيفني @0xdevil =)')
                banner()
                print('['+colorama.Fore.LIGHTRED_EX+'#'+colorama.Fore.RESET+'] Cool down for 10 sec !')
                time.sleep(10)
             
        else:
            ansr = str(input('['+colorama.Fore.RED+'-'+colorama.Fore.RESET+'] Unable to login wanna try again ?[y/n]'))
            if ansr == 'y' or ansr == 'Y':
                return main()
            else:
                print('['+colorama.Fore.MAGENTA+'^'+colorama.Fore.RESET+'] Follow me\ninstagram @0xdevil')
                exit(0) 
    except KeyboardInterrupt:
            print('['+colorama.Fore.RED+'CTRL+C'+colorama.Fore.RESET+'] Exit [ KeyboardInterrupt ]')
            print('['+colorama.Fore.MAGENTA+'^'+colorama.Fore.RESET+'] Follow me\ninstagram @0xdevil')
            exit(0) 


if __name__ == '__main__':
    main() 

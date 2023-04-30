# coding=utf-8
import discord, asyncio, time, socket, datetime, json, os, threading, tkinter as tk
from discord import client
from tkinter import messagebox as msg_box

if not os.path.isdir('logs'):
    os.mkdir('logs')

def print_log(text, mode=0):
    if mode == 0:
        window.log_text['state'] = tk.NORMAL
        window.log_text.insert(tk.END, f'{dae(1)} {text}\n')
        window.log_text['state'] = tk.DISABLED
        fil = open(f'./logs/{dae(0)}.txt', mode='a+', encoding='utf-8')
        fil.write(f'{dae(1)} {text}\n')
        fil.close()
    else:
        window.log_text['state'] = tk.NORMAL
        window.log_text.insert(tk.END, f'{text}\n')
        window.log_text['state'] = tk.DISABLED
        fil = open(f'./logs/{dae(0)}.txt', mode='a+', encoding='utf-8')
        fil.write(f'{text}\n')
        fil.close()

def dae(inp, inp2=''):
    year = []
    if inp2 == '':
        year = list([date for date in time.localtime()[0:6]])
    else:
        year = list([date for date in inp2])
    for i in range(0, len(year)):
        if year[i] < 10:
            year[i] = '0' + str(year[i])
        else:
            year[i] = str(year[i])
    
    if inp2 == '':
        if inp == 0:
            return year[0] + '-' + year[1] + '-' + year[2]
        elif inp == 1:
            return year[0] + '/' + year[1] + '/' + year[2] + ' ' + year[3] + ':' + year[4] + ':' + year[5]
    else:
        return year[0] + ':' + year[1] + ':' + year[2]

class Config():
    def __init__(self):
        if os.path.isfile('config.json'):
            fil = open('config.json', mode='r', encoding='utf-8')
            data = json.load(fil)
            fil.close()
        else:
            fil = open('config.json', mode='w', encoding='utf-8')
            data = {
                'token': '',
                'dvc_channel_id': 0,
                'admin_id': 0, 
                'prefix': '$',
                'embed_color': '00ff40',
                'embed_icon': 'https://cdn.logojoy.com/wp-content/uploads/20210422095037/discord-mascot.png'
            }
            fil.write(json.dumps(data, indent=4, separators=(',', ': ')))
            fil.close()
        self.token = data['token']
        self.dvc_channel_id = data['dvc_channel_id']
        self.admin_id = data['admin_id']
        self.prefix = data['prefix']
        self.embed_color = data['embed_color']
        self.embed_icon = data['embed_icon']

    def save(self, data):
        fil = open('config.json', mode='w', encoding='utf-8')
        fil.write(json.dumps(data, indent=4, separators=(',', ': ')))
        fil.close()

class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_channel = {}

        self.time_range = datetime.timedelta(hours = 8)

    async def on_ready(self):
        print_log(f'------------------------------\n\n\n\n{dae(0)}\n------------------------------', 1)
        print_log(f'{self.user} 啟動。')
        print_log(f'目前運作的電腦為:{socket.gethostname()}, PID(處理程序識別碼):{os.getpid()}。')

        self.bg_task = self.loop.create_task(self.create_channel_bk())
        self.bg_task = self.loop.create_task(self.delete_channel_bk())
        self.bg_task = self.loop.create_task(self.text_channel_bk())

        window.stop_button['state'] = tk.NORMAL

    async def create_channel_bk(self):
        dvc_channel = self.get_channel(window.data['dvc_channel_id'])
        while not(self.is_closed()):
            await asyncio.sleep(1)
            for user in dvc_channel.members:
                voice_channel = await user.guild.create_voice_channel(name=f'{user.display_name} 的頻道', category=dvc_channel.category)
                await user.move_to(voice_channel)
                overwrites = {user.guild.default_role:discord.PermissionOverwrite(view_channel=False), user:discord.PermissionOverwrite(view_channel=True)}
                text_channel = await user.guild.create_text_channel(name=f'{user.display_name} 的頻道', category=dvc_channel.category, overwrites=overwrites)
                print_log(f'創建一個語音頻道，頻道ID:{voice_channel.id}')
                print_log(f'創建一個文字頻道，頻道ID: {text_channel.id}')
                self.created_channel[voice_channel.id] = {'voice':{'channel':voice_channel, 'id':voice_channel.id}, 'text':{'channel':text_channel, 'id':text_channel.id, 'hide_list':{user.id:{'user':user, 'id':user.id, 'hide':True}}}, 'permission':{user.id :{'user':user, 'id':user.id}}}

    async def delete_channel_bk(self):
        while not(self.is_closed()):
            await asyncio.sleep(10)
            for key in list(self.created_channel.keys()):
                channel = self.created_channel[key]
                try:
                    if channel['voice']['channel'].members == []:
                        await channel['voice']['channel'].delete()
                        await channel['text']['channel'].delete()
                        print_log(f'刪除一個語音頻道，頻道ID:{channel["voice"]["id"]}')
                        print_log(f'刪除一個文字頻道，頻道ID:{channel["text"]["id"]}')
                        del self.created_channel[key]
                except Exception as e:
                    print(dae(1) + e)

    async def text_channel_bk(self):
        while not(self.is_closed()):
            await asyncio.sleep(1)
            for key in list(self.created_channel.keys()):
                channel = self.created_channel[key]
                for member in channel['voice']['channel'].members:
                    if channel['text']['hide_list'].get(member.id) == None:
                        channel['text']['hide_list'][member.id] = {'user':member, 'id':member.id, 'hide':True}
                        overwrite = discord.PermissionOverwrite()
                        overwrite.view_channel = True
                        await channel['text']['channel'].set_permissions(member, overwrite=overwrite)
                for user_id in list(channel['text']['hide_list'].keys()):
                    member = channel['text']['hide_list'][user_id]['user']
                    if member not in channel['voice']['channel'].members and channel['text']['hide_list'][user_id]['hide'] == True:
                        overwrite = discord.PermissionOverwrite()
                        overwrite.view_channel = None
                        await channel['text']['channel'].set_permissions(member, overwrite=overwrite)
                        del channel['text']['hide_list'][user_id]

    async def on_message(self, mes):
        prefix = window.data['prefix']
        embed_color = int(f'0x{window.data["embed_color"]}', 16)
        embed_icon = window.data['embed_icon']

        if mes.author == self.user:
            return
        elif mes.content.lower().startswith(prefix):
            print_log(f'使用者ID:{mes.author.id} 說:{mes.content}')
            command = mes.content[len(prefix):].lower().split(' ', 1)

            permission = False
            if mes.author.voice != None:
                if self.created_channel.get(mes.author.voice.channel.id) != None:
                    permission = self.created_channel[mes.author.voice.channel.id]['permission'].get(mes.author.id) != None

            if command[0] == 'help':
                embed=discord.Embed(title='幫助清單:', color=embed_color, timestamp=datetime.datetime.now()-self.time_range)
                embed.set_author(name="動態語音系統", icon_url=embed_icon)
                embed.set_thumbnail(url=embed_icon)
                out_1 = '`' + prefix + 'name <名稱>`  更改你頻道的名稱。\n'
                out_1 += '`' + prefix + 'limit <數字>`  更改你頻道的人數上限。'
                embed.add_field(name="基礎設定", value=out_1, inline=False)

                out_2 = '`' + prefix + 'hide`  將語音頻道隱藏，使其他使用者無法看見該頻道。\n'
                out_2 += '`' + prefix + 'unhide`  將頻道設為可被看見。\n'
                out_2 += '`' + prefix + 'lock`  將頻道上鎖，其他使用者無法自由加入。\n'
                out_2 += '`' + prefix + 'unlock`  將頻道解鎖，其他使用者可以自由加入。\n'
                out_2 += '`' + prefix + 'thide <@User>`  對指定使用者隱藏文字頻道。\n'
                out_2 += '`' + prefix + 'tunhide <@User>`  對指定使用者取消隱藏文字頻道。\n'
                out_2 += '※使用者仍然須在語音頻道內才能看見該頻道附屬的文字頻道'
                embed.add_field(name="參與者設定", value=out_2, inline=False)

                out_3 = '`' + prefix + 'kick <@User>`  踢出頻道內的某個使用者。\n'
                out_3 += '`' + prefix + 'ban <@User>`  驅逐頻道內的某個使用者。\n'
                out_3 += '`' + prefix + 'unban <@User>`  解除驅逐頻道內的某個使用者。'
                embed.add_field(name="隱私設定", value=out_3, inline=False)

                out_4 = '`' + prefix + 'tt <@User>`  給予某個使用者管理權限。\n`' + prefix + 'ut <@User>`  收回某個使用者的管理權限。\n`' + prefix + 'tl`  列出該頻道內具有管理權限的使用者。\n`' + prefix + 'claim`  在所有管理員離開後，成為新的管理員。'
                embed.add_field(name="管理設定", value=out_4, inline=False)

                embed.add_field(name="危險地帶", value='`' + prefix + 'del`  刪除該頻道。', inline=False)
                await mes.channel.send(embed=embed)
            
            #改名指令
            elif command[0] == 'name':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能更改名稱。')
                else:
                    if permission:
                        if len(command) == 1:
                            await mes.channel.send('命令語法不正確。')
                        else:
                            try:
                                await mes.author.voice.channel.edit(name=command[1])
                                await self.created_channel[mes.author.voice.channel.id]['text']['channel'].edit(name=command[1].replace(' ', '-'))
                                await mes.channel.send('名稱更改成功。')
                            except Exception as ex:
                                await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能更改名稱。')

            #人數限制指令
            elif command[0] == 'limit':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能設定人數限制。')
                else:
                    if permission:
                        if len(command) == 1:
                            await mes.channel.send('命令語法不正確。')
                        else:
                            try:
                                if int(command[1]) < 100 and int(command[1]) >= 0:
                                    await mes.author.voice.channel.edit(user_limit=int(command[1]))
                                    await mes.channel.send('人數限制更改成功。')
                                else:
                                    await mes.channel.send('無法更改限制至指定數字。')
                            except Exception as ex:
                                await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能設定人數限制。')

            #隱藏指令
            elif command[0] == 'hide':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能隱藏頻道。')
                else:
                    if permission:
                        try:
                            overwrite = discord.PermissionOverwrite()
                            overwrite.view_channel = False
                            await mes.author.voice.channel.set_permissions(mes.author.guild.default_role, overwrite=overwrite)
                            await mes.channel.send('頻道隱藏成功。')
                        except Exception as ex:
                            await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能隱藏頻道。')

            #取消隱藏指令
            elif command[0] == 'unhide':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能取消隱藏頻道。')
                else:
                    if permission:
                        try:
                            overwrite = discord.PermissionOverwrite()
                            overwrite.view_channel = True
                            await mes.author.voice.channel.set_permissions(mes.author.guild.default_role, overwrite=overwrite)
                            await mes.channel.send('頻道取消隱藏成功。')
                        except Exception as ex:
                            await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能取消隱藏頻道。')

            #隱藏指令(文字頻道)
            elif command[0] == 'thide':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能隱藏文字頻道。')
                else:
                    if permission:
                        if len(command) == 1:
                            await mes.channel.send('命令語法不正確。')
                        else:
                            try:
                                if '!' in command[1]:
                                    user_temp = await mes.author.guild.fetch_member(int(command[1][3:command[1].find('>')]))
                                else:
                                    user_temp = await mes.author.guild.fetch_member(int(command[1][2:command[1].find('>')]))
                                overwrite = discord.PermissionOverwrite()
                                overwrite.view_channel = False
                                await self.created_channel[mes.author.voice.channel.id]['text']['channel'].set_permissions(user_temp, overwrite=overwrite)
                                self.created_channel[mes.author.voice.channel.id]['text']['hide_list'][user_temp.id] = {'user':user_temp, 'id':user_temp.id, 'hide':False}
                                await mes.channel.send('文字頻道隱藏成功。')
                            except Exception as ex:
                                await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能隱藏文字頻道。')
            
            #取消隱藏指令(文字頻道)
            elif command[0] == 'tunhide':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能取消隱藏文字頻道。')
                else:
                    if permission:
                        if len(command) == 1:
                            await mes.channel.send('命令語法不正確。')
                        else:
                            try:
                                if '!' in command[1]:
                                    user_temp = await mes.author.guild.fetch_member(int(command[1][3:command[1].find('>')]))
                                else:
                                    user_temp = await mes.author.guild.fetch_member(int(command[1][2:command[1].find('>')]))
                                overwrite = discord.PermissionOverwrite()
                                overwrite.view_channel = True
                                await self.created_channel[mes.author.voice.channel.id]['text']['channel'].set_permissions(user_temp, overwrite=overwrite)
                                self.created_channel[mes.author.voice.channel.id]['text']['hide_list'][user_temp.id] = {'user':user_temp, 'id':user_temp.id, 'hide':True}
                                await mes.channel.send('文字頻道取消隱藏成功。')
                            except Exception as ex:
                                await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能取消隱藏文字頻道。')

            #上鎖指令
            elif command[0] == 'lock':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能上鎖頻道。')
                else:
                    if permission:
                        try:
                            overwrite = discord.PermissionOverwrite()
                            overwrite.connect = False
                            await mes.author.voice.channel.set_permissions(mes.author.guild.default_role, overwrite=overwrite)
                            await mes.channel.send('頻道上鎖成功。')
                        except Exception as ex:
                            await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能上鎖頻道。')

            #取消上鎖指令
            elif command[0] == 'unlock':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能取消上鎖頻道。')
                else:
                    if permission:
                        try:
                            overwrite = discord.PermissionOverwrite()
                            overwrite.connect = True
                            await mes.author.voice.channel.set_permissions(mes.author.guild.default_role, overwrite=overwrite)
                            await mes.channel.send('頻道取消上鎖成功。')
                        except Exception as ex:
                            await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能取消上鎖頻道。')

            #踢出指令
            elif command[0] == 'kick':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能踢出使用者。')
                else:
                    if permission:
                        if len(command) == 1:
                            await mes.channel.send('命令語法不正確。')
                        else:
                            try:
                                for name_temp in mes.author.voice.channel.members:
                                    if str(name_temp.id) in command[1]:
                                        await name_temp.move_to(None)
                                        await mes.channel.send('踢出使用者成功。')
                            except Exception as ex:
                                await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能踢出使用者。')

            #驅逐指令
            elif command[0] == 'ban':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能驅逐使用者。')
                else:
                    if permission:
                        if len(command) == 1:
                            await mes.channel.send('命令語法不正確。')
                        else:
                            try:
                                for name_temp in mes.author.voice.channel.members:
                                    if str(name_temp.id) in command[1]:
                                        await name_temp.move_to(None)
                                        overwrite = discord.PermissionOverwrite()
                                        overwrite.view_channel = False
                                        overwrite.connect = False
                                        await mes.author.voice.channel.set_permissions(name_temp, overwrite=overwrite)
                                        await mes.channel.send('驅逐使用者成功。')
                                        return
                                if '!' in command[1]:
                                    user_temp = await mes.author.guild.fetch_member(int(command[1][3:command[1].find('>')]))
                                else:
                                    user_temp = await mes.author.guild.fetch_member(int(command[1][2:command[1].find('>')]))
                                overwrite = discord.PermissionOverwrite()
                                overwrite.view_channel = False
                                overwrite.connect = False
                                await mes.author.voice.channel.set_permissions(user_temp, overwrite=overwrite)
                                await mes.channel.send('驅逐使用者成功。')
                            except Exception as ex:
                                await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能驅逐使用者。')

            #取消驅逐指令
            elif command[0] == 'unban':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能取消驅逐使用者。')
                else:
                    if permission:
                        if len(command) == 1:
                            await mes.channel.send('命令語法不正確。')
                        else:
                            try:
                                if '!' in command[1]:
                                    user_temp = await mes.author.guild.fetch_member(int(command[1][3:command[1].find('>')]))
                                else:
                                    user_temp = await mes.author.guild.fetch_member(int(command[1][2:command[1].find('>')]))
                                overwrite = discord.PermissionOverwrite()
                                overwrite.view_channel = True
                                overwrite.connect = True
                                await mes.author.voice.channel.set_permissions(user_temp, overwrite=overwrite)
                                await mes.channel.send('取消驅逐使用者成功。')
                            except Exception as ex:
                                await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能取消驅逐使用者。')

            #新增權限指令
            elif command[0] == 'tt':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能新增管理員。')
                else:
                    if permission:
                        if len(command) == 1:
                            await mes.channel.send('命令語法不正確。')
                        else:
                            try:
                                if '!' in command[1]:
                                    user_id_temp = int(command[1][3:command[1].find('>')])
                                else:
                                    user_id_temp = int(command[1][2:command[1].find('>')])
                                
                                if self.created_channel[mes.author.voice.channel.id]['permission'].get(user_id_temp) != None:
                                    await mes.channel.send('該位使用者已經是管理員了。')    
                                else:
                                    user_temp = await mes.author.guild.fetch_member(user_id_temp)
                                    self.created_channel[mes.author.voice.channel.id]['permission'][user_id_temp] = {'user':user_temp, 'id':user_id_temp}
                                    await mes.channel.send('管理員新增成功。')
                            except Exception as ex:
                                await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能新增管理員。')

            #移除權限指令
            elif command[0] == 'ut':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能移除管理員。')
                else:
                    if permission:
                        if len(command) == 1:
                            await mes.channel.send('命令語法不正確。')
                        else:
                            try:
                                if '!' in command[1]:
                                    user_id_temp = int(command[1][3:command[1].find('>')])
                                else:
                                    user_id_temp = int(command[1][2:command[1].find('>')])
                                
                                if self.created_channel[mes.author.voice.channel.id]['permission'].get(user_id_temp) == None:
                                    await mes.channel.send('該位使用者本來就不是管理員了。')    
                                else:
                                    del self.created_channel[mes.author.voice.channel.id]['permission'][user_id_temp]
                                    await mes.channel.send('管理員移除成功。')
                            except Exception as ex:
                                await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能移除管理員。')

            #權限列表指令
            elif command[0] == 'tl':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能顯示管理員列表。')
                else:
                    try:
                        out = ''
                        for ci_temp in list(self.created_channel[mes.author.voice.channel.id]['permission'].keys()):
                            out = out + '<@' + str(self.created_channel[mes.author.voice.channel.id]['permission'][ci_temp]['id']) + '>\n'
                        embed=discord.Embed(title='該頻道的管理員有:', description=out, color=embed_color, timestamp=datetime.datetime.now()-self.time_range)#綠色
                        embed.set_author(name="動態語音系統", icon_url=embed_icon)
                        embed.set_thumbnail(url=embed_icon)
                        await mes.channel.send(embed=embed)
                    except Exception as ex:
                        await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
            
            #代替權限指令
            elif command[0] == 'claim':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能要求成為管理員。')
                else:
                    if self.created_channel.get(mes.author.voice.channel.id) != None:
                        try:
                            bool_temp = True
                            for user_temp in mes.author.voice.channel.members:
                                if self.created_channel[mes.author.voice.channel.id]['permission'].get(user_temp.id) != None:
                                    bool_temp = False
                                    break
                            if bool_temp:
                                self.created_channel[mes.author.voice.channel.id]['permission'].clear
                                user_temp = await mes.author.guild.fetch_member(mes.author.id)
                                self.created_channel[mes.author.voice.channel.id]['permission'][mes.author.id] = {'user':user_temp, 'id':mes.author.id}
                                await mes.channel.send('成為新任管理員成功。')
                            else:
                                await mes.channel.send('管理員仍未離開當前的語音頻道。')
                            pass
                        except Exception as ex:
                            await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
            
            #頻道刪除指令
            elif command[0] == 'del':
                if mes.author.voice == None:
                    await mes.channel.send('你需要在一個語音頻道中才能刪除頻道。')
                else:
                    if permission:
                        try:
                            id_temp = mes.author.voice.channel.id
                            await self.created_channel[id_temp]['voice']['channel'].delete()
                            await self.created_channel[id_temp]['text']['channel'].delete()
                            print_log(f'刪除一個語音頻道，頻道ID:{self.created_channel[id_temp]["voice"]["id"]}')
                            print_log(f'刪除一個文字頻道，頻道ID:{self.created_channel[id_temp]["text"]["id"]}')
                            del self.created_channel[id_temp]
                            await mes.channel.send('頻道刪除成功。')
                        except Exception as ex:
                            await mes.channel.send('發生了意料之外的問題，請聯繫技術人員進行處理。\n(錯誤代碼:`' + str(ex) + '`)')
                    else:
                        await mes.channel.send('你需要擁有這個語音頻道的管理權限才能刪除頻道。')

            elif command[0] == 'dev':
                pass

    def stop(self):
        exit()

class GUI_Window():
    def __init__(self):
        #~設定主視窗
        self.root = tk.Tk()
        self.root.title('Discord動態語音機器人')
        self.root.minsize(width=600, height=450)
        self.root.geometry('800x600')
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        

        #~設定四框架
        self.config_frame = tk.LabelFrame(self.root, text='設置')
        self.button_frame = tk.LabelFrame(self.root, text='選項')
        self.version_frame = tk.LabelFrame(self.root, text='版本資訊')
        self.log_frame = tk.LabelFrame(self.root, text='輸出')

        sticky_mode = 'nswe'
        pad = 3

        #~放置框架
        self.config_frame.grid(column=1, row=0, padx=pad, pady=pad, sticky=sticky_mode)
        self.button_frame.grid(column=1, row=1, padx=pad, pady=pad, sticky=sticky_mode)
        self.version_frame.grid(column=1, row=2, padx=pad, pady=pad, sticky=sticky_mode)
        self.log_frame.grid(column=0, row=0, rowspan=3, padx=pad, pady=pad, sticky=sticky_mode)

        #~鎖定框架大小
        self.config_frame.grid_propagate(0)
        self.button_frame.grid_propagate(0)
        self.version_frame.grid_propagate(0)
        self.log_frame.grid_propagate(0)


        #~四框架設定
        #~設置框架
        label_list = []
        #~Token
        self.token_label = tk.Label(self.config_frame, text='Token:')

        self.token = tk.StringVar(value=config.token)
        self.token_entry = tk.Entry(self.config_frame, textvariable=self.token, show='●', width=0)
        label_list.append([self.token_label, self.token_entry])
        
        #~管理員ID
        self.admin_id_label = tk.Label(self.config_frame, text='管理員ID:')

        self.admin_id = tk.StringVar(value=str(config.admin_id))
        self.admin_id_entry = tk.Entry(self.config_frame, textvariable=self.admin_id, width=0)
        label_list.append([self.admin_id_label, self.admin_id_entry])

        #~命令前綴
        self.prefix_label = tk.Label(self.config_frame, text='命令前綴:')

        self.prefix = tk.StringVar(value=config.prefix)
        self.prefix_entry = tk.Entry(self.config_frame, textvariable=self.prefix, width=0)
        label_list.append([self.prefix_label, self.prefix_entry])

        #~語音頻道ID
        self.dvc_channel_id_label = tk.Label(self.config_frame, text='語音頻道ID:')

        self.dvc_channel_id = tk.StringVar(value=str(config.dvc_channel_id))
        self.dvc_channel_id_entry = tk.Entry(self.config_frame, textvariable=self.dvc_channel_id, width=0)
        label_list.append([self.dvc_channel_id_label, self.dvc_channel_id_entry])

        #~Embed顏色
        self.embed_color_label = tk.Label(self.config_frame, text='Embed顏色(HEX):')

        self.embed_color = tk.StringVar(value=config.embed_color)
        self.embed_color_entry = tk.Entry(self.config_frame, textvariable=self.embed_color, width=0)
        label_list.append([self.embed_color_label, self.embed_color_entry])

        #~Embed圖片
        self.embed_icon_label = tk.Label(self.config_frame, text='Embed圖片:')

        self.embed_icon = tk.StringVar(value=config.embed_icon)
        self.embed_icon_entry = tk.Entry(self.config_frame, textvariable=self.embed_icon, width=0)
        label_list.append([self.embed_icon_label, self.embed_icon_entry])

        #~放置Label
        for label in label_list:
            label[0].grid(column=0, row=label_list.index(label), sticky='w')
            label[1].grid(column=1, row=label_list.index(label), padx=pad, pady=pad, sticky=sticky_mode)

        #~按鈕框架
        #~啟動
        self.start_button = tk.Button(self.button_frame, text='啟動', command=self.start_button_command)
        self.start_button.grid(column=0, row=0, padx=pad, pady=pad, sticky=sticky_mode)

        #~停止
        self.stop_button = tk.Button(self.button_frame, text='停止', command=self.stop_client, state=tk.DISABLED)
        self.stop_button.grid(column=0, row=1, padx=pad, pady=pad, sticky=sticky_mode)

        #~儲存
        self.save_button = tk.Button(self.button_frame, text='儲存', command=self.save_button_command)
        self.save_button.grid(column=0, row=2, padx=pad, pady=pad, sticky=sticky_mode)


        #~輸出框架
        self.log_text = tk.Text(self.log_frame, state=tk.DISABLED, width=1, height=1)
        self.log_text.grid(column=0, row=0, padx=pad*2, pady=pad*2, sticky=sticky_mode)


        #~設置比例
        self.config_frame.columnconfigure(0, weight=0)
        self.config_frame.columnconfigure(1, weight=1)
        
        self.button_frame.columnconfigure(0, weight=1)

        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)

        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=5)
        self.root.rowconfigure(1, weight=4)
        self.root.rowconfigure(2, weight=3)

    def on_closing(self):
        msg_input = msg_box.askyesno('離開', '確定要離開嗎')
        if msg_input:
            self.root.destroy()
            os.system(f'taskkill /f /PID {os.getpid()}')

    def start_button_command(self):
        #~啟動參數
        try:
            self.data = {
                'token': self.token.get(),
                'dvc_channel_id': int(self.dvc_channel_id.get()),
                'admin_id': int(self.admin_id.get()),
                'prefix': self.prefix.get(),
                'embed_color': self.embed_color.get(),
                'embed_icon': self.embed_icon.get()
            }
            self.start_button['state'] = tk.DISABLED
            self.save_button['state'] = tk.DISABLED
            thr = threading.Thread(target=self.start_client)
            thr.start()
        except:
            msg_box.showerror('錯誤', '參數錯誤，請重新填寫')
    
    def start_client(self):
        try:
            client.run(config.token)
        except:
            self.start_button['state'] = tk.NORMAL
            self.save_button['state'] = tk.NORMAL
            msg_box.showerror('錯誤', '參數錯誤，請重新填寫')

    def stop_client(self):
        self.root.destroy()
        os.system(f'taskkill /f /PID {os.getpid()}')

    def save_button_command(self):
        try:
            self.data = {
                'token': self.token.get(),
                'dvc_channel_id': int(self.dvc_channel_id.get()),
                'admin_id': int(self.admin_id.get()),
                'prefix': self.prefix.get(),
                'embed_color': self.embed_color.get(),
                'embed_icon': self.embed_icon.get()
            }
            config.save(self.data)
        except:
            msg_box.showerror('錯誤', '參數錯誤，請重新填寫')

config = Config()
window = GUI_Window()
client = DiscordClient()
window.root.mainloop()


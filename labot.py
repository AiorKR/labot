# -*- coding:utf-8 -*- 

import discord, asyncio
import labotenv #토큰값 저장 env파일
import requests
import json
import datetime
import time
from discord.ext import tasks, commands

import random

#디스코드 선언부
token = labotenv.discord_token
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
latoken = labotenv.lostArk_token

#시간 사전설정
kst = datetime.timezone(datetime.timedelta(hours=9)) #KST(한국시간)으로 설정
ri = datetime.time(hour=10, minute=1, tzinfo=kst)
startEventsTime = datetime.time(hour=10, minute=1, tzinfo=kst)
endEventsTime = datetime.time(hour=22, tzinfo=kst)
chaosGateTime = datetime.time(minute=48, tzinfo=kst)
scheduleTime = datetime.time(hour=7, tzinfo=kst)

##################################################
#정기 스케쥴
"""
@tasks.loop(time=ri) #정기점검 루틴
async def print_test():
    now = datetime.datetime.now()
    await bot.get_guild(labotenv.serverId).get_channel(labotenv.channelId).send(now, delete_after=30)
    print(now)

@tasks.loop(time=startEventsTime) #이벤트 시작 루틴
async def startEvents():
    event = Event()
    await bot.get_guild(labotenv.serverId).get_channel(labotenv.channelId).send(embed=event.endEventList(), delete_after=3600)

@tasks.loop(time=endEventsTime) #이벤트 종료 루틴
async def endEvents():
    laRole = bot.get_guild(labotenv.serverId).get_role(labotenv.lostArkId) #"서버 내 로스트아크 플레이어들이 부여받은 역할"의 ID
    event = Event()
    await bot.get_guild(labotenv.serverId).get_channel(labotenv.channelId).send("{}".format(laRole.mention), delete_after=28800)
    await bot.get_guild(labotenv.serverId).get_channel(labotenv.channelId).send(embed=event.endEventList(), delete_after=28800)
    print(laRole)
    time.sleep(1) #중복발송 방지
"""
@tasks.loop(time=scheduleTime) #스케줄 루틴
async def adventure():
    cal = Calendar()
    await bot.get_guild(labotenv.serverId).get_channel(labotenv.channelId).send(embed=cal.adventure(), delete_after=36000)
"""
@tasks.loop(seconds=20) #카오스게이트 루틴
async def chaosGate():  
    now = datetime.datetime.now()
    print(now)
    time.sleep()
"""
    ##################################################
@bot.event
async def on_ready(): # 봇이 준비가 되면 1회 실행되는 부분
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('언제나 함께')) #dnd= '다른 용무 중', idle = '자리 비움'
    print("I'm Ready!")
    print(bot.user.name)
    
    #############
    #정기루틴 시작
    #############
    adventure.start()
    #chaosGate.start()

#LostArk API 공통 헤더
headers = {
    'accept': 'application/json',
    'authorization': latoken,
    'Content-Type': 'application/json' #POST 처리용
}

#캐릭터
class Character:
    def __init__(self, str):
        self.str = str

    #검색    
    def search(self):
        url = 'https://developer-lostark.game.onstove.com/armories/characters/'+self.str
        response = requests.get(url, headers=headers)
        if(response.status_code == 200):
            contents = response.json() #dict 타입
            dictPreset = contents['ArmoryProfile']

            #요약정보
            serverName = dictPreset['ServerName']
            expeditionLevel = dictPreset['ExpeditionLevel']
            if(str(dictPreset['Title']) == 'None'):
                title = '없음'
            else:
                title = dictPreset['Title']
            pvpGradeName = dictPreset['PvpGradeName']
            guildName = dictPreset['GuildName']
            townInfo = 'Lv.' + str(dictPreset['TownLevel'])+' '+dictPreset['TownName']
            miniInfo= '[`서버` : %s] [`원정대 레벨` : %s] [`칭호` : %s]\n[`PvP` : %s] [`길드` : %s]\n[`영지` : %s]'%(serverName, expeditionLevel, title, pvpGradeName, guildName, townInfo)
            
            #캐릭터 정보
            className = dictPreset['CharacterClassName']
            itemLevel = dictPreset['ItemAvgLevel']
            charLevel = dictPreset['CharacterLevel']
            skillPoint = dictPreset['TotalSkillPoint']
            charInfo = '`직업` : %s\n`아이템 레벨` : %s\n`전투레벨` : %s\n`보유 스킬 포인트` : %s'%(className, itemLevel, charLevel, skillPoint)

            #전투 특성
            specPreset = dictPreset['Stats']
            specDict = {}
            for i in range(len(specPreset)):
                for key in specPreset[i]:
                    if(key == 'Type'):
                        specDict[specPreset[i].get('Type')] = specPreset[i].get('Value')
            spec = '`공격력` : %s\n`최대 생명력` : %s\n'%(specDict.get('공격력'), specDict.get('최대 생명력'))
            combatSpec = '`치명` : %s\n`특화` : %s\n`신속` : %s\n`제압` : %s\n`인내` : %s\n`숙련` : %s'%(specDict.get('치명'), specDict.get('특화'), specDict.get('신속'), specDict.get('제압'), specDict.get('인내'), specDict.get('숙련'))
            
            #각인
            response = requests.get(url+'/engravings', headers=headers) #각인 정보를 위한 재설정
            contents = response.json() #dict 타입
            engPreset = contents['Effects']
            engList = []
            eng=""
            for i in range(len(engPreset)):
                for key in engPreset[i]:
                    if(key == 'Name'):
                        engList.append(engPreset[i].get('Name'))
            for i in engList:
                eng += '`'+ i[:-6] +'` : '+i[-5:] +'\n'

            #임베드 출력
            embed = discord.Embed(title= self.str, url = 'https://lostark.game.onstove.com/Profile/Character/%s'%self.str, description=miniInfo, color=0x62c1cc)
            embed.add_field(name='캐릭터 정보', value=charInfo + '\n\n' + spec, inline=True)
            embed.add_field(name='전투 특성', value=combatSpec, inline=True)
            embed.add_field(name='각인 효과', value=eng, inline=True)
            embed.set_footer(text = "닉네임을 누르면 전투정보실로 이동합니다.")

        else:
            code = {201 : 'Bad Request', 401 : 'Unauthorized', 403 : 'Forbidden', 404 : 'Not Found', 415 : 'Unsupported Media Type', 429 : 'Rate Limite Exceeded', 500 : 'Internal Server Error', 502 : 'Bad Gateway', 503 : 'Service Unavailable', 504 : 'Gateway Timeout'}                
            for key in code.keys():
                if(response.status_code == key):
                    status = code.get(key)
            embed = discord.Embed(title= status, description='', color=0x62c1cc)
            embed.add_field(name='response.status_code', value=response.status_code, inline=False)
        return embed
    
    #수집품
    def collect(self):
        url = 'https://developer-lostark.game.onstove.com/armories/characters/'+self.str+'/collectibles'
        response = requests.get(url, headers=headers)
        if(response.status_code == 200):
            contents = response.json() #dict 타입
            category = ''
            point = ''
            pointPercentage = ''
            sumRes=0
            for i in range(len(contents)):
                for key in contents[i].keys():
                    if(key == 'Type'):
                        category += '`'+contents[i].get('Type')+'`'+ '\n'
                    if(key == 'Point'):
                        point += '`' + str(contents[i].get('Point'))+'`' + ' / '+ str(contents[i].get('MaxPoint'))+'     '+'\n'
                    if(key == 'MaxPoint'):
                        pointPercentage += '`'+str(round((contents[i].get('Point') / contents[i].get('MaxPoint'))*100,2))+'`' + '%\n'
                        sumRes += (contents[i].get('Point') / contents[i].get('MaxPoint'))
            
            average = str(round((sumRes / len(contents))*100,2))
            desStr = self.str + '의 수집형 포인트' + '\n' + '평균 수집율 : ' + '`' + average + '`%'

            #임베드 출력
            embed = discord.Embed(title= self.str, url = 'https://lostark.game.onstove.com/Profile/Character/%s'%self.str, description=desStr, color=0x62c1cc)
            embed.add_field(name='항목', value=category, inline=True)
            embed.add_field(name='수집개수', value=point, inline=True)
            embed.add_field(name='수집율', value=pointPercentage, inline=True)
            embed.set_footer(text = "닉네임을 누르면 전투정보실로 이동합니다.")

        else:
            code = {201 : 'Bad Request', 401 : 'Unauthorized', 403 : 'Forbidden', 404 : 'Not Found', 415 : 'Unsupported Media Type', 429 : 'Rate Limite Exceeded', 500 : 'Internal Server Error', 502 : 'Bad Gateway', 503 : 'Service Unavailable', 504 : 'Gateway Timeout'}                
            for key in code.keys():
                if(response.status_code == key):
                    status = code.get(key)
            embed = discord.Embed(title= status, description='', color=0x62c1cc)
            embed.add_field(name='response.status_code', value=response.status_code, inline=False)
        return embed

#도전어비스던전
class ChallengeAbyss: 
    response = requests.get('https://developer-lostark.game.onstove.com/gamecontents/challenge-abyss-dungeons', headers=headers)
    if(response.status_code == 200):
        contents = response.json() #list 타입
        if(contents[0]['AreaName'] == contents[1]['AreaName']):
            areaName = contents[0]['AreaName'] 
            image = contents[0]['Image']
            startTime = contents[0]['StartTime']
            endTime = contents[0]['EndTime']
            minItemLevel = contents[0]['MinItemLevel']
            embed = discord.Embed(title= '도전 어비스 던전', description='', color=0x62c1cc) 
            embed.set_image(url=image)
            embed.add_field(name=areaName, value=startTime + ' ~ ' + endTime + '\n 최소입장레벨 : ' + str(minItemLevel), inline=False)
        else:
            status = '데이터에 오류가 발생하였습니다. code=200'
    else:
            code = {201 : 'Bad Request', 401 : 'Unauthorized', 403 : 'Forbidden', 404 : 'Not Found', 415 : 'Unsupported Media Type', 429 : 'Rate Limite Exceeded', 500 : 'Internal Server Error', 502 : 'Bad Gateway', 503 : 'Service Unavailable', 504 : 'Gateway Timeout'}                
            for key in code.keys():
                if(response.status_code == key):
                    status = code.get(key)
            embed = discord.Embed(title= status, description='', color=0x62c1cc)
            embed.add_field(name='response.status_code', value=response.status_code, inline=False)

#도전가디언토벌
class ChallengeGuardian:    
    response = requests.get('https://developer-lostark.game.onstove.com/gamecontents/challenge-guardian-raids', headers=headers)
    if(response.status_code == 200):
        contents = response.json() #dict 타입
        raid = contents['Raids']
        embed = discord.Embed(title= '도전 가디언 토벌', description='', color=0x62c1cc)

        for i in range(0, len(raid)):
            embed.add_field(name='', value=raid[i]['Name']+' : '+raid[i]['StartTime']+' ~ '+raid[i]['EndTime'], inline=False)

    else:
            code = {201 : 'Bad Request', 401 : 'Unauthorized', 403 : 'Forbidden', 404 : 'Not Found', 415 : 'Unsupported Media Type', 429 : 'Rate Limite Exceeded', 500 : 'Internal Server Error', 502 : 'Bad Gateway', 503 : 'Service Unavailable', 504 : 'Gateway Timeout'}                
            for key in code.keys():
                if(response.status_code == key):
                    status = code.get(key)
            embed = discord.Embed(title= status, description='', color=0x62c1cc)
            embed.add_field(name='response.status_code', value=response.status_code, inline=False)

#경매
class LootAuction:
    def __init__(self, amount):
        self.amount = amount
    
    def loot(self):
        #골드 분배금 계산
        rAmount = self.amount * 0.95 #보증금을 제외한 실 수령
        auction = [rAmount*0.75,rAmount*0.6818 ,rAmount*0.875,rAmount*0.7954] #[4인균등 / 4인이득 / 8인균등 / 8인이득]

        #임베드
        embed = discord.Embed(title="%d골드 경매계산"%(self.amount), description="", color=0x62c1cc)
        embed.add_field(name='인원', value='4인\n8인', inline=True)
        embed.add_field(name='균등', value="%d \n %d"%(round(auction[0]), round(auction[2])), inline=True)
        embed.add_field(name='이득', value="%d \n %d"%(round(auction[1]), round(auction[3])), inline=True)

        return embed

#달력
class Calendar:
    def __init__(self):
        pass
    
    def adventure(self):
        url = 'https://developer-lostark.game.onstove.com/gamecontents/calendar'
        response = requests.get(url, headers=headers)
        now = datetime.datetime.now(kst)
        if(response.status_code == 200):
            contents = response.json() #list 타입
            res1 = {}
            res2 = {}
            str1=''
            str2 = ''
            for i in range(len(contents)):
                    for key in contents[i].keys():
                        if(contents[i].get(key) == '모험 섬'):
                            for j in range(len(contents[i]['RewardItems'])):
                                if(contents[i]['RewardItems'][j]['StartTimes'] == None):
                                    continue
                                else:
                                    if(now.weekday() == 5 or now.weekday() == 6):
                                        for k in range(len(contents[i]['RewardItems'][j]['StartTimes'])):
                                            if((contents[i]['RewardItems'][j]['StartTimes'][k])[:13] == str(now)[:10]+"T09"):
                                                if(contents[i]['RewardItems'][j].get('Name')== '영혼의 잎사귀' or contents[i]['RewardItems'][j].get('Name') == '인연의 돌'):
                                                    continue
                                                else:
                                                    res1[contents[i].get('ContentsName')] = contents[i]['RewardItems'][j].get('Name')
                                                    break
                                            elif((contents[i]['RewardItems'][j]['StartTimes'][k])[:13] == str(now)[:10]+"T19"):
                                                if(contents[i]['RewardItems'][j].get('Name')== '영혼의 잎사귀' or contents[i]['RewardItems'][j].get('Name') == '인연의 돌'):
                                                    continue
                                                else:
                                                    res2[contents[i].get('ContentsName')] = contents[i]['RewardItems'][j].get('Name')
                                                    break
                                            else:
                                                continue
                                    else:
                                        for k in range(len(contents[i]['RewardItems'][j]['StartTimes'])):
                                            if((contents[i]['RewardItems'][j]['StartTimes'][k])[:10] == str(now)[:10]):
                                                if(contents[i]['RewardItems'][j].get('Name')== '영혼의 잎사귀' or contents[i]['RewardItems'][j].get('Name') == '인연의 돌'):
                                                    continue
                                                else:
                                                    res1[contents[i].get('ContentsName')] = contents[i]['RewardItems'][j].get('Name')
                                                    break
                                            else:
                                                continue
                        else:
                            continue                
            
            for key, value in res1.items():
                if(value == '전설 ~ 고급 카드 팩'):
                    str1 += '`'+ key +'` : ' + '`카드`' + '\n'
                elif(value == '골드'):
                    str1 += '`'+ key +'` : ' + '`**'+ value +'`' + '\n'
                else:
                    str1 += '`'+ key +'` : ' + '`'+ value +'`' + '\n'

            for key, value in res2.items():
                if(value == '전설 ~ 고급 카드 팩'):
                    str2 += '`'+ key +'` : ' + '`카드`' + '\n'
                elif(value == '골드'):
                    str2 += '`'+ key +'` : ' + '`**'+ value +'`' + '\n'
                else:
                    str2 += '`'+ key +'` : ' + '`'+ value +'`' + '\n'
            
            #임베드 출력
            embed = discord.Embed(title= str(now)[:10] + ' 모험섬', description='', color=0x62c1cc)
            if(now.weekday() == 5 or now.weekday() == 6): #오늘이 주말일 경우
                embed.add_field(name='오전', value=str1, inline=False)
                embed.add_field(name='오후', value=str2, inline=True)
            else:
                embed.add_field(name='', value=str1, inline=True)

        else:
            code = {201 : 'Bad Request', 401 : 'Unauthorized', 403 : 'Forbidden', 404 : 'Not Found', 415 : 'Unsupported Media Type', 429 : 'Rate Limite Exceeded', 500 : 'Internal Server Error', 502 : 'Bad Gateway', 503 : 'Service Unavailable', 504 : 'Gateway Timeout'}                
            for key in code.keys():
                if(response.status_code == key):
                    status = code.get(key)
            embed = discord.Embed(title= status, description='', color=0x62c1cc)
            embed.add_field(name='response.status_code', value=response.status_code, inline=False)
        return embed
    
    def chaosGate(self):
        url = 'https://developer-lostark.game.onstove.com/gamecontents/calendar'
        response = requests.get(url, headers=headers)
        now = datetime.datetime.now(kst)
        if(response.status_code == 200):
            contents = response.json()
            indexInt = 0
            minLevel=0
            for i in range(len(contents)):
                for key in contents[i].keys():
                    if(contents[i].get(key) == '카오스게이트'):
                        if(contents[i]['MinItemLevel'] > minLevel):
                            minLevel = contents[i]['MinItemLevel']
                            indexInt = i
                        else:
                            continue
                    else:
                        continue
            chaosGate = contents[indexInt]['StartTimes']
            testStr=str(now)[:10] + 'T' + str(now)[11:16]+':00'
        else:
            code = {201 : 'Bad Request', 401 : 'Unauthorized', 403 : 'Forbidden', 404 : 'Not Found', 415 : 'Unsupported Media Type', 429 : 'Rate Limite Exceeded', 500 : 'Internal Server Error', 502 : 'Bad Gateway', 503 : 'Service Unavailable', 504 : 'Gateway Timeout'}                
            for key in code.keys():
                if(response.status_code == key):
                    status = code.get(key)
        return testStr


#아이템
class Item:
    def __init__(self) -> None:
        pass

    def legendaryMap(self):
        response = requests.get('https://developer-lostark.game.onstove.com/markets/options', headers=headers)
        now = datetime.datetime.now(kst)
        if(response.status_code == 200):
            itemName = ['태양의','명예의 파편 주머니(대)']
            multipleInt=[16,8,4,8]
            sum = 0
            indexInt = 0
            embed = discord.Embed(title= str(now)[:16] + ' 현재 전설지도', description='', color=0x62c1cc)
            for i in itemName:
                json_data = {
                                'Sort': 'GRADE',
                                'CategoryCode': 50000,
                                'CharacterClass': None,
                                'ItemTier': None,
                                'ItemGrade': None,
                                'ItemName': i,
                                'PageNo': 1,
                                'SortCondition': 'ASC',
                            }
                response = requests.post('https://developer-lostark.game.onstove.com/markets/items', headers=headers, json=json_data)
                contents = response.json()
                for j in contents['Items']:
                    embed.add_field(name='', value='`%s` : `%s`골드 (총 %s개)'%(j['Name'],str(j['CurrentMinPrice']),str(multipleInt[indexInt])) + '\n', inline=False)
                    sum += j['CurrentMinPrice'] * multipleInt[indexInt]
                    indexInt += 1
            response = requests.get('https://developer-lostark.game.onstove.com/auctions/options', headers=headers)
            classList = response.json()['Classes']
            jemPrice = []
            for i in classList:
                json_data2 = {
                                    'ItemLevelMin': 0,
                                    'ItemLevelMax': 0,
                                    'ItemGradeQuality': None,
                                    'SkillOptions': [
                                                        {
                                                            'FirstOption': None,
                                                            'SecondOption': None,
                                                            'MinValue': None,
                                                            'MaxValue': None,
                                                        },
                                                    ],
                                    'EtcOptions': [
                                                        {
                                                            'FirstOption': None,
                                                            'SecondOption': None,
                                                            'MinValue': None,
                                                            'MaxValue': None,
                                                        },
                                                    ],
                                    'Sort': 'BUY_PRICE',
                                    'CategoryCode': 210000,
                                    'CharacterClass': i,
                                    'ItemTier': 3,
                                    'ItemGrade': '고급',
                                    'ItemName': '1레벨',
                                    'PageNo': 1,
                                    'SortCondition': 'ASC',
                                }    
                response2 = requests.post('https://developer-lostark.game.onstove.com/auctions/items', headers=headers, json=json_data2)
                results = response2.json()['Items']
                for j in results:
                    if(len(jemPrice) == 0):
                        jemPrice.append(j['AuctionInfo']['StartPrice'])
                    """
                    else:
                        for k in range(len(jemPrice)):
                            if(jemPrice[k] >= j['AuctionInfo']['StartPrice']):
                                jemPrice.insert(k, j['AuctionInfo']['StartPrice'])
                        

                       
                            if(k >= response2.json()['Items'][j]['AuctionInfo']['StartPrice']):
                                jemPrice.append(response2.json()['Items'][j]['AuctionInfo']['StartPrice'])
                                jemPrice.insert(0, response2.json()['Items'][j]['AuctionInfo']['StartPrice'])
                            else:
                        """                           
            #sum += (jemPrice*48)
            embed.add_field(name='', value='`3티어 1레벨 보석` : `%s` (총 48개)'%(jemPrice) + '\n', inline=False)
            embed.add_field(name='골드', value='**`현재 가치` : `%s`골드\n**`손익분기` : `%s`골드'%(str(sum), str(round(sum*0.863636))), inline=False)
        else:
            code = {201 : 'Bad Request', 401 : 'Unauthorized', 403 : 'Forbidden', 404 : 'Not Found', 415 : 'Unsupported Media Type', 429 : 'Rate Limite Exceeded', 500 : 'Internal Server Error', 502 : 'Bad Gateway', 503 : 'Service Unavailable', 504 : 'Gateway Timeout'}                
            for key in code.keys():
                if(response.status_code == key):
                    status = code.get(key)
            embed = discord.Embed(title= status, description='', color=0x62c1cc)
            embed.add_field(name='response.status_code', value=response.status_code, inline=False)

        return jemPrice

#이벤트
class Event:
    def __init__(self):
        pass

    def eventList(self):
        response = requests.get('https://developer-lostark.game.onstove.com/news/events', headers=headers)
        if(response.status_code == 200):
            contents = response.json() #list 타입
            embed = discord.Embed(title = '진행중 이벤트', url = 'https://lostark.game.onstove.com/News/Event/Now', description='', color=0x62c1cc)
            for i in range(len(contents)):
                for key in contents[i]:
                    if(key == 'Title'):
                        if(contents[i].get('RewardDate')==None):
                            embed.add_field(name = contents[i].get('Title'), value = '~ ' + contents[i].get('EndDate')[:10] , inline=False)
                        else:
                            embed.add_field(name = contents[i].get('Title'), value = '~ ' + contents[i].get('RewardDate')[:10] , inline=False)
        else:
            code = {201 : 'Bad Request', 401 : 'Unauthorized', 403 : 'Forbidden', 404 : 'Not Found', 415 : 'Unsupported Media Type', 429 : 'Rate Limite Exceeded', 500 : 'Internal Server Error', 502 : 'Bad Gateway', 503 : 'Service Unavailable', 504 : 'Gateway Timeout'}                
            for key in code.keys():
                if(response.status_code == key):
                    status = code.get(key)
            embed = discord.Embed(title= status, description='', color=0x62c1cc)
            embed.add_field(name='response.status_code', value=response.status_code, inline=False)
        return embed
    
    def startEventList(self):
        response = requests.get('https://developer-lostark.game.onstove.com/news/events', headers=headers)
        if(response.status_code == 200):
            contents = response.json() #list 타입
            embed = discord.Embed(title = '시작하는 이벤트', url = 'https://lostark.game.onstove.com/News/Event/Now', description='', color=0x62c1cc)
            now = datetime.datetime.now()
            for i in range(len(contents)):
                for key in contents[i]:
                    if(key == 'Title'):
                        if(contents[i].get('StartDate')[:10]==str(now)[:10]):
                            if(contents[i].get('RewardDate')==None):
                                embed.add_field(name = contents[i].get('Title'), value = '~ ' + contents[i].get('EndDate')[:10], inline=False)
                            else:
                                embed.add_field(name = contents[i].get('Title'), value = '~ ' + contents[i].get('RewardDate')[:10] , inline=False)
        else:
            code = {201 : 'Bad Request', 401 : 'Unauthorized', 403 : 'Forbidden', 404 : 'Not Found', 415 : 'Unsupported Media Type', 429 : 'Rate Limite Exceeded', 500 : 'Internal Server Error', 502 : 'Bad Gateway', 503 : 'Service Unavailable', 504 : 'Gateway Timeout'}                
            for key in code.keys():
                if(response.status_code == key):
                    status = code.get(key)
            embed = discord.Embed(title= status, description='', color=0x62c1cc)
            embed.add_field(name='response.status_code', value=response.status_code, inline=False)
        return embed
    
    def endEventList(self):
        response = requests.get('https://developer-lostark.game.onstove.com/news/events', headers=headers)
        if(response.status_code == 200):
            contents = response.json() #list 타입
            embed = discord.Embed(title = '종료예정 이벤트', url = 'https://lostark.game.onstove.com/News/Event/Now', description='', color=0x62c1cc)
            now = datetime.datetime.now()
            plusDay = datetime.timedelta(days=1)
            tomorrow = now + plusDay
            for i in range(len(contents)):
                for key in contents[i]:
                    if(key == 'Title'):
                        if(contents[i].get('RewardDate')==None):
                            if(contents[i].get('EndDate')[:10]==str(tomorrow)[:10]):
                                embed.add_field(name = contents[i].get('Title'), value = '~ ' + contents[i].get('EndDate')[:10], inline=False)
                        else:
                            if(contents[i].get('RewardDate')[:10]==str(tomorrow)[:10]):
                                embed.add_field(name = contents[i].get('Title'), value = '~ ' + contents[i].get('RewardDate')[:10] , inline=False)
            embed.set_footer(text = "이벤트 종료 전에 미수령 보상을 모두 확인하시기 바랍니다.")
        else:
            code = {201 : 'Bad Request', 401 : 'Unauthorized', 403 : 'Forbidden', 404 : 'Not Found', 415 : 'Unsupported Media Type', 429 : 'Rate Limite Exceeded', 500 : 'Internal Server Error', 502 : 'Bad Gateway', 503 : 'Service Unavailable', 504 : 'Gateway Timeout'}                
            for key in code.keys():
                if(response.status_code == key):
                    status = code.get(key)
            embed = discord.Embed(title= status, description='', color=0x62c1cc)
            embed.add_field(name='response.status_code', value=response.status_code, inline=False)
        return embed

@bot.command()
async def 검색(ctx, nickname):
    sC=Character(nickname)
    await ctx.message.delete()
    await ctx.send(embed=sC.search(), delete_after=120)

@bot.command()
async def 경매(ctx, amount: int):
  if amount>0:
    la = LootAuction(amount)
    await ctx.message.delete()
    await ctx.send(embed=la.loot(), delete_after=20)
  else:
    await ctx.send("값이 올바르지않습니다.", delete_after=20)

@bot.command()
async def 도비스(ctx):
    ca = ChallengeAbyss().embed
    await ctx.message.delete()
    await ctx.send(embed=ca, delete_after=30)

@bot.command()
async def 도가토(ctx):
    cg = ChallengeGuardian().embed
    await ctx.message.delete()
    await ctx.send(embed=cg, delete_after=30)

@bot.command()
async def 모험섬(ctx):
  cal = Calendar()
  await ctx.message.delete()
  await ctx.send(embed=cal.adventure(), delete_after=60)

@bot.command()
async def 수집품(ctx, nickname):
    coll=Character(nickname)
    await ctx.message.delete()
    await ctx.send(embed=coll.collect())   

@bot.command()
async def 이벤트(ctx):
    event = Event()
    await ctx.message.delete()
    await ctx.send(embed=event.eventList(), delete_after=60)

@bot.command()
async def 주간(ctx):
    ca = ChallengeAbyss()
    cg = ChallengeGuardian()
    embed = discord.Embed(title= '주간 컨텐츠', description='', color=0x62c1cc)
    for i in range(0, len(cg.raid)):
        embed.add_field(name='', value=cg.raid[i]['Name']+' : '+cg.raid[i]['StartTime']+' ~ '+cg.raid[i]['EndTime'], inline=False)
    embed.set_image(url=ca.image)
    embed.add_field(name='', value='', inline=False)
    embed.add_field(name=ca.areaName, value=ca.startTime + ' ~ ' + ca.endTime + '\n 최소입장레벨 : ' + str(ca.minItemLevel), inline=False)
    await ctx.message.delete()
    await ctx.send(embed=embed, delete_after=30)

@bot.command()
async def 호출(ctx):
  await ctx.message.delete()
  await ctx.send("{}님이 채널주인을 호출하였습니다".format(ctx.author.mention), delete_after=300)
  host = await bot.fetch_user(191775623683899392)
  if host.dm_channel is None:
    channel = await host.create_dm()
    await channel.send("{}님이 호출하였습니다".format(ctx.author.mention))
  else:
     await host.dm_channel.send("{}님이 호출하였습니다".format(ctx.author.mention))

@bot.command()
async def 명령어(ctx):
    embed = discord.Embed(title="Command List", description="사용할 명령어 앞에 '/'를 붙여 사용해주세요.", color=0x62c1cc) # Embed의 기본 틀(색상, 메인 제목, 설명)을 잡아줍니다
    embed.add_field(name="검색", value="/검색 `닉네임` : 해당 캐릭터를 검색합니다.", inline=False)
    embed.add_field(name="경매", value="/경매 `가격` : 해당 가격에 대한 적정 입찰가를 계산해줍니다.", inline=False)
    embed.add_field(name="도비스", value="**이번주 도전 어비스 던전을 알려줍니다.", inline=False)
    embed.add_field(name="도가토", value="**이번주 도전 가디언 토벌을 알려줍니다.", inline=False)
    embed.add_field(name="모험섬", value="**오늘의 모험섬을 알려줍니다.", inline=False)
    embed.add_field(name="수집품", value="/수집품 `닉네임` : 해당 캐릭터의 수집형 포인트 정보를 알려줍니다", inline=False)
    embed.add_field(name="이벤트", value="**현재 진행중인 이벤트를 알려줍니다.", inline=False)
    embed.add_field(name="주간", value="**주간 컨텐츠 현황을 알려줍니다.", inline=False)
    embed.add_field(name="호출", value="**채널 주인을 호출합니다.", inline=False)
    await ctx.message.delete()
    await ctx.send(embed=embed, delete_after=300)

@bot.command()
async def 전설지도(ctx):
  map = Item()
  await ctx.message.delete()
  print(map.legendaryMap())
  #await ctx.send(embed=map.legendaryMap(), delete_after=60)

@bot.command()
async def 테스트(ctx):
  test = Calendar()
  await ctx.message.delete()
  print(test.chaosGate())
  print(datetime.datetime.now())
  #await ctx.send(embed=map.legendaryMap(), delete_after=60)  

bot.run(token) # 봇 실행부분
# -*- coding:utf-8 -*- 

import discord, asyncio
import labotenv #토큰값 저장 env파일
import requests
import json
import datetime
from discord.ext import commands

#디스코드 선언부
token = labotenv.discord_token
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
latoken = labotenv.lostArk_token

@bot.event
async def on_ready(): # 봇이 준비가 되면 1회 실행되는 부분
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('언제나 함께'))
    #dnd= '다른 용무 중', idle = '자리 비움'
    print("I'm Ready!")
    print(bot.user.name)

#LostArk API 공통 헤더
headers = {
    'accept': 'application/json',
    'authorization': latoken,
}

#캐릭터
class Character:
    def __init__(self, str):
        self.str = str
        
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
            if(response.status_code == 201):
                status = 'Bad Request'
            elif(response.status_code == 401):
                status = 'Unauthorized'  
            elif(response.status_code == 403):
                status = 'Forbidden'
            elif(response.status_code == 404):
                status = 'Not Found'
            elif(response.status_code == 415):
                status = 'Unsupported Media Type'
            elif(response.status_code == 429):
                status = 'Rate Limite Exceeded'
            elif(response.status_code == 500):
                status = 'Internal Server Error'
            elif(response.status_code == 502):
                status = 'Bad Gateway'
            elif(response.status_code == 503):
                status = 'Service Unavailable'
            elif(response.status_code == 504):
                status = 'Gateway Timeout'
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
        if(response.status_code == 201):
            status = 'Bad Request'
        elif(response.status_code == 401):
            status = 'Unauthorized'
        elif(response.status_code == 403):
            status = 'Forbidden'
        elif(response.status_code == 404):
            status = 'Not Found'
        elif(response.status_code == 415):
            status = 'Unsupported Media Type'
        elif(response.status_code == 429):
            status = 'Rate Limite Exceeded'
        elif(response.status_code == 500):
            status = 'Internal Server Error'
        elif(response.status_code == 502):
            status = 'Bad Gateway'
        elif(response.status_code == 503):
            status = 'Service Unavailable'
        elif(response.status_code == 504):
            status = 'Gateway Timeout'
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
        if(response.status_code == 201):
            status = 'Bad Request'
        elif(response.status_code == 401):
            status = 'Unauthorized'
        elif(response.status_code == 403):
            status = 'Forbidden'
        elif(response.status_code == 404):
            status = 'Not Found'
        elif(response.status_code == 415):
            status = 'Unsupported Media Type'
        elif(response.status_code == 429):
            status = 'Rate Limite Exceeded'
        elif(response.status_code == 500):
            status = 'Internal Server Error'
        elif(response.status_code == 502):
            status = 'Bad Gateway'
        elif(response.status_code == 503):
            status = 'Service Unavailable'
        elif(response.status_code == 504):
            status = 'Gateway Timeout'
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
                        embed.add_field(name = contents[i].get('Title'), value = '~ ' + contents[i].get('EndDate')[:10] , inline=False)
        else:
            if(response.status_code == 201):
                status = 'Bad Request'
            elif(response.status_code == 401):
                status = 'Unauthorized'
            elif(response.status_code == 403):
                status = 'Forbidden'
            elif(response.status_code == 404):
                status = 'Not Found'
            elif(response.status_code == 415):
                status = 'Unsupported Media Type'
            elif(response.status_code == 429):
                status = 'Rate Limite Exceeded'
            elif(response.status_code == 500):
                status = 'Internal Server Error'
            elif(response.status_code == 502):
                status = 'Bad Gateway'
            elif(response.status_code == 503):
                status = 'Service Unavailable'
            elif(response.status_code == 504):
                status = 'Gateway Timeout'
            embed = discord.Embed(title= status, description='', color=0x62c1cc)
            embed.add_field(name='response.status_code', value=response.status_code, inline=False)
        return embed
    """
    def startEventList(self):
        response = requests.get('https://developer-lostark.game.onstove.com/news/events', headers=headers)
        if(response.status_code == 200):
            contents = response.json() #list 타입
            embed = discord.Embed(title = '새로운 이벤트', url = 'https://lostark.game.onstove.com/News/Event/Now', description='', color=0x62c1cc)
            for i in range(len(contents)):
                for key in contents[i]:
                    if(key == 'Title'):
                        embed.add_field(name = contents[i].get('Title'), value = '~ ' + contents[i].get('EndDate')[:10] , inline=False)
        else:
            if(response.status_code == 201):
                status = 'Bad Request'
            elif(response.status_code == 401):
                status = 'Unauthorized'
            elif(response.status_code == 403):
                status = 'Forbidden'
            elif(response.status_code == 404):
                status = 'Not Found'
            elif(response.status_code == 415):
                status = 'Unsupported Media Type'
            elif(response.status_code == 429):
                status = 'Rate Limite Exceeded'
            elif(response.status_code == 500):
                status = 'Internal Server Error'
            elif(response.status_code == 502):
                status = 'Bad Gateway'
            elif(response.status_code == 503):
                status = 'Service Unavailable'
            elif(response.status_code == 504):
                status = 'Gateway Timeout'
            embed = discord.Embed(title= status, description='', color=0x62c1cc)
            embed.add_field(name='response.status_code', value=response.status_code, inline=False)
        return embed
    
    def endEventList(self):
        response = requests.get('https://developer-lostark.game.onstove.com/news/events', headers=headers)
        if(response.status_code == 200):
            contents = response.json() #list 타입
            embed = discord.Embed(title = '진행중 이벤트', url = 'https://lostark.game.onstove.com/News/Event/Now', description='', color=0x62c1cc)
            for i in range(len(contents)):
                for key in contents[i]:
                    if(key == 'Title'):
                        embed.add_field(name = contents[i].get('Title'), value = '~ ' + contents[i].get('EndDate')[:10] , inline=False)
        else:
            if(response.status_code == 201):
                status = 'Bad Request'
            elif(response.status_code == 401):
                status = 'Unauthorized'
            elif(response.status_code == 403):
                status = 'Forbidden'
            elif(response.status_code == 404):
                status = 'Not Found'
            elif(response.status_code == 415):
                status = 'Unsupported Media Type'
            elif(response.status_code == 429):
                status = 'Rate Limite Exceeded'
            elif(response.status_code == 500):
                status = 'Internal Server Error'
            elif(response.status_code == 502):
                status = 'Bad Gateway'
            elif(response.status_code == 503):
                status = 'Service Unavailable'
            elif(response.status_code == 504):
                status = 'Gateway Timeout'
            embed = discord.Embed(title= status, description='', color=0x62c1cc)
            embed.add_field(name='response.status_code', value=response.status_code, inline=False)
        return embed
    """

@bot.command()
async def 검색(ctx, nickname):
    sC=Character(nickname)
    #print(sC.search())
    await ctx.message.delete()
    await ctx.send(embed=sC.search(), delete_after=100)

@bot.command()
async def 경매(ctx, amount: int):
  if amount>0:
    la = LootAuction(amount)
    await ctx.message.delete()
    await ctx.send(embed=la.loot(), delete_after=20)
  else:
    await ctx.send("값이 올바르지않습니다.", delete_after=10)
    
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
    embed.add_field(name="이벤트", value="**현재 진행중인 이벤트를 알려줍니다.", inline=False)
    embed.add_field(name="주간", value="**주간 컨텐츠 현황을 알려줍니다.", inline=False)
    embed.add_field(name="호출", value="**채널 주인을 호출합니다.", inline=False)
    await ctx.message.delete()
    await ctx.send(embed=embed, delete_after=300)

bot.run(token) # 봇 실행부분
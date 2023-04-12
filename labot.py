# -*- coding:utf-8 -*- 
# 위에 구문은 # 빼버리시면 문제 생깁니다.
# 가끔가다 애가 인코딩을 잘못 읽어서 오류를 냅니다. 그것을 대비하기 위해 'utf-8'으로 읽으라고 선언합니다.

import discord, asyncio
import labotenv #토큰값 저장 env파일
import requests
import json
from discord.ext import commands

#디스코드 선언부
token = labotenv.discord_token
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
latoken = labotenv.lostArk_token
#client = discord.Client() # discord.Client() 같은 긴 단어 대신 client를 사용하겠다는 선언입니다.

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
        contents = response.json() #dict 타입
        dictPreset = contents['ArmoryProfile']

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
        
        className = dictPreset['CharacterClassName']
        itemLevel = dictPreset['ItemAvgLevel']
        charLevel = dictPreset['CharacterLevel']
        skillPoint = dictPreset['TotalSkillPoint']
        charInfo = '`직업` : %s\n`아이템 레벨` : %s\n`전투레벨` : %s\n`보유 스킬 포인트` : %s'%(className, itemLevel, charLevel, skillPoint)

        specPreset = dictPreset['Stats']
        specDict = {}
        for i in range(len(specPreset)):
            for key in specPreset[i]:
                if(key == 'Type'):
                   specDict[specPreset[i].get('Type')] = specPreset[i].get('Value')
        spec = '`공격력` : %s\n`최대 생명력` : %s\n'%(specDict.get('공격력'), specDict.get('최대 생명력'))
        combatSpec = '`치명` : %s\n`특화` : %s\n`신속` : %s\n`제압` : %s\n`인내` : %s\n`숙련` : %s'%(specDict.get('치명'), specDict.get('특화'), specDict.get('신속'), specDict.get('제압'), specDict.get('인내'), specDict.get('숙련'))
        
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

        embed = discord.Embed(title= self.str, description=miniInfo, color=0x62c1cc)
        embed.add_field(name='캐릭터 정보', value=charInfo + '\n\n' + spec, inline=True)
        embed.add_field(name='전투 특성', value=combatSpec, inline=True)
        embed.add_field(name='각인 효과', value=eng, inline=True)
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

@bot.command()
async def 검색(ctx, nickname):
    sC=Character(nickname)
    #print(sC.search())
    await ctx.message.delete()
    await ctx.send(embed=sC.search(), delete_after=100)
    
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

bot.run(token) # 봇 실행부분
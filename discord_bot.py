# bot.py
import os
import discord
import json
import re
import datetime
from math import sqrt, pow
from random import randint
from dotenv import load_dotenv
from discord.utils import get
from discord.ext import commands

#Bot url to share
#https://discord.com/api/oauth2/authorize?client_id=890766766291185694&permissions=85008&scope=bot



load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

guild = discord.Guild
role = discord.Role
bot = commands.Bot('?')




#steps
#1. look in dt channel for gm approval: Done
#2. Read the message and parse the data: Done
#3. execute the releveant downtime code: Done
#4. return the result: Done
#5. Execute command in trb_bot



@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')




@bot.command(name='man', aliases=['h'])
async def manual(ctx):
    #used to print all the channels in the server
    #print(ctx.guild.channels)

    # ******
    valid_channels = [852529119937429575, 899836717870231593]
    #channel = discord.utils.get(bot.get_all_channels(), name='🕛-archive-and-downtime')
    #channel = discord.utils.get(bot.get_all_channels(), name='dt')
    # ******


    if ctx.channel.id in valid_channels:
        description = "Downtime bot version 1\n\nCrafted items follow the naming scheme of 5e-tools and the TRB players guide\n https://5e.tools/items.html#abacus_phb\n\n https://homebrewery.naturalcrit.com/share/1ddAlA50cS8UnWxcCHNV-bSY_5b8xpKBb9ru_XJqnuq9Z\n\n ***The words in bold are what will trigger the bot to do an activity***"
        embed = discord.Embed(title="Downtime Bot Help", description=description)
        embed.add_field(name='Battle Training Example', value='Character: Realgar\nRelevant Ability & Modifier: +11 athletics\nDowntime Activity:  Battle **train**ing a camel\nDuration: 61 days ', inline=False)
        embed.add_field(name='Crafting Example', value='Character: Realgar\nRelevant Ability & Mod: +11 athletics\nDowntime Activity: **Craft**ing adamantium full plate\nDuration: 90 days\nProgress: 1400', inline=False)
        embed.add_field(name='Gathering/Foraging Example', value='Character:  Realgar\nRelevant Ability & Mod: herb kit +6\nDowntime Activity: **Gather**ing herbs for 10 potion of healing\nDuration: 62 days', inline=False)
        embed.add_field(name='Religious Service Example', value='Character: Realgar\nDowntime Activity: **Religious** Service \nDuration: 30 days\nRelevant Ability & Modifiers: +9 insight\nFaction: church of Mhim', inline=False)
        embed.add_field(name='Research Example', value='Character: Realgar\nDowntime Activity: **Research**ing a magic item  \nDuration: 30 days\nRelevant Ability & Modifiers: +9 insight', inline=False)
        embed.add_field(name='Teaching Trick Example', value='Character: Realgar\nRelevant Ability & Modifier: +7 animal handling\nDowntime Activity:  **Train**ing a giant ant to **(Activity)** Track\nDuration: 20 days ', inline=False)
        embed.add_field(name='Upgrading Example', value='Character:  Realgar\nRelevant Ability & Mod: +2 smith tools\nDowntime Activity: **Upgrad**e **(starting item)** +1 mace  **to**  **(desired item)** mace +2\nDuration:  10 days\nprogress: 3', inline=False)
        embed.add_field(name='Working Example', value='Character: Realgar\nLevel: 9\nCharisma Modifier: 0\nDowntime Activity: **Work**ing for the Woodcarvers guild\nDuration: 30 days\nRelevant Ability & Modifiers: Woodcarving tools +9\nFaction: Woodcarvers guild +2', inline=False)

        message = ctx.message
        await message.delete()
        await ctx.send(embed=embed, delete_after=120)
        #await ctx.send(embed=embed)

    return


@bot.event
async def on_raw_reaction_add(payload):
    days_used = None
    reaction_message_id = payload.message_id
    #reaction_user_id = payload.user_id
    reaction_user_roles = payload.member.roles
    #reaction_member = payload.member
    reaction_channel_id = payload.channel_id
    reaction_emoji = payload.emoji

    #******
    #print(reaction_emoji.name) #used to get the name of the emoji so we can save it laster.  This is manual!
    #******

    #******                 TRB                   My Server
    valid_channels = [852529119937429575, 899836717870231593]
    #channel = discord.utils.get(bot.get_all_channels(), name='🕛-archive-and-downtime')
    #channel = discord.utils.get(bot.get_all_channels(), name='dt')
    #******


    #if a post is reacted to in the downtime channel
    if reaction_channel_id in valid_channels:
        channel = bot.get_channel(reaction_channel_id)
        post = await channel.fetch_message(reaction_message_id)
        message_content = post.content
        message_author = post.author #used to message the writer of the post the result of their downtime activity
        # print(message_content)
        # print(message_author)



        #check to make sure no two gm's can approve the same post and have the downtime kick off more than once
        reaction = get(post.reactions, emoji=reaction_emoji.name)
        if reaction and reaction.count > 1:
            return

        #********
        #if the checkmark emoji is used
        if reaction_emoji.name == '✅':#change the checkmark to the one we use
        #********
            #if the person who reacted is a GM
            for role in reaction_user_roles:
                if role.name == 'GM' or role.name == 'TGM' or role.name == 'Moderator' or role.name == 'Casual TGM':
                    #create a dictionary of the downtime data
                    downtime_data = message_content.split('\n')
                    data = {}
                    for field in downtime_data:
                        #key is left of ':', value is right of ':'.  Strip removes leading and trailing whitespace
                        try:
                            data[field.split(':')[0].lower()] = field.split(':')[1].strip().lower()
                        except IndexError as e:
                            print(e)
                            description = "Your Request is incorrectly formatted. Please refer to the manual with '?h' or '?man'"
                            embed = discord.Embed(title="Formating Error", description=description)
                            await post.reply(message_author.mention, embed=embed)
                            return



                    craft_regex = re.compile(r'(craft[a-z]*)')
                    work_regex = re.compile(r'(work[a-z]*)')
                    train_regex = re.compile(r'(train[a-z]*)')
                    upgrade_regex = re.compile(r'(upgrad[a-z]*)')
                    forage_regex = re.compile(r'(forag[a-z]*)|(gath[a-z]*)')
                    relax_regex = re.compile(r'(relax[a-z]*)')
                    relgious_regex = re.compile(r'(relig[a-z]*)')
                    research_regex = re.compile(r'(research[a-z]*)')

                    # check if activity is crafting
                    if craft_regex.search(data.get('downtime activity').lower()):
                        try:
                            days_used = await crafting_calc(channel, message_author, post, data)
                            break


                        except KeyError as e:
                            print(e)
                            description = "Your Request is incorrectly formatted. Please use '?h' to show an example"
                            embed = discord.Embed(title="Formating Error", description=description)
                            await post.reply(message_author.mention, embed=embed)
                            return

                    # check if activity is working
                    elif work_regex.search(data.get('downtime activity').lower()):
                        days_used = await work_calc(channel, message_author, post, data)
                        break


                    # check if activity is upgrading
                    elif upgrade_regex.search(data.get('downtime activity').lower()):
                        days_used = await upgrade_calc(channel, message_author, post, data)
                        break


                    # check if activity is forage/gather ingredients
                    elif forage_regex.search(data.get('downtime activity').lower()):
                        days_used = await forage_calc(channel, message_author, post, data)
                        break

                    # check if activity is animal training
                    elif train_regex.search(data.get('downtime activity').lower()):
                        days_used = await animal_handling_calc(channel, message_author, post, data)
                        break

                    # check if activity is religious service
                    elif relgious_regex.search(data.get('downtime activity').lower()):
                        days_used = await religious_service_calc(channel, message_author, post, data)
                        break

                    # check if activity is research
                    elif relgious_regex.search(data.get('downtime activity').lower()):
                        days_used = await research_calc(channel, message_author, post, data)
                        break

                    else:
                        description = "Your Request is incorrectly formatted. Please use '?h' to show an example"
                        embed = discord.Embed(title="Formating Error", description=description)
                        await post.reply(message_author.mention, embed=embed)
                        return



    if not days_used:
        return
    #write the downtime command in the trb bot channel
    #******
    channel = discord.utils.get(bot.get_all_channels(), name='💻-trb-bot')
    #channel = discord.utils.get(bot.get_all_channels(), name='general')
    #******


    #await get_character_info(data)









async def get_character_info(data):
    # write the downtime command in the trb bot channel
    # ******
    channel = discord.utils.get(bot.get_all_channels(), name='💻-trb-bot')
    #channel = discord.utils.get(bot.get_all_channels(), name='general')
    # ******



    character = data.get('character').lower()

    await channel.send("\info " + str(character))


    # Save the current time before getting the characters info
    time_utc = datetime.datetime.utcnow()

    #simulate the trb bots response
    #description = "Please enter your relevant ability and modifiers" + "\n eg. relevant ability & mod: +2" + "\n Downtime has not been subtracted"
    #embed = discord.Embed(title="get info", description=description)
    #await channel.send(embed=embed)


    async for mess in channel.history(limit=3, after=time_utc):
        available_days = ''
        current_day = ''
        if mess.author != 'The Realm Beyond Bot#3757':
        #if str(mess.author) != 'trb_music_bot#0521':
            continue

        embeded_message = mess.embeds

        for contents in embeded_message:
            print(contents.to_dict())
            prof_regex = re.compile(r'(char[a-z]*)')
            # find a key with character in it
            for i in data.keys():
                if re.search(prof_regex, i.lower()) is not None:
                    if data[re.search(prof_regex, i.lower())] in contents.to_dict():
                        #get available days
                        available_days_string_regex = re.compile(r'((Downtime:)(\s+)([0-9]+)(\s+)(days))')
                        available_days_regex = re.compile(r'([0-9]+)')
                        #get current day in timeline
                        current_day_string_regex = re.compile(r'((Day:)(\s+)([0-9]+))')
                        current_day_regex = re.compile(r'([0-9]+)')




async def research_calc(channel, author, post, data):
    #######
    # save the days
    try:
        days = int(re.search(r"([0-9]+)", data['duration'].strip())[0])
    except TypeError:
        description = "Invalid duration value.  Please use numbers instead of the phonetic spelling.\n Downtime has not been subtracted"
        embed = discord.Embed(title="Formating Error", description=description)
        await post.reply(author.mention, embed=embed)
        return
    if 'week' in data['duration']:
        days = days * 7

    days_used = days
    #######

    #######
    # parse out the value for proficiency modifier.
    prof_mod = None
    # find the word "relev" and save everything after it
    prof_regex = re.compile(r'(relev[\w \W]*)')
    # find a key with ability modifier in it
    for i in data.keys():
        if re.search(prof_regex, i) is not None:
            prof_mod = int(re.search(r"([+-]?[0-9]+)", data[str(re.search(prof_regex, i)[0])].strip())[0])

    if prof_mod is None:
        description = "Please enter your relevant ability and modifiers" + "\n eg. relevant ability & mod: +2" + "\n Downtime has not been subtracted"
        embed = discord.Embed(title="Research Error", description=description)
        await post.reply(author.mention, embed=embed)
        return
    #######

    rolls = int(days / 7)
    units_earned = 0
    for i in range(rolls):
        roll = randint(1, 20) + prof_mod

        if roll >= 21:
            units_earned += 3
        elif roll >= 11:
            units_earned += 2
        elif roll >= 6:
            units_earned += 1



    # print out the results
    description = 'You have earned ' + str(units_earned) + ' research units.'
    embed = discord.Embed(title="Research log", description=description)
    await post.reply(author.mention + " Your downtime has been approved!", embed=embed)

    return days_used


async def religious_service_calc(channel, author, post, data):
    #######
    # save the days
    try:
        days = int(re.search(r"([0-9]+)", data['duration'].strip())[0])
    except TypeError:
        description = "Invalid duration value.  Please use numbers instead of the phonetic spelling.\n Downtime has not been subtracted"
        embed = discord.Embed(title="Formating Error", description=description)
        await post.reply(author.mention, embed=embed)
        return
    if 'week' in data['duration']:
        days = days * 7

    days_used = days
    #######

    #######
    # parse out the value for proficiency modifier.
    prof_mod = None
    # find the word "relev" and save everything after it
    prof_regex = re.compile(r'(relev[\w \W]*)')
    # find a key with ability modifier in it
    for i in data.keys():
        if re.search(prof_regex, i) is not None:
            prof_mod = int(re.search(r"([+-]?[0-9]+)", data[str(re.search(prof_regex, i)[0])].strip())[0])

    if prof_mod is None:
        description = "Please enter your relevant ability and modifiers" + "\n eg. relevant ability & mod: +2" + "\n Downtime has not been subtracted"
        embed = discord.Embed(title="Religious Service Error", description=description)
        await post.reply(author.mention, embed=embed)
        return
    #######

    rolls = int(days / 7)
    favors_earned = 0
    for i in range(rolls):
        roll = randint(1, 20) + prof_mod

        if roll >= 21:
            favors_earned += 2
        elif roll >= 11:
            favors_earned += 1



    # print out the results
    description = 'You have earned ' + str(favors_earned) + ' favors.'
    embed = discord.Embed(title="Religious Service log", description=description)
    await post.reply(author.mention + " Your downtime has been approved!", embed=embed)

    return days_used



async def work_calc(channel, author, post, data):
    log = []

    rep_dict = {1: 10, 2: 25, 3: 50, 4: 100, 5: 250, 6: 500, 7: 1000, 8: 2500, 9: 5000, 10: 10000}

    def check_reputation(roll, rep, dcmod, level, log, total):
        maxrep = 0
        if level > 12:
            maxrep = 10
        elif level > 8:
            maxrep = 8
        elif level > 4:
            maxrep = 6
        else:
            maxrep = 4

        dc = 16 + (rep * 2) - dcmod



        if rep >= maxrep:
            #sell a rep and try to earn it back
            previous_dc = 16 + (rep-1 * 2) - dcmod
            if roll >= previous_dc:
                log.append('\nConverting 1 rep to gp: +' +str(rep_dict[rep]) + 'gp')
                total += rep_dict[rep]
                log.append('Reputation increased back to maximum!(' + str(rep) + ' rep)')

            log.append('\nYou have maxed out your rep for this faction.\n  Subsequent weeks will attempt to convert 1 rep to gp while maintaining max rep')
            return rep, total


        if roll >= dc and rep < maxrep:
            log.append('Reputation increased to '+ str(rep+1) + '!')
            return rep + 1, total
        else:
            log.append('Reputation failed to increase')
            return rep, total


    #######
    #save the days
    try:
        days = int(re.search(r"([0-9]+)", data['duration'].strip())[0])
    except TypeError:
        description = "Invalid duration value.  Please use numbers instead of the phonetic spelling.\n Downtime has not been subtracted"
        embed = discord.Embed(title="Formating Error", description=description)
        await post.reply(author.mention, embed=embed)
        return

    if 'week' in data['duration']:
        days = days * 7

    days_used = days
    #######


    #######
    # parse out the value for proficiency modifier.
    prof_mod = None
    #find the word "relev" and save everything after it
    prof_regex = re.compile(r'(relev[\w \W]*)')
    # find a key with ability modifier in it
    for i in data.keys():
        if re.search(prof_regex, i) is not None:
            prof_mod = int(re.search(r"([+-]?[0-9]+)", data[str(re.search(prof_regex, i)[0])].strip())[0])

    if prof_mod is None:
        description = "Please enter your relevant ability and modifiers" + "\n eg. relevant ability & mod: +2" + "\n Downtime has not been subtracted"
        embed = discord.Embed(title="Work Error", description=description)
        await post.reply(author.mention, embed=embed)
        return
    #######

    #######
    #Save the level
    level = int(re.search(r"([0-9]+)", data['level'].strip())[0])
    #######


    #######
    #save the rep
    try:
        rep = int(re.search(r"([+-]?[0-9]+)", data['faction'].strip())[0])
    except KeyError:
        description = "Please enter a faction to work for so you don't miss out on rep!" + "\n eg. faction: city guards +3" + "\n Downtime has not been subtracted"
        embed = discord.Embed(title="Work Error", description=description)
        await post.reply(author.mention, embed=embed)
        return
    except:
        rep = 0
    #######


    #######
    #parse out the value for charisma modifier.
    #regex searches for "charis" + 0 or more letters and 0 or more spaces
    char_mod = None
    charisma_regex = re.compile(r'((charis[a-z ]*)|((cha[a-z ]*)(mod[ a-z]*)))')
    #find a key with char mod in it
    for i in data.keys():
        if re.search(charisma_regex, i) is not None:
            char_mod = int(data[str(re.search(charisma_regex, i)[0])])

    if char_mod is None:
        description = "Please enter your Charisma modifier so you don't miss out on rep!" + "\n eg. charisma modifier: +2" + "\n Downtime has not been subtracted"
        embed = discord.Embed(title="Work Error", description=description)
        await post.reply(author.mention, embed=embed)
        return
    #######




    total = 0
    repaccum = 0
    for day in range(1, days+1):
        roll = randint(1, 20) + prof_mod
        repaccum += roll
        workmod = 0
        if level > 10:
            workmod = 4
        elif level > 4:
            workmod = 2

        if data.get('show rolls') == 'true':
            log.append('Rolled a ' + str(roll))
        cash = 0.0
        if roll > 20 + workmod:
            cash += level * 2

        elif roll > 15 + workmod:
            cash += level

        elif roll > 10 + workmod:
            cash += level * .5

        else:
            cash += level * .2

        total += cash

        if day % 7 == 0:
            rep, total = check_reputation(roll, rep, char_mod, level, log, total)
            repaccum = 0


    log.append('\nTotal earned: ' + str(round(total, 1)) + 'gp')
    log.append('Final reputation: ' + str(rep))


    #if for some reason the results is to long, break it up and print it out
    description = ''
    for i in log:
        description = description + '\n' + i
        if len(description) >= 3900:
            embed = discord.Embed(title="Work Results", description=description)
            await post.reply(author.mention, embed=embed)
            description = ''

    #print out the results
    embed = discord.Embed(title="Working log", description=description)
    await post.reply(author.mention + " Your downtime has been approved!", embed=embed)

    return days_used



async def forage_calc(channel, author, post, data):
    log = []

    # load all craftable items
    with open('items.txt') as jsonfile:
        item_list = json.load(jsonfile)

    consumable_dc = {'common': ('14', 50), 'uncommon': ('18', 250), 'rare': ('22', 2500), 'very rare': ('26', 25000), 'legendary': ('30', 125000)}

    #######
    # get the starting progress.  If none set it to 0
    if data.get('progress') is None:
        progress = 0.0
    else:
        progress = float(data['progress'])
    #######

    #######
    # parse out the number of days to use.  checks for 1 or more numbers ignoring everything else
    days = int(re.search(r"([0-9]+)", data['duration'])[0])
    if 'week' in data['duration']:
        days = days * 7
    remaining_days = days
    #######

    #######
    # parse out the value for proficiency modifier.
    prof_mod = None
    # regex searches for "relev" + 0 or more letters followed by a space followed by "abili" + 0 or more letters followed by a space followed by "&" followed by a space followed by "mod" + 0 or more letters.  THEN OR'd with
    # "relev" + 0 or more letters followed by a space followed by "abili" + 0 or more letters followed by a space followed by "and" followed by a space followed by "mod" + 0 or more letters
    prof_regex = re.compile(r'((relev[a-z]*)(\s+)(abil[a-z]*)(\s+)(&)(\s+)(mod[a-z]*))|((relev[a-z]*)(\s+)(abil[a-z]*)(\s+)(and)(\s+)(mod[a-z]*))')
    # find a key with ability modifier in it
    for i in data.keys():
        if re.search(prof_regex, i) is not None:
            prof_mod = int(re.search(r"([+-]?[0-9]+)", data[str(re.search(prof_regex, i)[0])].strip())[0])

    if prof_mod is None:
        description = "Please enter your relevant ability and modifiers" + "\n eg. relevant ability & mod: +2" + "\n Downtime has not been subtracted"
        embed = discord.Embed(title="Work Error", description=description)
        await post.reply(author.mention, embed=embed)
        return
    #######

    #######
    # get the potion the ingredients are being foraged for
    item_regex = re.compile(r'(forag[a-z]*)|(gath[a-z]*)')
    raw_item_string = data['downtime activity'].split(re.search(item_regex, data['downtime activity'])[0])[1].strip()

    item = re.findall(r"([a-z ']+)", raw_item_string)

    quantity_regex = re.compile(r'(([^\+-])[0-9]+)')
    try:
        quantity = int(re.search(quantity_regex, data['downtime activity'])[0])
    except:
        quantity = 1
    #######


    ##########################
    #find the dc of the potion being foraged for.
    #check to see if the potion in downtime activity exists in 5e tools item list and grab the rarity
    found = False
    for item_reference in item_list.keys():
        for count in range(len(item)):
            if item_reference.lower() in item[count].strip().lower():

                found = True

                dc = consumable_dc[item_list[item_reference]][0]
                final_value = round(consumable_dc[item_list[item_reference]][1]/2, 1)

                if int(dc) > int(prof_mod) + 20:
                    embed = discord.Embed(title="Gathering Error!", description='You have no chance of succeeding at gathering the ingredients.\nThe DC you need to beat is ' + str(dc) + ' and the highest you can roll is ' + str(prof_mod + 20) + '.\nDowntime has not been used.')
                    await post.reply(author.mention, embed=embed)
                    return

    if not found:
        description = "I cannot determine the item you are foraging for.  Please make sure the name is spelled as it appears in 5e tools.  \n Downtime has not been subtracted"
        embed = discord.Embed(title="Gathering Error", description=description)
        await post.reply(author.mention, embed=embed)
        return
    ###########################

    ########################
    #code for calculating progress of foraging
    count = 1
    initial_quantity = quantity
    while quantity > 0 and remaining_days > 0:
        log.append("Gathering " + str(count) + "/" + str(initial_quantity))
        value_gathered = 0
        while final_value > progress and remaining_days > 0:
            roll = randint(1, 20) + prof_mod
            if roll >= int(dc):
                progress += (roll - int(dc)) + round(sqrt(final_value), 2)
            remaining_days -= 1

            if data.get('show rolls') == 'true':
                log.append('rolled a ' + str(roll))
                log.append('Progress... ' + str(progress))
                log.append('Days left: ' + str(remaining_days))

        # if craft completed reset the progress and continue
        if round(progress, 1) > round(final_value, 1):
            log.append("Successfully gathered enough ingredients for " + str(count) + "/" + str(initial_quantity) + ' potions')
            value_gathered += final_value
            #for gathering ingredients for multiple items, start with the remainder after the first success
            progress = progress - round(final_value, 1)
            quantity -= 1
            count += 1
        else:
            if remaining_days == 0:
                log.append('Not enough days to gather the all the required ingredients')
            value_gathered = round(progress, 1)

    log.append('_' * 50)

    log.append('Value of ingredients gathered ' + str(value_gathered) + "/" + str(final_value))
    log.append('Days of Downtime expended: ' + str(days - remaining_days))
    #############################

    #############################################################################
    #log the output
    # if for some reason the results is to long, break it up and print it out
    description = ''
    for i in log:
        description = description + '\n' + i
        if len(description) >= 3900:
            embed = discord.Embed(title="Crafting log", description=description)
            await post.reply(author.mention, embed=embed)
            description = ''

    # print out the results
    embed = discord.Embed(title="Crafting log", description=description)
    await post.reply(author.mention + " Your downtime has been approved!", embed=embed)
    ####################################################################################

    return str(days - remaining_days)
    ##############################



async def crafting_calc(channel, author, post, data):

    log = []

    # load all craftable items
    with open('items.txt') as jsonfile:
        item_list = json.load(jsonfile)

    # the progress function
    def craft(dc, progress, final_value, remaining_dtd, quantity, potion=False):

        if potion:
            count = 0
            successfull_potions = 0
            failed_potions = 0
            while quantity > 0:
                potion_roll = randint(1, 20) + prof_mod

                if potion_roll + prof_mod >= int(dc):
                    successfull_potions += 1

                elif potion_roll + prof_mod < int(dc):
                    failed_potions += 1

                count += 1
                quantity -= 1
            log.append('Potions successfully created: ' + str(successfull_potions))
            log.append('Random potions created: ' + str(failed_potions))
            log.append('Days of Downtime expended: ' + str(count))
            log.append('Ingredient cost to pay: ' + str((round(final_value / 2, 1)/2)*count))

            return str(count)


        else:
            count = 1
            initial_quantity = quantity
            while quantity > 0 and remaining_dtd > 0:
                log.append("Crafting " + str(count) + "/" + str(initial_quantity))
                while final_value > progress and remaining_dtd > 0:
                    roll = randint(1, 20) + prof_mod
                    if roll >= int(dc):
                        progress += (roll - int(dc)) + round(sqrt(final_value), 2)
                    remaining_dtd -= 1

                    if data.get('show rolls') == 'true':
                        log.append('rolled a ' + str(roll))
                        log.append('Progress... ' + str(progress))
                        log.append('Days left: ' + str(remaining_dtd))

                #if craft completed reset the progress and continue
                if round(progress, 1) > round(final_value, 1):
                    log.append("Successfully crafted " + str(count) + "/" + str(initial_quantity))
                    progress = 0
                    quantity -= 1
                    count += 1

            log.append('_' * 50)


            #if not all items were crafted show the current progress of the item being worked on
            if count < initial_quantity:
                #if the craft is complete, display final_value/final_value because players complain like bitches
                if round(progress, 1) > round(final_value, 1):
                    log.append('Current Progress: ' + str(round(final_value, 1)) + ' / ' + str(round(final_value, 1)))
            #show current progress
                else:
                    if remaining_dtd == 0:
                        log.append('Not enough days to finish item')
                    log.append('Current Progress: ' + str(round(progress, 1)) + ' / ' + str(round(final_value, 1)))

            else:
                if count > initial_quantity:
                    log.append('Current Progress: ' + str(round(final_value, 1)) + ' / ' + str(round(final_value, 1)))
                else:
                    log.append('Current Progress: ' + str(round(progress, 1)) + ' / ' + str(round(final_value, 1)))

            log.append('Days of Downtime expended: ' + str(days - remaining_dtd))
            log.append('Material cost to pay: ' + str(round(final_value / 2, 1)))
            return str(days - remaining_dtd)






    #key=rarity
    #value= tuple(dc, final_value)
    schematic_dc = {'common': ('14', 100), 'uncommon': ('18', 500), 'rare': ('22', 5000), 'very rare': ('26', 50000), 'legendary': ('30', 250000)}
    consumable_dc = {'common': ('14', 50), 'uncommon': ('18', 250), 'rare': ('22', 2500), 'very rare': ('26', 25000), 'legendary': ('30', 125000)}
    scroll_dc = {'level 0': ('3', 25), 'level 1': ('5', 50), 'level 2': ('8', 125), 'level 3': ('12', 250), 'level 4': ('15', 1000), 'level 5': ('19', 2500), 'level 6': ('22', 10000), 'level 7': ('26', 25000), 'level 8': ('29', 50000), 'level 9': ('33', 125000)}
    socket_dc = {0: '9', 1: '14', 2: '18', 3: '22', 4: '26', 5: '30'}
    weapon_info = {'club': '0.10', 'dagger': '2.00', 'greatclub':'0.20', 'handaxe': '5.00', 'javelin': '0.50', 'light hammer': '2.00', 'mace': '5.00', 'quarterstaff': '1.00', 'sickle': '1.00', 'spear': '1.00',
                   'light crossbow': '25.00', 'dart': '0.05', 'shortbow': '25.00', 'sling': '0.10', 'blowgun': '10.00', 'hand crossbow': '75.00', 'heavy crossbow': '50.00', 'longbow': '50.00', 'net': '1.00', 'arrows': '1.00', 'pistol': '150.00', 'pepperbox': '250.00', 'hand mortar': '500.00',
                   'musket': '100.00', 'bad news': '800.00', 'palm pistol': '50.00', 'blunderbuss': '300.00', 'battleaxe': '10.00', 'flail': '10.00', 'glaive': '20.00', 'greataxe': '30.00', 'greatsword': '30.00', 'halberd': '20.00', 'lance': '10.00', 'longsword': '15.00', 'maul': '20.00',
                   'morningstar': '15.00', 'pike': '5.00', 'rapier': '25.00', 'scimitar': '25.00', 'double scimitar': '50.00', 'shortsword': '10.00', 'trident': '5.00', 'war pick': '5.00', 'warhammer': '15.00', 'whip': '2.00'
                   }
    armor_info = {'padded': '5.00', 'leather': '10.00', 'studded leather': '45.00', 'hide': '10.00', 'chain shirt': '50.00', 'scale mail': '50.00', 'breastplate': '150.00', 'half plate': '750.00', 'ring mail': '30', 'chain mail': '75', 'splint': '200', 'full plate': '1500', 'shield': '10'}

    #######
    #get the starting progress.  If none set it to 0
    if data.get('progress') is None:
        progress = 0.0
    else:
        progress = float(data['progress'])
    #######


    #######
    # parse out the number of days to use.  checks for 1 or more numbers ignoring everything else
    days = int(re.search(r"([0-9]+)", data['duration'])[0])
    if 'week' in data['duration']:
        days = days * 7
    remaining_days = days
    #######

    #######
    # parse out the value for proficiency modifier.
    prof_mod = None
    # regex searches for "relev" + 0 or more letters followed by a space followed by "abili" + 0 or more letters followed by a space followed by "&" followed by a space followed by "mod" + 0 or more letters.  THEN OR'd with
    # "relev" + 0 or more letters followed by a space followed by "abili" + 0 or more letters followed by a space followed by "and" followed by a space followed by "mod" + 0 or more letters
    prof_regex = re.compile(r'((relev[a-z]*)(\s+)(abil[a-z]*)(\s+)(&)(\s+)(mod[a-z]*))|((relev[a-z]*)(\s+)(abil[a-z]*)(\s+)(and)(\s+)(mod[a-z]*))')
    # find a key with ability modifier in it
    for i in data.keys():
        if re.search(prof_regex, i) is not None:
            prof_mod = int(re.search(r"([+-]?[0-9]+)", data[str(re.search(prof_regex, i)[0])].strip())[0])

    if prof_mod is None:
        description = "Please enter your relevant ability and modifiers" + "\n eg. relevant ability & mod: +2" + "\n Downtime has not been subtracted"
        embed = discord.Embed(title="Work Error", description=description)
        await post.reply(author.mention, embed=embed)
        return
    #######

    #######
    #get the raw item
    item_regex = re.compile(r'(craft[a-z]*)')
    raw_item_string = data['downtime activity'].split(re.search(item_regex, data['downtime activity'])[0])[1].strip()
    #######



    #######
    #get the level of the item (used for scrolls)
    spell_scroll_regex = re.compile(r'((spell)(\s*)(scroll))')
    spell_scroll_level_regex = re.compile(r'((lev[a-z]+)(\s+)([0-9]*))|((lvl)(\s+)([0-9]*))')
    try:
        level = re.search(spell_scroll_level_regex, raw_item_string)[0].strip()
        raw_item_string = raw_item_string.replace(level, '')
        for i in scroll_dc.keys():
            num = str(re.search(r'[0-9]+', level)[0])
            if num in i:
                level = i
    except:
        pass
    #######


    #######
    #get the item and quantity being crafted
    item = re.search(r"([a-z ']+)", raw_item_string)[0].strip()
    quantity_regex = re.compile(r'([0-9]+)')
    try:
        quantity = int(re.search(quantity_regex, raw_item_string)[0])
    except:
        quantity = 1
    #######



    #if the item is a magic item or potion get the dc
    if item in item_list.keys():
        if 'potion' in item:
            if quantity > days:
                embed = discord.Embed(title="Crafting Error!", description="You did not provide enough days to craft " + str(quantity) + " " + item +"\nDowntime has not been used.")
                await post.reply(author.mention, embed=embed)
                return
            #use the potion dc's
            item_rarity = item_list[item]
            dc = consumable_dc[item_rarity][0]
            final_value = consumable_dc[item_rarity][1]
            # make sure the player can craft the item

            if int(dc) > int(prof_mod) + 20:
                embed = discord.Embed(title="Crafting Error!", description='You have no chance of succeeding at this craft.\nThe DC you need to beat is ' + str(dc) + ' and the highest you can roll is ' + str(prof_mod + 20) + '.\nDowntime has not been used.')
                await post.reply(author.mention, embed=embed)
                return


            days_used = craft(dc, progress, final_value, remaining_days, quantity, potion=True)



        else:
            #use schematic dc's
            item_rarity = item_list[item]
            dc = schematic_dc[item_rarity][0]
            final_value = schematic_dc[item_rarity][1]

            if data.get('consumable') == 'true':
                final_value = final_value/2

            if int(dc) > int(prof_mod) + 20:
                embed = discord.Embed(title="Crafting Error!", description='You have no chance of succeeding at this craft.\nThe DC you need to beat is ' + str(dc) + ' and the highest you can roll is ' + str(prof_mod + 20) + '.\nDowntime has not been used.')
                await post.reply(author.mention, embed=embed)
                return

            days_used = craft(dc, progress, final_value, remaining_days, quantity)


    #item is a scroll
    elif re.search(spell_scroll_regex, item) is not None:
        if re.search(spell_scroll_regex, item)[0].strip() in raw_item_string:
            #get the level and dc of the spell scroll
            try:
                dc = scroll_dc[level][0]
                final_value = scroll_dc[level][1]
            except:
                embed = discord.Embed(title="Crafting Error!", description='Unable to determine the level of spell scroll\nDowntime has not been used.')
                await post.reply(author.mention, embed=embed)
                return

            if int(dc) > int(prof_mod) + 20:
                embed = discord.Embed(title="Crafting Error!", description='You have no chance of succeeding at this craft.\nThe DC you need to beat is ' + str(dc) + ' and the highest you can roll is ' + str(prof_mod + 20) + '.\nDowntime has not been used.')
                await post.reply(author.mention, embed=embed)
                return

            days_used = craft(dc, progress, final_value, remaining_days, quantity)
        else:
            embed = discord.Embed(title="Crafting Error!", description='Unable to determine the scroll being crafted\nDowntime has not been used.')
            await post.reply(author.mention, embed=embed)
            return

    #item is weapon or armor
    else:
        #determine if item is socket or mundane
        try:
            sockets = re.search(r"([+]?[0-9]+)", raw_item_string)[0].strip()
        except:
            sockets = '0'

        #find the base item name to look up in the weapon/armor dictionary
        base_item = item.replace(sockets, '').strip()


        #if adamantium or mithral in the name, add 500 to the final value.  If both add 1000
        adamant_regex = re.compile(r'(adam[a-z]+)(\s+)')
        mithral_regex = re.compile(r'(mith[a-z]+)(\s+)')
        adamant = False
        mithral = False
        if adamant_regex.search(base_item):
            base_item = base_item.replace(adamant_regex.search(base_item)[0], '')
            adamant = True
        if mithral_regex.search(base_item):
            base_item = base_item.replace(mithral_regex.search(base_item)[0], '')
            mithral = True




        #item is weapon
        if weapon_info.get(base_item):

            base_value = float(weapon_info.get(base_item))
            if int(sockets) == 0:
                final_value = base_value
            else:
                final_value = ((base_value * (int(sockets)+1+1)) + sqrt(sqrt(base_value)) * pow(10, int(sockets)+1))

            if int(sockets) > 0:
                dc = socket_dc[int(sockets)+1] #socketed
            else:
                dc = socket_dc[int(sockets)] #mundane

            if int(dc) > int(prof_mod) + 20:
                embed = discord.Embed(title="Crafting Error!", description='You have no chance of succeeding at this craft.\nThe DC you need to beat is ' + str(dc) + ' and the highest you can roll is ' + str(prof_mod + 20) + '.\nDowntime has not been used.')
                await post.reply(author.mention, embed=embed)
                return

            days_used = craft(dc, progress, final_value, remaining_days, quantity)



        #item is armor
        elif armor_info.get(base_item):
            #calculate the final_value of a shield

            if base_item == 'shield':
                base_value = float(armor_info.get(base_item))
                if int(sockets) == 0:
                    final_value = base_value
                else:
                    final_value = float(((base_value * (int(sockets)+1+1)) + sqrt(sqrt(base_value)) * pow(10, int(sockets)+1)))

            #calculate the final value of armor
            else:
                base_value = float(armor_info.get(base_item))
                if int(sockets) == 0:
                    final_value = base_value
                else:
                    final_value = float(((base_value * (int(sockets)+2+1)) + sqrt(sqrt(base_value)) * pow(10, int(sockets)+2)))


            #if crafting adamant or mithral armor, add 500 to the final price.
            if adamant or mithral:
                final_value += 500



            if int(sockets) > 0:
                dc = socket_dc[int(sockets) + 2]  # socketed
            else:
                dc = socket_dc[int(sockets)]#mundane



            if int(dc) > int(prof_mod) + 20:
                embed = discord.Embed(title="Crafting Error!", description='You have no chance of succeeding at this craft.\nThe DC you need to beat is ' + str(dc) + ' and the highest you can roll is ' + str(prof_mod + 20) + '.\nDowntime has not been used.')
                await post.reply(author.mention, embed=embed)
                return

            days_used = craft(dc, progress, final_value, remaining_days, quantity)

        else:
            description = "I am having issues with '" + str(data['downtime activity'] + "'\n Downtime has not been subtracted")
            embed = discord.Embed(title="Crafting Error", description=description)
            await post.reply(author.mention, embed=embed)
            return False



    # if for some reason the results is to long, break it up and print it out
    description = ''
    for i in log:
        description = description + '\n' + i
        if len(description) >= 3900:
            embed = discord.Embed(title="Crafting log", description=description)
            await post.reply(author.mention, embed=embed)
            description = ''


    # print out the results
    embed = discord.Embed(title="Crafting log", description=description)
    await post.reply(author.mention + " Your downtime has been approved!", embed=embed)

    return days_used



async def upgrade_calc(channel, author, post, data):
    log = []

    # the progress function
    def upgrade(dc, progress, final_value, remaining_dtd):

        while remaining_dtd > 0:
            while final_value > progress and remaining_dtd > 0:
                roll = randint(1, 20) + prof_mod
                if roll >= int(dc):
                    progress += (roll - int(dc)) + round(sqrt(final_value), 2)
                remaining_dtd -= 1

                if data.get('show rolls') == 'true':
                    log.append('rolled a ' + str(roll))
                    log.append('Progress... ' + str(progress))
                    log.append('Days left: ' + str(remaining_dtd))



        log.append('_' * 50)

        # if the craft is complete, display final_value/final_value because players complain like bitches
        if round(progress, 1) > round(final_value, 1):
            log.append('Current Progress: ' + str(round(final_value, 1)) + ' / ' + str(round(final_value, 1)))
        # show current progress
        else:
            if remaining_dtd == 0:
                log.append('Not enough days to finish item')
            log.append('Current Progress: ' + str(round(progress, 1)) + ' / ' + str(round(final_value, 1)))


        log.append('Days of Downtime expended: ' + str(days - remaining_dtd))
        #subtract the cost of the initial item from the final value
        log.append('Material cost to pay: ' + str(round((final_value / 2)-original_item_progress, 1)))
        return str(days - remaining_dtd)



    socket_dc = {0: '9', 1: '14', 2: '18', 3: '22', 4: '26', 5: '30'}
    weapon_info = {'club': '0.10', 'dagger': '2.00', 'greatclub':'0.20', 'handaxe': '5.00', 'javelin': '0.50', 'light hammer': '2.00', 'mace': '5.00', 'quarterstaff': '1.00', 'sickle': '1.00', 'spear': '1.00',
                   'light crossbow': '25.00', 'dart': '0.05', 'shortbow': '25.00', 'sling': '0.10', 'blowgun': '10.00', 'hand crossbow': '75.00', 'heavy crossbow': '50.00', 'longbow': '50.00', 'net': '1.00', 'arrows': '1.00', 'pistol': '150.00', 'pepperbox': '250.00', 'hand mortar': '500.00',
                   'musket': '100.00', 'bad news': '800.00', 'palm pistol': '50.00', 'blunderbuss': '300.00', 'battleaxe': '10.00', 'flail': '10.00', 'glaive': '20.00', 'greataxe': '30.00', 'greatsword': '30.00', 'halberd': '20.00', 'lance': '10.00', 'longsword': '15.00', 'maul': '20.00',
                   'morningstar': '15.00', 'pike': '5.00', 'rapier': '25.00', 'scimitar': '25.00', 'double scimitar': '50.00', 'shortsword': '10.00', 'trident': '5.00', 'war pick': '5.00', 'warhammer': '15.00', 'whip': '2.00'
                   }
    armor_info = {'padded': '5.00', 'leather': '10.00', 'studded leather': '45.00', 'hide': '10.00', 'chain shirt': '50.00', 'scale mail': '50.00', 'breastplate': '150.00', 'half plate': '750.00', 'ring mail': '30', 'chain mail': '75', 'splint': '200', 'full plate': '1500', 'shield': '10'}



    #######
    #get the starting progress.  If none set it to 0
    if data.get('progress') is None:
        progress = 0.0
    else:
        progress = float(data['progress'])
    #######


    #######
    # parse out the number of days to use.  checks for 1 or more numbers ignoring everything else
    days = int(re.search(r"([0-9]+)", data['duration'])[0])
    if 'week' in data['duration']:
        days = days * 7
    remaining_days = days
    #######

    #######
    # parse out the value for proficiency modifier.
    prof_mod = None
    # regex searches for "relev" + 0 or more letters followed by a space followed by "abili" + 0 or more letters followed by a space followed by "&" followed by a space followed by "mod" + 0 or more letters.  THEN OR'd with
    # "relev" + 0 or more letters followed by a space followed by "abili" + 0 or more letters followed by a space followed by "and" followed by a space followed by "mod" + 0 or more letters
    prof_regex = re.compile(r'((relev[a-z]*)(\s+)(abil[a-z]*)(\s+)(&)(\s+)(mod[a-z]*))|((relev[a-z]*)(\s+)(abil[a-z]*)(\s+)(and)(\s+)(mod[a-z]*))')
    # find a key with ability modifier in it
    for i in data.keys():
        if re.search(prof_regex, i) is not None:
            prof_mod = int(re.search(r"([+-]?[0-9]+)", data[str(re.search(prof_regex, i)[0])].strip())[0])

    if prof_mod is None:
        description = "Please enter your relevant ability and modifiers" + "\n eg. relevant ability & mod: +2" + "\n Downtime has not been subtracted"
        embed = discord.Embed(title="Upgrade Error", description=description)
        await post.reply(author.mention, embed=embed)
        return
    #######

    #######
    #get the raw item
    item_regex = re.compile(r'(upgr[a-z]*)')
    raw_item_string = data['downtime activity'].split(re.search(item_regex, data['downtime activity'])[0])[1].strip()
    #######



    #######
    #get the item and quantity being crafted
    item = re.search(r"([a-z ']+)", raw_item_string)[0].strip()
    quantity_regex = re.compile(r'([0-9]+)')
    try:
        quantity = int(re.search(quantity_regex, raw_item_string)[0])
    except:
        quantity = 1
    #######


    original_item = raw_item_string.split('to')[0].strip()
    new_item = raw_item_string.split('to')[1].strip()


    if re.search(r'[a-z]+', new_item)[0] != re.search(r'[a-z]+', original_item)[0]:
        embed = discord.Embed(title="Upgrade Error!", description='The two items provided do not share the same base item. Please double check the spelling!\nDowntime has not been used.')
        await post.reply(author.mention, embed=embed)
        return

    try:
        original_item_sockets = re.search(r"([+]?[0-9]+)", original_item)[0].strip()
    except:
        original_item_sockets = '0'

    try:
        new_item_sockets = re.search(r"([+]?[0-9]+)", new_item)[0].strip()
    except:
        new_item_sockets = '0'


    base_item = original_item.replace(original_item_sockets, '').strip().lower()

    #if item is armor
    for i in armor_info.keys():
        if i in original_item and i in new_item:
            #get the progress of the original item and use that as the starting base
            if int(original_item_sockets) == 0:
                original_item_progress = float(armor_info[base_item])

            elif 'shield' == base_item:
                original_item_progress = float(((float(armor_info[base_item]) * (int(original_item_sockets)+1+1)) + sqrt(sqrt(float(armor_info[base_item]))) * pow(10, int(original_item_sockets)+1)))

            else:
                original_item_progress = float(((float(armor_info[base_item]) * (int(original_item_sockets) + 2 + 1)) + sqrt(sqrt(float(armor_info[base_item]))) * pow(10, int(original_item_sockets) + 2)))

            # if progress not provided or the progress is less than the base price of the original item, the starting progress is the base price of the original item
            if progress == 0 or progress < original_item_progress:
                progress = original_item_progress


            #get the final value which is the value of the new item
            if int(new_item_sockets) == 0:
                final_value = float(armor_info[base_item])

            elif 'shield' == base_item:
                final_value = float(((float(armor_info[base_item]) * (int(new_item_sockets)+1+1)) + sqrt(sqrt(float(armor_info[base_item]))) * pow(10, int(new_item_sockets)+1)))

            else:
                final_value = float(((float(armor_info[base_item]) * (int(new_item_sockets) + 2 + 1)) + sqrt(sqrt(float(armor_info[base_item]))) * pow(10, int(new_item_sockets) + 2)))

            if progress >= final_value:
                embed = discord.Embed(title="Upgrade Error", description='Your progress is greater than the value of the upgraded item impying that the item is already crafted.\nDowntime has not been subtracted')
                await post.reply(author.mention, embed=embed)
                return

            if int(new_item_sockets) > 0:
                dc = socket_dc[int(new_item_sockets) + 2]  # socketed
            else:
                dc = socket_dc[int(new_item_sockets)]#mundane

            if int(dc) > int(prof_mod) + 20:
                embed = discord.Embed(title="Upgrade Error!", description='You have no chance of succeeding at this craft.\nThe DC you need to beat is ' + str(dc) + ' and the highest you can roll is ' + str(prof_mod + 20) + '.\nDowntime has not been used.')
                await post.reply(author.mention, embed=embed)
                return


            days_used = upgrade(dc, progress, final_value, remaining_days)


    #if item is weapon
    for i in weapon_info.keys():
        if i in original_item and i in new_item:
            # get the progress of the original item and use that as the starting base
            if int(original_item_sockets) == 0:
                original_item_progress = float(weapon_info[base_item])
            else:
                original_item_progress = ((float(weapon_info[base_item]) * (int(original_item_sockets) + 1 + 1)) + sqrt(sqrt(float(weapon_info[base_item]))) * pow(10, int(original_item_sockets) + 1))

            # if progress not provided or the progress is less than the base price of the original item, the starting progress is the base price of the original item
            if progress == 0 or progress <original_item_progress:
                progress = original_item_progress

            # get the final value which is the value of the new item
            if int(new_item_sockets) == 0:
                final_value = int(weapon_info[base_item])
            else:
                final_value = ((float(weapon_info[base_item]) * (int(new_item_sockets) + 1 + 1)) + sqrt(sqrt(float(weapon_info[base_item]))) * pow(10, int(new_item_sockets) + 1))

            if int(new_item_sockets) > 0:
                dc = socket_dc[int(new_item_sockets) + 1]  # socketed
            else:
                dc = socket_dc[int(new_item_sockets)]  # mundane

            if int(dc) > int(prof_mod) + 20:
                embed = discord.Embed(title="Upgrade Error!", description='You have no chance of succeeding at this craft.\nThe DC you need to beat is ' + str(dc) + ' and the highest you can roll is ' + str(prof_mod + 20) + '.\nDowntime has not been used.')
                await post.reply(author.mention, embed=embed)
                return

            days_used = upgrade(dc, progress, final_value, remaining_days)



    # if for some reason the results is to long, break it up and print it out
    description = ''
    for i in log:
        description = description + '\n' + i
        if len(description) >= 3900:
            embed = discord.Embed(title="Upgrade log", description=description)
            await post.reply(author.mention, embed=embed)
            description = ''

    # print out the results
    embed = discord.Embed(title="Upgrade log", description=description)
    await post.reply(author.mention + " Your downtime has been approved!", embed=embed)

    return days_used


async def animal_handling_calc(channel, author, post, data):

    log = []

    #name: (exotic, no trained, battle trained, flying, huge, aggressive)
    animal_info = {'camel': (False, 50.00, 250.00, False, False, False),
                    'donkey': (False, 8.00, 40.00, False, False, False),
                    'mule': (False, 8.00, 40.00, False, False, False),
                    'elephant': (True, 200.00, 2000.00, False, True, False),
                    'horse draft': (False, 50.00, 250.00, False, False, False),
                    'draft horse': (False, 50.00, 250.00, False, False, False),
                    'horse riding': (False, 75.00, 375.00, False, False, False),
                    'riding horse': (False, 75.00, 375.00, False, False, False),
                    'mastiff': (False, 25.00, 125.00, False, False, False),
                    'pony': (False, 30.00, 150.00, False, False, False),
                    'warhorse': (False, None, 400.00, False, False, False),
                    'giant ant': (True, 500.00, 5000.00, False, False, True),
                    'axe beak': (True, 250.00, 2500.00, False, False, True),
                    'kalin': (True, 550.00, 5500.00, False, False, True),
                    'rhinoceros': (True, 500.00, 5000.00, False, False, False),
                    'riding lizard': (True, 300.00, 3000.00, False, False, False),
                    'steeder': (True, 600.00, 6000.00, False, False, True),
                    'thunderherder': (True, 800.00, 8000.00, False, True, True),
                    'triceratops': (True, 1000, 10000.00, False, True, False),
                    'worg': (True, 200.00, 2000.00, False, False, True)
    }

    #            'trick name': (common(dc, price), exotic(dc, price))
    trick_info = {'fetch': ((14, 100), (18, 500)),
                    'guard': ((14, 100), (18, 500)),
                    'track': ((14, 100), (18, 500)),
                    'attack': ((14, 100), (18, 500)),
                    'disengage': ((14, 100), (18, 500)),
                    'disengage(bonus action)': ((18, 500), (22, 5000)),
                    'multi-attack(2)': ((18, 500), (22, 5000)),
                    'hold': ((22, 5000), (26, 50000)),
                    'stablize': ((22, 5000), (26, 50000)),
                    'help': ((22, 5000), (26, 50000)),
                    'multi-attack(3)': ((22, 5000), (26, 50000))

    }

    # the progress function
    def craft(dc, progress, final_value, remaining_dtd):

        while remaining_dtd > 0 and final_value > progress:
            while final_value >= progress and remaining_dtd > 0:
                roll = randint(1, 20) + prof_mod
                if roll >= int(dc):
                    progress += (roll - int(dc)) + round(sqrt(final_value), 2)
                remaining_dtd -= 1

                if data.get('show rolls') == 'true':
                    log.append('rolled a ' + str(roll))
                    log.append('Progress... ' + str(progress))
                    log.append('Days left: ' + str(remaining_dtd))


        log.append('_' * 50)


        # if the craft is complete, display final_value/final_value because players complain like bitches
        if round(progress, 1) > round(final_value, 1):
            log.append('Current Progress: ' + str(round(final_value, 1)) + ' / ' + str(round(final_value, 1)))
        # show current progress
        else:
            if remaining_dtd == 0:
                log.append('Not enough days to finish training')
            log.append('Current Progress: ' + str(round(progress, 1)) + ' / ' + str(round(final_value, 1)))


        log.append('Days of Downtime expended: ' + str(days - remaining_dtd))
        log.append('Material cost to pay: ' + str(round(final_value / 2, 1)))
        return str(days - remaining_dtd)





    #######
    # get the starting progress.  If none set it to 0
    if data.get('progress') is None:
        progress = 0.0
    else:
        progress = float(data['progress'])
    #######

    #######
    # parse out the number of days to use.  checks for 1 or more numbers ignoring everything else
    days = int(re.search(r"([0-9]+)", data['duration'])[0])
    if 'week' in data['duration']:
        days = days * 7
    remaining_days = days
    #######

    #######
    # parse out the value for proficiency modifier.
    prof_mod = None
    # regex searches for "relev" + 0 or more letters followed by a space followed by "abili" + 0 or more letters followed by a space followed by "&" followed by a space followed by "mod" + 0 or more letters.  THEN OR'd with
    # "relev" + 0 or more letters followed by a space followed by "abili" + 0 or more letters followed by a space followed by "and" followed by a space followed by "mod" + 0 or more letters
    prof_regex = re.compile(r'((relev[a-z]*)(\s+)(abil[a-z]*)(\s+)(&)(\s+)(mod[a-z]*))|((relev[a-z]*)(\s+)(abil[a-z]*)(\s+)(and)(\s+)(mod[a-z]*))')
    # find a key with ability modifier in it
    for i in data.keys():
        if re.search(prof_regex, i) is not None:
            prof_mod = int(re.search(r"([+-]?[0-9]+)", data[str(re.search(prof_regex, i)[0])].strip())[0])

    if prof_mod is None:
        description = "Please enter your relevant ability and modifiers" + "\n eg. relevant ability & mod: +2" + "\n Downtime has not been subtracted"
        embed = discord.Embed(title="Training Error", description=description)
        await post.reply(author.mention, embed=embed)
        return
    #######

    #######
    # get the raw item
    item_regex = re.compile(r'(train[a-z]*)')
    raw_item_string = data['downtime activity'].split(re.search(item_regex, data['downtime activity'])[0])[1].strip()
    #######

    #######
    # get the item and quantity being crafted
    item = re.search(r"([a-z ']+)", raw_item_string)[0].strip()
    quantity_regex = re.compile(r'([0-9]+)')
    try:
        quantity = int(re.search(quantity_regex, raw_item_string)[0])
    except:
        quantity = 1
    #######



    for animal in animal_info:
        if animal.lower() in item.lower():
            item = animal.lower()

    learn_trick = False
    for the_trick in trick_info:
        if the_trick.lower() in raw_item_string.lower():
            learn_trick = True
            trick = the_trick.lower()


    #the animal is being taught a trick
    if learn_trick:

        #if animal is exotic
        if animal_info[item][0]:
            dc = trick_info[trick][1][0]
            final_value = trick_info[trick][1][1]

        else:
            dc = trick_info[trick][0][0]
            final_value = trick_info[trick][0][1]

        if int(dc) > int(prof_mod) + 20:
            embed = discord.Embed(title="Training Error!", description='You have no chance of succeeding at teaching your animal this trick.\nThe DC you need to beat is ' + str(dc) + ' and the highest you can roll is ' + str(prof_mod + 20) + '.\nDowntime has not been used.')
            await post.reply(author.mention, embed=embed)
            return

        days_used = craft(dc, progress, final_value, remaining_days)




    #the animal is being battle trained
    else:
        #get the battle trained price
        final_value = animal_info[item][2]

        #set the progress to the base price of the animal if progress is not provided or it is lower than the base price
        if progress < animal_info[item][1]:
            progress = animal_info[item][1]

        dc = 10
        #if exotic
        if animal_info[item][0]:
            dc += 5
        #if flying
        if animal_info[item][3]:
            dc += 5
        #if huge
        if animal_info[item][4]:
            dc += 5
        #if aggressive
        if animal_info[item][5]:
            dc += 5


        if int(dc) > int(prof_mod) + 20:
            embed = discord.Embed(title="Training Error!", description='You have no chance of succeeding at battle training your animal.\nThe DC you need to beat is ' + str(dc) + ' and the highest you can roll is ' + str(prof_mod + 20) + '.\nDowntime has not been used.')
            await post.reply(author.mention, embed=embed)
            return

        days_used = craft(dc, progress, final_value, remaining_days)



    # if for some reason the results is to long, break it up and print it out
    description = ''
    for i in log:
        description = description + '\n' + i
        if len(description) >= 3900:
            embed = discord.Embed(title="Animal Training Results", description=description)
            await post.reply(author.mention, embed=embed)
            description = ''

    # print out the results
    embed = discord.Embed(title="Animal Training log", description=description)
    await post.reply(author.mention + " Your downtime has been approved!", embed=embed)



    return days_used





bot.run(TOKEN)
import openai
import discord
import os
import re
import requests

client = discord.Client(intents=discord.Intents.all())
import os.path
openai.api_key = os.getenv("OPENAI_KEY")

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Streaming(
      name="🐒", url="https://www.twitch.tv/juuleeeeeee"
    ), status=discord.Status.online)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!help"):
        response = "Hi there! Here are the available commands:\n"
        response += "!image: Generates an image based on a prompt using OpenAI's ChatGPT model image-alpha-001.\n"
        response += "!chat: Answers prompts using OpenAI's ChatGPT.\n"
        response += "!code: Answers prompts using OpenAI's ChatGPT and puts the answer in a code box (for easy copy and pasting).\n"
        response += "!creative: Answers prompts using OpenAI's ChatGPT with more variety and creativity (look up ChatGPT temperature settings, it is set to 1 with this command and 0.5 for the other).\n"
        response += "!cc: Answers prompts using OpenAI's ChatGPT with both !creative and !code.\n"
        await message.channel.send(response)

    elif message.content.startswith("!image"):
        prompt = message.content[7:]
        loading_message = await message.channel.send("***Generating image, please wait...***")
        api_url = "https://api.openai.com/v1/images/generations"
        api_key = {"Authorization": f"Bearer {openai.api_key}"}
        data = {"model": "image-alpha-001", "prompt": prompt, "num_images": 1, "size": "1024x1024", "response_format": "url"}
        response = requests.post(api_url, headers=api_key, json=data).json()
        if 'error' in response:
            error_message = response['error']['message']
            await message.channel.send(f"An error occurred: {error_message}")
        else:
            image_url = response['data'][0]['url']
            response = requests.get(image_url)
            embed = discord.Embed()
            embed.set_image(url=image_url)
            await message.channel.send(embed=embed)
        await loading_message.delete()

    elif message.content.startswith("!chat"):
        prompt = message.content[6:]
        loading_message = await message.channel.send("***Generating response, please wait...***")
        response_lines = generate_response(prompt, 0.5)
        if isinstance(response_lines, str):
            await message.channel.send(response_lines)
        else:
            for line in response_lines:
                await message.channel.send(line)
        await loading_message.delete()

    elif message.content.startswith("!code"):
        prompt = message.content[6:]
        loading_message = await message.channel.send("***Generating response, please wait...***")
        response_lines = generate_response(prompt, 0.5)
        if isinstance(response_lines, str):
            await message.channel.send(response_lines)
        else:
            response = '\n'.join(response_lines)
            await message.channel.send('```' + response + '```')
        await loading_message.delete()

    elif message.content.startswith("!creative"):
        prompt = message.content[10:]
        loading_message = await message.channel.send("***Generating response, please wait...***")
        response_lines = generate_response(prompt, 1)
        if isinstance(response_lines, str):
            await message.channel.send(response_lines)
        else:
            for line in response_lines:
                await message.channel.send(line)
        await loading_message.delete()

    elif message.content.startswith("!cc"):
        prompt = message.content[4:]
        loading_message = await message.channel.send("***Generating response, please wait...***")
        response_lines = generate_response(prompt, 1)
        if isinstance(response_lines, str):
            await message.channel.send(response_lines)
        else:
            response = '\n'.join(response_lines)
            await message.channel.send('```' + response + '```')
        await loading_message.delete()

def generate_response(prompt, temperature):
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=4000, # 4000 is the maximum number of tokens for the davinci 003 GPT3 model
        n=1,
        stop=None,
        temperature=temperature,
    )

    if 'error' in completions:
        return completions['error']['message']
    else:
        message = completions.choices[0].text
    if '!code' in prompt:
        return message
    elif '!cc' in prompt:
        return message
    elif '!image' in prompt:
        return message
    else:
        words = re.split(r'\b', message)
        lines = []
        current_line = ''
        for word in words:
            if len(current_line + word) > 75:
                lines.append(current_line)
                current_line = ''
            current_line += word
        lines.append(current_line)
        return lines

client.run(os.getenv("DISCORD_BOT_TOKEN"))
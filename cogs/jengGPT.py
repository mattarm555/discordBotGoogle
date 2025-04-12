import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed
import requests

# Replace with your current localtunnel URL:
OLLAMA_URL = "https://smooth-books-brush.loca.lt"  

class JengGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="askjeng", description="Ask JengGPT a question.")
    @app_commands.describe(prompt="Your question or message")
    async def askjeng(self, interaction: Interaction, prompt: str):
        await interaction.response.defer(thinking=True)

        try:
            response = requests.post(f"{OLLAMA_URL}/api/generate", json={
                "model": "mistral",  # or llama2 if that's what you're running
                "prompt": prompt,
                "stream": False
            })
            data = response.json()
            answer = data.get("response", "🤖 No response from the model.")

            embed = Embed(
                title="🧠 JengGPT",
                description=answer.strip(),
                color=discord.Color.blurple()
            )
            embed.set_footer(text="powered by your local AI 😎")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(embed=Embed(
                title="❌ Error",
                description=f"Something went wrong:\n```\n{str(e)}\n```",
                color=discord.Color.red()
            ))

async def setup(bot):
    await bot.add_cog(JengGPT(bot))
